from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from apps.digital.models import (
    ServiceType, NetworkProvider, DigitalProduct, 
    Transaction, UserPricing
)
from apps.digital.serializers import (
    ServiceTypeSerializer, NetworkProviderSerializer, 
    DigitalProductSerializer, UserPricingSerializer, TransactionSerializer
)


@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def manage_service_types(request):
    """
    Get or create service types (Data, Airtime, WAEC, etc.)
    """
    if request.method == 'GET':
        service_types = ServiceType.objects.all()
        serializer = ServiceTypeSerializer(service_types, many=True)
        return Response({'data': serializer.data})
    
    elif request.method == 'POST':
        serializer = ServiceTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def manage_network_providers(request):
    """
    Get or create network providers (MTN, Vodafone, AirtelTigo)
    """
    if request.method == 'GET':
        providers = NetworkProvider.objects.all()
        serializer = NetworkProviderSerializer(providers, many=True)
        return Response({'data': serializer.data})
    
    elif request.method == 'POST':
        serializer = NetworkProviderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def manage_digital_products(request):
    """
    Get or create digital products (data bundles, airtime denominations)
    """
    if request.method == 'GET':
        products = DigitalProduct.objects.select_related('service_type', 'network_provider').all()
        serializer = DigitalProductSerializer(products, many=True)
        return Response({'data': serializer.data})
    
    elif request.method == 'POST':
        serializer = DigitalProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET', 'PUT', 'DELETE'])
def manage_digital_product(request, product_id):
    """
    Get, update or delete a specific digital product
    """
    try:
        product = DigitalProduct.objects.get(id=product_id)
    except DigitalProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DigitalProductSerializer(product)
        return Response({'data': serializer.data})
    
    elif request.method == 'PUT':
        serializer = DigitalProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def toggle_service_availability(request, service_type_id):
    """
    Toggle the availability of a service type
    """
    try:
        service_type = ServiceType.objects.get(id=service_type_id)
    except ServiceType.DoesNotExist:
        return Response({'error': 'Service type not found'}, status=status.HTTP_404_NOT_FOUND)
    
    service_type.is_active = not service_type.is_active
    service_type.save()
    
    serializer = ServiceTypeSerializer(service_type)
    return Response({'data': serializer.data})


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def toggle_product_availability(request, product_id):
    """
    Toggle the availability of a digital product
    """
    try:
        product = DigitalProduct.objects.get(id=product_id)
    except DigitalProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    product.is_active = not product.is_active
    product.save()
    
    serializer = DigitalProductSerializer(product)
    return Response({'data': serializer.data})


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def admin_transactions(request):
    """
    Get all transactions for admin dashboard
    """
    transactions = Transaction.objects.select_related(
        'user', 'product', 'service_type', 'network_provider'
    ).all().order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    user_filter = request.query_params.get('user')
    if user_filter:
        transactions = transactions.filter(user__email__icontains=user_filter)
    
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
        'data': serializer.data,
        'total': transactions.count(),
        'page': int(page),
        'page_size': int(page_size)
    })


@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def user_pricing_management(request, user_id):
    """
    Get or set pricing for a specific user
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        user_pricings = UserPricing.objects.filter(user=user).select_related('product')
        serializer = UserPricingSerializer(user_pricings, many=True)
        return Response({'data': serializer.data})
    
    elif request.method == 'POST':
        # Expecting a list of product_id and price pairs
        pricing_data = request.data.get('pricing', [])
        
        results = []
        for item in pricing_data:
            product_id = item.get('product_id')
            price = item.get('price')
            
            try:
                product = DigitalProduct.objects.get(id=product_id)
                
                user_pricing, created = UserPricing.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={'price': price, 'is_active': True}
                )
                
                if not created:
                    user_pricing.price = price
                    user_pricing.is_active = True
                    user_pricing.save()
                
                serializer = UserPricingSerializer(user_pricing)
                results.append(serializer.data)
                
            except DigitalProduct.DoesNotExist:
                results.append({
                    'product_id': product_id,
                    'error': 'Product not found'
                })
        
        return Response({'data': results})