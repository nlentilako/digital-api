from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from apps.users.models import User as CustomUser
from apps.digital.models import DigitalProduct, Transaction, APIKey
from apps.wallets.models import Wallet
from apps.digital.serializers import DigitalProductSerializer, TransactionSerializer
from apps.users.serializers import UserSerializer
from apps.wallets.serializers import WalletSerializer
from apps.digital.services.digital_service import DigitalService
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from decimal import Decimal
import uuid


# Authentication endpoints
@api_view(['POST'])
def register(request):
    """
    Register a new user account.
    """
    # Implementation will depend on your User model
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_number = request.data.get('phone_number')
    
    if not all([email, password, first_name, last_name, phone_number]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Missing required fields',
                'details': {
                    'required_fields': ['email', 'password', 'first_name', 'last_name', 'phone_number']
                }
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({
                'error': {
                    'code': 'DUPLICATE_ENTRY',
                    'message': 'User with this email already exists'
                }
            }, status=status.HTTP_409_CONFLICT)
        
        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Create wallet for the user
        Wallet.objects.get_or_create(user=user)
        
        return Response({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'role': user.user_type,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login(request):
    """
    Authenticate and receive JWT tokens.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email and password are required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.user_type
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': 'Invalid credentials'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def refresh_token(request):
    """
    Get a new access token using refresh token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Refresh token is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
        
        return Response({
            'access': new_access_token,
            'refresh': str(token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': 'Invalid refresh token'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    """
    Logout and blacklist the refresh token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Refresh token is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': 'Invalid refresh token'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


# User endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current user details.
    """
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    
    return Response({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'role': user.user_type,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
        'profile': {
            'avatar': user.avatar.url if user.avatar else None,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'address': user.address
        }
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile.
    """
    user = request.user
    
    # Update fields if provided
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    if 'phone_number' in request.data:
        user.phone_number = request.data['phone_number']
    if 'profile' in request.data:
        profile_data = request.data['profile']
        if 'date_of_birth' in profile_data:
            user.date_of_birth = profile_data['date_of_birth']
        if 'address' in profile_data:
            user.address = profile_data['address']
    
    user.save()
    
    return Response({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'role': user.user_type,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
        'profile': {
            'avatar': user.avatar.url if user.avatar else None,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'address': user.address
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    if not all([old_password, new_password, new_password_confirm]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'All password fields are required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password_confirm:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'New passwords do not match'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    if not user.check_password(old_password):
        return Response({
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': 'Current password is incorrect'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


# Products endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_products(request):
    """
    Get all available products with optional filters.
    """
    products = DigitalProduct.objects.filter(is_active=True)
    
    # Apply filters
    category = request.query_params.get('category')
    if category:
        products = products.filter(service_type__code__iexact=category)
    
    network = request.query_params.get('network')
    if network:
        products = products.filter(network_provider__code__iexact=network)
    
    is_active = request.query_params.get('is_active')
    if is_active is not None:
        products = products.filter(is_active=is_active.lower() == 'true')
    
    min_price = request.query_params.get('min_price')
    if min_price:
        try:
            min_price = Decimal(min_price)
            products = products.filter(denomination__gte=min_price)
        except:
            pass
    
    max_price = request.query_params.get('max_price')
    if max_price:
        try:
            max_price = Decimal(max_price)
            products = products.filter(denomination__lte=max_price)
        except:
            pass
    
    search = request.query_params.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    if page_size > 100:
        page_size = 100
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_products = products[start:end]
    
    serializer = DigitalProductSerializer(paginated_products, many=True)
    
    return Response({
        'count': products.count(),
        'next': f'/api/v1/products/?page={page + 1}&page_size={page_size}' if end < products.count() else None,
        'previous': f'/api/v1/products/?page={page - 1}&page_size={page_size}' if page > 1 else None,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_details(request, product_id):
    """
    Get product details by ID.
    """
    product = get_object_or_404(DigitalProduct, id=product_id, is_active=True)
    serializer = DigitalProductSerializer(product)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_data_bundles(request):
    """
    List data bundles with optional network filter.
    """
    products = DigitalProduct.objects.filter(
        service_type__code__iexact='data',
        is_active=True
    )
    
    network = request.query_params.get('network')
    if network:
        products = products.filter(network_provider__code__iexact=network)
    
    serializer = DigitalProductSerializer(products, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# Orders endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create a new order.
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    recipient_phone = request.data.get('recipient_phone')
    payment_method = request.data.get('payment_method', 'wallet')
    
    if not all([product_id, recipient_phone]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Product ID and recipient phone are required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if payment_method not in ['wallet', 'paystack', 'card']:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid payment method'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = DigitalProduct.objects.get(id=product_id, is_active=True)
    except DigitalProduct.DoesNotExist:
        return Response({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Product not found'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Use DigitalService to create transaction
        digital_service = DigitalService()
        transaction = digital_service.initiate_purchase(
            user=request.user,
            product_id=product_id,
            phone_number=recipient_phone,
            quantity=quantity
        )
        
        # Process the transaction
        result = digital_service.process_transaction(transaction.id)
        
        # Return order details
        return Response({
            'id': transaction.id,
            'order_number': transaction.reference,
            'product': {
                'id': str(product.id),
                'name': product.name
            },
            'quantity': quantity,
            'unit_price': float(transaction.price),
            'total_amount': float(transaction.amount),
            'status': transaction.status,
            'recipient_phone': recipient_phone,
            'payment_method': payment_method,
            'created_at': transaction.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bulk_order(request):
    """
    Create a bulk order (agents only).
    """
    # Check if user is an agent
    if request.user.user_type != 'agent':
        return Response({
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'Only agents can create bulk orders'
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    product_id = request.data.get('product_id')
    recipients = request.data.get('recipients', [])
    payment_method = request.data.get('payment_method', 'wallet')
    
    if not all([product_id, recipients]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Product ID and recipients are required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not isinstance(recipients, list) or len(recipients) == 0:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Recipients must be a non-empty list'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = DigitalProduct.objects.get(id=product_id, is_active=True)
    except DigitalProduct.DoesNotExist:
        return Response({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Product not found'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Process bulk order - for now, just return a success message
    # In a real implementation, you would process each recipient separately
    order_results = []
    
    for phone_number in recipients:
        try:
            digital_service = DigitalService()
            transaction = digital_service.initiate_purchase(
                user=request.user,
                product_id=product_id,
                phone_number=phone_number,
                quantity=1  # For bulk orders, each recipient gets 1 unit
            )
            
            result = digital_service.process_transaction(transaction.id)
            
            order_results.append({
                'recipient': phone_number,
                'transaction_id': transaction.id,
                'status': transaction.status,
                'message': result.get('message', 'Order processed successfully')
            })
        except Exception as e:
            order_results.append({
                'recipient': phone_number,
                'status': 'failed',
                'message': str(e)
            })
    
    return Response({
        'order_results': order_results,
        'summary': {
            'total_orders': len(recipients),
            'successful_orders': len([r for r in order_results if r['status'] != 'failed']),
            'failed_orders': len([r for r in order_results if r['status'] == 'failed'])
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """
    List user orders with optional filters.
    """
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters
    status_filter = request.query_params.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        from django.utils.dateparse import parse_date
        start_date = parse_date(start_date)
        if start_date:
            transactions = transactions.filter(created_at__date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        from django.utils.dateparse import parse_date
        end_date = parse_date(end_date)
        if end_date:
            transactions = transactions.filter(created_at__date__lte=end_date)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    if page_size > 100:
        page_size = 100
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_transactions = transactions[start:end]
    
    serializer = TransactionSerializer(paginated_transactions, many=True)
    
    return Response({
        'count': transactions.count(),
        'next': f'/api/v1/orders/?page={page + 1}&page_size={page_size}' if end < transactions.count() else None,
        'previous': f'/api/v1/orders/?page={page - 1}&page_size={page_size}' if page > 1 else None,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    """
    Get order details by ID.
    """
    transaction = get_object_or_404(Transaction, id=order_id, user=request.user)
    serializer = TransactionSerializer(transaction)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# Wallet endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet_balance(request):
    """
    Get user wallet balance.
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    return Response({
        'id': str(wallet.id),
        'balance': float(wallet.balance),
        'currency': 'GHS',  # Assuming Ghana Cedis
        'is_active': wallet.is_active,
        'created_at': wallet.created_at.isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fund_wallet(request):
    """
    Fund user wallet.
    """
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method', 'paystack')
    
    if not amount:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Amount is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Amount must be greater than 0'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid amount format'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real implementation, you would integrate with a payment provider
    # For now, just return a mock response
    reference = f"WALLET_FUND_{uuid.uuid4().hex[:12].upper()}"
    
    return Response({
        'reference': reference,
        'amount': float(amount),
        'payment_url': f'https://paystack.com/pay/{reference}',
        'status': 'pending'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_withdrawal(request):
    """
    Request wallet withdrawal.
    """
    amount = request.data.get('amount')
    bank_code = request.data.get('bank_code')
    account_number = request.data.get('account_number')
    account_name = request.data.get('account_name')
    
    if not all([amount, bank_code, account_number, account_name]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'All withdrawal fields are required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Amount must be greater than 0'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid amount format'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check wallet balance
    wallet = Wallet.objects.get(user=request.user)
    if wallet.balance < amount:
        return Response({
            'error': {
                'code': 'INSUFFICIENT_FUNDS',
                'message': 'Insufficient wallet balance'
            }
        }, status=status.HTTP_402_PAYMENT_REQUIRED)
    
    # In a real implementation, you would process the withdrawal
    # For now, just return a success message
    return Response({
        'message': 'Withdrawal request submitted successfully',
        'reference': f"WD-{uuid.uuid4().hex[:12].upper()}",
        'amount': float(amount),
        'status': 'pending'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_transaction_history(request):
    """
    Get wallet transaction history.
    """
    # This would require a WalletTransaction model which may not exist yet
    # For now, return an empty list
    return Response({
        'count': 0,
        'results': []
    }, status=status.HTTP_200_OK)


# Payments endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate payment.
    """
    amount = request.data.get('amount')
    email = request.data.get('email', request.user.email)
    order_id = request.data.get('order_id')
    callback_url = request.data.get('callback_url')
    
    if not amount:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Amount is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Amount must be greater than 0'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid amount format'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real implementation, you would integrate with a payment provider
    # For now, just return a mock response
    reference = f"PAY_{uuid.uuid4().hex[:12].upper()}"
    
    return Response({
        'reference': reference,
        'authorization_url': f'https://paystack.com/pay/{reference}',
        'access_code': 'access_code_here'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify payment.
    """
    reference = request.data.get('reference')
    
    if not reference:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Reference is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real implementation, you would verify with the payment provider
    # For now, just return a mock response
    return Response({
        'reference': reference,
        'status': 'success',
        'message': 'Payment verified successfully',
        'amount': 100.00
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def payment_webhook(request):
    """
    Payment webhook endpoint.
    """
    # This endpoint should be called by payment providers
    # In a real implementation, you would verify the webhook signature
    # and update transaction status accordingly
    return Response({'status': 'received'}, status=status.HTTP_200_OK)


# Agent endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_become_agent(request):
    """
    Apply to become an agent.
    """
    business_name = request.data.get('business_name')
    business_type = request.data.get('business_type')
    business_address = request.data.get('business_address')
    ghana_card_number = request.data.get('ghana_card_number')
    ghana_card_image = request.data.get('ghana_card_image')
    reason = request.data.get('reason')
    
    if not all([business_name, business_type, business_address, ghana_card_number, reason]):
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'All required fields must be provided'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real implementation, you would save this application
    # For now, just return a success message
    return Response({
        'message': 'Agent application submitted successfully',
        'application_id': str(uuid.uuid4()),
        'status': 'pending'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_application_status(request):
    """
    Get agent application status.
    """
    # In a real implementation, you would fetch the user's application
    # For now, return a mock response
    return Response({
        'id': str(uuid.uuid4()),
        'status': 'pending',
        'business_name': 'Sample Business',
        'applied_at': '2024-01-01T00:00:00Z',
        'reviewed_at': None,
        'reviewer_notes': None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_agents(request):
    """
    List agents (admin/employee only).
    """
    # Check if user has admin privileges
    if request.user.user_type not in ['admin', 'employee']:
        return Response({
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'Only admin and employee can list agents'
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    # In a real implementation, you would fetch agents from the database
    # For now, return an empty list
    return Response({
        'count': 0,
        'results': []
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_agent(request, agent_id):
    """
    Approve agent application (admin/employee only).
    """
    # Check if user has admin privileges
    if request.user.user_type not in ['admin', 'employee']:
        return Response({
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'Only admin and employee can approve agents'
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    # In a real implementation, you would approve the agent
    # For now, just return a success message
    return Response({
        'message': f'Agent {agent_id} approved successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_agent(request, agent_id):
    """
    Reject agent application (admin/employee only).
    """
    # Check if user has admin privileges
    if request.user.user_type not in ['admin', 'employee']:
        return Response({
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'Only admin and employee can reject agents'
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    reason = request.data.get('reason')
    
    # In a real implementation, you would reject the agent
    # For now, just return a success message
    return Response({
        'message': f'Agent {agent_id} rejected successfully',
        'reason': reason
    }, status=status.HTTP_200_OK)


# Transactions endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_transactions(request):
    """
    List transactions with optional filters.
    """
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters
    transaction_type = request.query_params.get('transaction_type')
    if transaction_type:
        # Map transaction type to service type
        transactions = transactions.filter(service_type__code__iexact=transaction_type)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    start_date = request.query_params.get('start_date')
    if start_date:
        from django.utils.dateparse import parse_date
        start_date = parse_date(start_date)
        if start_date:
            transactions = transactions.filter(created_at__date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        from django.utils.dateparse import parse_date
        end_date = parse_date(end_date)
        if end_date:
            transactions = transactions.filter(created_at__date__lte=end_date)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    if page_size > 100:
        page_size = 100
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_transactions = transactions[start:end]
    
    serializer = TransactionSerializer(paginated_transactions, many=True)
    
    return Response({
        'count': transactions.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction_details(request, transaction_id):
    """
    Get transaction details by ID.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    serializer = TransactionSerializer(transaction)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


# Placeholder functions for other endpoints that require additional models
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """
    List user notifications.
    """
    # This requires a Notification model which may not exist yet
    return Response({
        'count': 0,
        'unread_count': 0,
        'results': []
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark notification as read.
    """
    # This requires a Notification model which may not exist yet
    return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read.
    """
    # This requires a Notification model which may not exist yet
    return Response({'message': 'All notifications marked as read'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_chat_rooms(request):
    """
    List chat rooms.
    """
    # This requires a Chat model which may not exist yet
    return Response({'count': 0, 'results': []}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    """
    Create chat room.
    """
    # This requires a Chat model which may not exist yet
    return Response({'message': 'Chat room created'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_messages(request, room_id):
    """
    Get room messages.
    """
    # This requires a Chat model which may not exist yet
    return Response({'count': 0, 'results': []}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Send message.
    """
    # This requires a Chat model which may not exist yet
    return Response({'message': 'Message sent'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Dashboard overview based on user role.
    """
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    
    if user.user_type == 'admin':
        # Admin dashboard data
        return Response({
            'total_users': CustomUser.objects.count(),
            'total_agents': CustomUser.objects.filter(user_type='agent').count(),
            'total_revenue': '50000.00',
            'pending_agents': 5,
            'system_health': {'status': 'operational'}
        }, status=status.HTTP_200_OK)
    elif user.user_type == 'agent':
        # Agent dashboard data
        return Response({
            'wallet_balance': float(wallet.balance),
            'total_sales': '5000.00',
            'commission_earned': '250.00',
            'monthly_revenue': [],
            'top_products': []
        }, status=status.HTTP_200_OK)
    else:
        # Regular user dashboard data
        return Response({
            'wallet_balance': float(wallet.balance),
            'total_orders': Transaction.objects.filter(user=user).count(),
            'recent_transactions': [],
            'pending_orders': Transaction.objects.filter(user=user, status='pending').count()
        }, status=status.HTTP_200_OK)


# Developer API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_api_keys(request):
    """
    List API keys for the user.
    """
    api_keys = APIKey.objects.filter(user=request.user)
    
    keys_data = []
    for key in api_keys:
        keys_data.append({
            'id': str(key.id),
            'name': key.name,
            'key_prefix': key.key[:10] + '...' if len(key.key) > 10 else key.key,
            'is_active': key.is_active,
            'is_sandbox': key.is_sandbox,
            'environment': 'sandbox' if key.is_sandbox else 'live',
            'created_at': key.created_at.isoformat()
        })
    
    return Response(keys_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_api_key(request):
    """
    Create a new API key.
    """
    name = request.data.get('name')
    environment = request.data.get('environment', 'sandbox')
    permissions = request.data.get('permissions', [])
    allowed_ips = request.data.get('allowed_ips', [])
    
    if not name:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Name is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate API key
    import uuid
    api_key = f"dm_{'live' if environment == 'live' else 'test'}_{uuid.uuid4().hex[:24]}"
    
    # Create the API key in the database
    new_key = APIKey.objects.create(
        user=request.user,
        key=api_key,
        name=name,
        is_sandbox=(environment != 'live'),
        ip_whitelist=allowed_ips
    )
    
    return Response({
        'id': str(new_key.id),
        'name': new_key.name,
        'api_key': new_key.key,
        'key_prefix': new_key.key[:10] + '...',
        'environment': environment,
        'message': 'Store this API key securely. It will not be shown again.'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_api_key(request, key_id):
    """
    Regenerate an API key.
    """
    try:
        api_key = APIKey.objects.get(id=key_id, user=request.user)
        
        # Generate new API key
        import uuid
        new_key = f"dm_{'live' if not api_key.is_sandbox else 'test'}_{uuid.uuid4().hex[:24]}"
        api_key.key = new_key
        api_key.save()
        
        return Response({
            'id': str(api_key.id),
            'api_key': api_key.key,
            'message': 'API key regenerated successfully'
        }, status=status.HTTP_200_OK)
    except APIKey.DoesNotExist:
        return Response({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'API key not found'
            }
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_api_key(request, key_id):
    """
    Revoke an API key.
    """
    try:
        api_key = APIKey.objects.get(id=key_id, user=request.user)
        api_key.is_active = False
        api_key.save()
        
        return Response({
            'message': 'API key revoked successfully'
        }, status=status.HTTP_200_OK)
    except APIKey.DoesNotExist:
        return Response({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'API key not found'
            }
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_key_usage_statistics(request, key_id):
    """
    Get API key usage statistics.
    """
    # This would require usage tracking which may not be implemented yet
    # For now, return mock data
    return Response({
        'key_id': key_id,
        'requests_today': 150,
        'requests_this_month': 4500,
        'rate_limit': 1000,
        'last_used_at': '2024-01-01T00:00:00Z'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_webhooks(request):
    """
    List webhooks for the user.
    """
    # This requires a Webhook model which may not exist yet
    return Response({'count': 0, 'results': []}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_webhook(request):
    """
    Create a webhook.
    """
    # This requires a Webhook model which may not exist yet
    url = request.data.get('url')
    events = request.data.get('events', [])
    
    if not url:
        return Response({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'URL is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'id': str(uuid.uuid4()),
        'url': url,
        'events': events,
        'status': 'active'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_webhook_events(request):
    """
    List available webhook events.
    """
    events = [
        'order.completed',
        'order.failed',
        'payment.success',
        'payment.failed',
        'wallet.funded',
        'wallet.withdrawn'
    ]
    
    return Response(events, status=status.HTTP_200_OK)