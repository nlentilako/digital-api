from celery import shared_task
import logging
from apps.digital.services.digital_service import DigitalService
from apps.digital.models import Transaction
from apps.digital.services.provider_factory import ProviderFactory
from django.utils import timezone


logger = logging.getLogger(__name__)


@shared_task
def process_transaction_async(transaction_id):
    """
    Async task to process a digital transaction.
    
    Args:
        transaction_id: ID of the transaction to process
    """
    try:
        digital_service = DigitalService()
        result = digital_service.process_transaction(transaction_id)
        logger.info(f"Successfully processed transaction {transaction_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
        raise e


@shared_task
def retry_failed_transaction(transaction_id):
    """
    Async task to retry a failed transaction.
    
    Args:
        transaction_id: ID of the transaction to retry
    """
    try:
        digital_service = DigitalService()
        result = digital_service.retry_transaction(transaction_id)
        logger.info(f"Successfully retried transaction {transaction_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error retrying transaction {transaction_id}: {str(e)}")
        raise e


@shared_task
def verify_transaction_with_provider(transaction_id):
    """
    Async task to verify a transaction with the provider.
    
    Args:
        transaction_id: ID of the transaction to verify
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        provider = ProviderFactory.get_provider(transaction.provider)
        result = provider.verify_transaction(transaction.provider_transaction_id)
        
        # Update transaction status based on verification
        if result.get('verified'):
            transaction.status = 'completed'
            transaction.provider_response = {**transaction.provider_response, 'verified': True}
        else:
            transaction.status = 'failed'
            transaction.provider_response = {**transaction.provider_response, 'verified': False}
        
        transaction.save()
        
        logger.info(f"Verified transaction {transaction_id} with provider: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying transaction {transaction_id}: {str(e)}")
        raise e


@shared_task
def cleanup_old_transactions():
    """
    Async task to cleanup old transactions based on their status.
    """
    try:
        # Define thresholds for cleanup
        from datetime import timedelta
        failed_threshold = timezone.now() - timedelta(days=30)  # 30 days for failed transactions
        completed_threshold = timezone.now() - timedelta(days=365)  # 1 year for completed transactions
        
        # Delete failed transactions older than threshold
        old_failed_transactions = Transaction.objects.filter(
            status='failed',
            created_at__lt=failed_threshold
        )
        failed_count = old_failed_transactions.count()
        old_failed_transactions.delete()
        
        # Archive or delete completed transactions older than threshold
        old_completed_transactions = Transaction.objects.filter(
            status='completed',
            created_at__lt=completed_threshold
        )
        completed_count = old_completed_transactions.count()
        old_completed_transactions.delete()
        
        logger.info(f"Cleaned up {failed_count} failed transactions and {completed_count} completed transactions")
        
        return {
            'failed_deleted': failed_count,
            'completed_deleted': completed_count
        }
    except Exception as e:
        logger.error(f"Error during transaction cleanup: {str(e)}")
        raise e


@shared_task
def send_transaction_notification(transaction_id, notification_type='status_update'):
    """
    Async task to send transaction notifications.
    
    Args:
        transaction_id: ID of the transaction
        notification_type: Type of notification to send
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # In a real implementation, this would send emails, SMS, or push notifications
        # For now, we'll just log the notification
        logger.info(f"Notification sent for transaction {transaction_id} - Type: {notification_type}")
        
        # Example: send email notification
        # send_mail(
        #     subject=f'Transaction {transaction.status.title()} - {transaction.reference}',
        #     message=f'Your transaction {transaction.reference} is now {transaction.status}.',
        #     from_email='noreply@digitalorchestrator.com',
        #     recipient_list=[transaction.user.email],
        # )
        
        return {
            'transaction_id': transaction_id,
            'notification_type': notification_type,
            'sent_to': transaction.user.email
        }
    except Exception as e:
        logger.error(f"Error sending notification for transaction {transaction_id}: {str(e)}")
        raise e