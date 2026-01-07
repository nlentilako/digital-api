from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import hashlib
import hmac
from django.conf import settings
from apps.digital.models import Transaction


@api_view(['POST'])
@permission_classes([AllowAny])
def mtn_webhook(request):
    """
    Webhook endpoint for MTN provider notifications.
    """
    try:
        # Verify webhook signature (implement based on MTN's requirements)
        if not _verify_webhook_signature(request, 'mtn'):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Process the webhook payload
        payload = request.data
        transaction_id = payload.get('transaction_id')
        status = payload.get('status')
        provider_response = payload.get('provider_response', {})
        
        # Update the transaction in the database
        try:
            transaction = Transaction.objects.get(provider_transaction_id=transaction_id)
            transaction.provider_response = provider_response
            
            if status == 'success':
                transaction.status = 'completed'
                transaction.completed_at = transaction.completed_at or transaction.updated_at
            elif status == 'failed':
                transaction.status = 'failed'
                transaction.failed_at = transaction.updated_at
            else:
                transaction.status = status  # Update to whatever status was provided
            
            transaction.save()
            
            return Response({'status': 'success', 'message': 'Webhook processed successfully'})
            
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def vodafone_webhook(request):
    """
    Webhook endpoint for Vodafone provider notifications.
    """
    try:
        # Verify webhook signature (implement based on Vodafone's requirements)
        if not _verify_webhook_signature(request, 'vodafone'):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Process the webhook payload
        payload = request.data
        transaction_id = payload.get('transaction_id')
        status = payload.get('status')
        provider_response = payload.get('provider_response', {})
        
        # Update the transaction in the database
        try:
            transaction = Transaction.objects.get(provider_transaction_id=transaction_id)
            transaction.provider_response = provider_response
            
            if status == 'success':
                transaction.status = 'completed'
                transaction.completed_at = transaction.completed_at or transaction.updated_at
            elif status == 'failed':
                transaction.status = 'failed'
                transaction.failed_at = transaction.updated_at
            else:
                transaction.status = status  # Update to whatever status was provided
            
            transaction.save()
            
            return Response({'status': 'success', 'message': 'Webhook processed successfully'})
            
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def airteltigo_webhook(request):
    """
    Webhook endpoint for AirtelTigo provider notifications.
    """
    try:
        # Verify webhook signature (implement based on AirtelTigo's requirements)
        if not _verify_webhook_signature(request, 'airteltigo'):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Process the webhook payload
        payload = request.data
        transaction_id = payload.get('transaction_id')
        status = payload.get('status')
        provider_response = payload.get('provider_response', {})
        
        # Update the transaction in the database
        try:
            transaction = Transaction.objects.get(provider_transaction_id=transaction_id)
            transaction.provider_response = provider_response
            
            if status == 'success':
                transaction.status = 'completed'
                transaction.completed_at = transaction.completed_at or transaction.updated_at
            elif status == 'failed':
                transaction.status = 'failed'
                transaction.failed_at = transaction.updated_at
            else:
                transaction.status = status  # Update to whatever status was provided
            
            transaction.save()
            
            return Response({'status': 'success', 'message': 'Webhook processed successfully'})
            
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _verify_webhook_signature(request, provider):
    """
    Verify the signature of a webhook request.
    
    Args:
        request: The webhook request
        provider: The provider name
        
    Returns:
        True if signature is valid, False otherwise
    """
    # This is a simplified implementation
    # In a real system, you would implement provider-specific signature verification
    
    # Get the signature from the request headers
    signature = request.META.get('HTTP_X_SIGNATURE') or request.META.get('HTTP_X_WEBHOOK_SIGNATURE')
    
    if not signature:
        # Some providers may use different header names
        signature = request.META.get('HTTP_X_MTN_SIGNATURE') or \
                   request.META.get('HTTP_X_VODAFONE_SIGNATURE') or \
                   request.META.get('HTTP_X_AIRTELTIGO_SIGNATURE')
    
    if not signature:
        # For development, you might want to skip signature verification
        # But in production, this should always be enforced
        return getattr(settings, 'SKIP_WEBHOOK_VERIFICATION', False)
    
    # Get the secret key for the provider
    provider_secret = getattr(settings, f'{provider.upper()}_WEBHOOK_SECRET', None)
    
    if not provider_secret:
        return False
    
    # Create the expected signature
    payload = request._request.body.decode('utf-8')
    expected_signature = hmac.new(
        provider_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(signature, expected_signature)