from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.digital.serializers import TransactionCreateSerializer, TransactionSerializer
from apps.digital.services.digital_service import DigitalService
from apps.digital.models import DigitalProduct


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def initiate_purchase(request):
    """
    Initiate a digital service purchase.
    """
    serializer = TransactionCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Get the product
            product_id = serializer.validated_data['product']
            product = get_object_or_404(DigitalProduct, id=product_id, is_active=True)
            
            # Get other validated data
            phone_number = serializer.validated_data['phone_number']
            quantity = serializer.validated_data.get('quantity', 1)
            priority = serializer.validated_data.get('priority', 'normal')
            
            # Create digital service instance
            digital_service = DigitalService()
            
            # Initiate the purchase
            transaction = digital_service.initiate_purchase(
                user=request.user,
                product_id=product_id,
                phone_number=phone_number,
                quantity=quantity,
                priority=priority
            )
            
            # Process the transaction (in a real app, this might be queued)
            result = digital_service.process_transaction(transaction.id)
            
            # Return the transaction details
            transaction_serializer = TransactionSerializer(transaction)
            return Response({
                'status': 'success',
                'message': result.get('message', 'Transaction processed successfully'),
                'data': transaction_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'status': 'error',
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_transaction_status(request, transaction_id):
    """
    Get the status of a specific transaction.
    """
    try:
        digital_service = DigitalService()
        status_data = digital_service.get_transaction_status(transaction_id)
        
        return Response({
            'status': 'success',
            'data': status_data
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def retry_transaction(request, transaction_id):
    """
    Retry a failed transaction.
    """
    try:
        digital_service = DigitalService()
        result = digital_service.retry_transaction(transaction_id)
        
        return Response({
            'status': 'success',
            'message': 'Transaction retry initiated successfully',
            'data': result
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_transactions(request):
    """
    List user's transactions.
    """
    try:
        # Get transactions for the authenticated user
        transactions = request.user.transaction_set.all().order_by('-created_at')
        
        # Apply filters if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            transactions = transactions.filter(status=status_filter)
        
        service_type_filter = request.query_params.get('service_type')
        if service_type_filter:
            transactions = transactions.filter(service_type__code=service_type_filter)
        
        # Paginate results
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        
        start = (int(page) - 1) * int(page_size)
        end = start + int(page_size)
        
        paginated_transactions = transactions[start:end]
        
        serializer = TransactionSerializer(paginated_transactions, many=True)
        
        return Response({
            'status': 'success',
            'data': serializer.data,
            'total': transactions.count(),
            'page': int(page),
            'page_size': int(page_size)
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)