import uuid
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.db import transaction as db_transaction
from django.utils import timezone
from apps.digital.models import Transaction, UserPricing, DigitalProduct
from apps.digital.services.provider_factory import ProviderFactory
from apps.wallets.models import Wallet, WalletTransaction
from core.exceptions import (
    InsufficientFundsException, 
    InvalidTransactionException, 
    ProviderException,
    FraudDetectedException,
    ServiceNotAvailableException
)
from apps.digital.services.fraud_service import FraudDetectionService
from apps.digital.services.pricing_service import PricingService


logger = logging.getLogger(__name__)


class DigitalService:
    """
    Main service class for handling digital transactions (Data, Airtime, WAEC, etc.)
    Orchestrates the entire transaction flow from validation to completion.
    """
    
    def __init__(self):
        self.fraud_service = FraudDetectionService()
        self.pricing_service = PricingService()

    def initiate_purchase(self, 
                         user, 
                         product_id: str, 
                         phone_number: str, 
                         quantity: int = 1,
                         priority: str = 'normal') -> Transaction:
        """
        Initiate a digital service purchase.
        
        Args:
            user: The user initiating the purchase
            product_id: ID of the digital product
            phone_number: Recipient phone number
            quantity: Quantity of products to purchase
            priority: Transaction priority (low, normal, high, critical)
            
        Returns:
            Transaction object
        """
        # Validate inputs
        if not phone_number or len(phone_number) < 10:
            raise InvalidTransactionException("Invalid phone number")
        
        if quantity <= 0:
            raise InvalidTransactionException("Quantity must be greater than 0")
        
        # Get the product
        try:
            from apps.digital.models import DigitalProduct
            product = DigitalProduct.objects.select_related(
                'service_type', 'network_provider'
            ).get(id=product_id, is_active=True)
        except DigitalProduct.DoesNotExist:
            raise InvalidTransactionException("Product not found or inactive")
        
        # Check if service is available
        if not product.service_type.is_active:
            raise ServiceNotAvailableException("Service is not available")
        
        # Get user pricing
        price = self.pricing_service.get_user_price(user, product)
        
        # Calculate total amount
        total_amount = price * quantity
        
        # Check for fraud
        fraud_check = self.fraud_service.check_transaction_risk(
            user=user,
            phone_number=phone_number,
            amount=total_amount
        )
        
        if fraud_check['is_fraud']:
            raise FraudDetectedException(f"Fraud detected: {fraud_check['reason']}")
        
        # Create transaction
        transaction_id = str(uuid.uuid4()).replace('-', '')[:12].upper()
        reference = f"TXN{int(timezone.now().timestamp())}{transaction_id}"
        
        transaction = Transaction.objects.create(
            id=transaction_id,
            reference=reference,
            user=user,
            product=product,
            service_type=product.service_type,
            network_provider=product.network_provider,
            phone_number=phone_number,
            amount=total_amount,
            price=price,
            quantity=quantity,
            priority=priority,
            provider=product.network_provider.code.lower() if product.network_provider else 'general'
        )
        
        return transaction

    def process_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Process a digital transaction through the complete flow.
        
        Args:
            transaction_id: ID of the transaction to process
            
        Returns:
            Dict containing transaction result
        """
        try:
            # Get transaction
            transaction = Transaction.objects.select_related(
                'user', 'product', 'service_type', 'network_provider'
            ).get(id=transaction_id)
            
            # Update status to processing
            transaction.status = 'processing'
            transaction.save()
            
            # Lock user wallet to prevent concurrent transactions
            wallet = self._lock_wallet(transaction.user)
            
            try:
                # Check wallet balance
                if wallet.balance < transaction.amount:
                    raise InsufficientFundsException(
                        f"Insufficient funds. Balance: {wallet.balance}, "
                        f"Required: {transaction.amount}"
                    )
                
                # Debit wallet
                wallet_transaction = self._debit_wallet(
                    wallet=wallet,
                    amount=transaction.amount,
                    reference=transaction.reference,
                    description=f"Digital service purchase: {transaction.product.name}"
                )
                
                # Link wallet transaction to digital transaction
                transaction.provider = transaction.provider
                transaction.save()
                
            except Exception as e:
                # If wallet debit fails, unlock wallet and return error
                self._unlock_wallet(transaction.user)
                raise e
            
            # Get provider
            try:
                provider = ProviderFactory.get_provider(transaction.provider)
            except ValueError as e:
                # Unlock wallet on provider error
                self._unlock_wallet(transaction.user)
                raise ProviderException(f"Provider error: {str(e)}")
            
            # Execute purchase with provider
            provider_response = provider.purchase(transaction)
            
            # Process provider response
            if provider_response.get('status') == 'success':
                # Complete transaction
                transaction.status = 'completed'
                transaction.provider_response = provider_response
                transaction.provider_transaction_id = provider_response.get('transaction_id')
                transaction.completed_at = timezone.now()
                transaction.save()
                
                # Unlock wallet
                self._unlock_wallet(transaction.user)
                
                return {
                    'status': 'success',
                    'transaction_id': transaction.id,
                    'reference': transaction.reference,
                    'provider_response': provider_response,
                    'message': 'Transaction completed successfully'
                }
            else:
                # Handle failed transaction - rollback wallet
                self._rollback_wallet_transaction(wallet_transaction)
                
                # Unlock wallet
                self._unlock_wallet(transaction.user)
                
                # Update transaction status
                transaction.status = 'failed'
                transaction.provider_response = provider_response
                transaction.failed_at = timezone.now()
                transaction.save()
                
                raise ProviderException(f"Provider transaction failed: {provider_response.get('message')}")
                
        except Transaction.DoesNotExist:
            raise InvalidTransactionException("Transaction not found")
        except Exception as e:
            # Log error
            logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
            
            # Try to unlock wallet if it's still locked
            try:
                self._unlock_wallet(transaction.user)
            except:
                pass  # Ignore if user doesn't have a wallet
            
            raise e

    def _lock_wallet(self, user) -> Wallet:
        """
        Lock a user's wallet for transaction processing.
        
        Args:
            user: The user whose wallet to lock
            
        Returns:
            Wallet object
        """
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        if wallet.is_locked:
            raise Exception("Wallet is already locked")
        
        wallet.is_locked = True
        wallet.save()
        
        return wallet

    def _unlock_wallet(self, user) -> Wallet:
        """
        Unlock a user's wallet after transaction processing.
        
        Args:
            user: The user whose wallet to unlock
            
        Returns:
            Wallet object
        """
        wallet = Wallet.objects.get(user=user)
        wallet.is_locked = False
        wallet.save()
        
        return wallet

    def _debit_wallet(self, wallet: Wallet, amount: Decimal, 
                     reference: str, description: str) -> WalletTransaction:
        """
        Debit an amount from a wallet.
        
        Args:
            wallet: The wallet to debit
            amount: Amount to debit
            reference: Transaction reference
            description: Description of the transaction
            
        Returns:
            WalletTransaction object
        """
        balance_before = wallet.balance
        balance_after = balance_before - amount
        
        # Create wallet transaction
        wallet_transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='debit',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference=reference,
            description=description,
            status='pending'
        )
        
        # Update wallet balance
        wallet.balance = balance_after
        wallet.save()
        
        # Mark wallet transaction as completed
        wallet_transaction.status = 'completed'
        wallet_transaction.processed_at = timezone.now()
        wallet_transaction.save()
        
        return wallet_transaction

    def _credit_wallet(self, wallet: Wallet, amount: Decimal, 
                      reference: str, description: str) -> WalletTransaction:
        """
        Credit an amount to a wallet.
        
        Args:
            wallet: The wallet to credit
            amount: Amount to credit
            reference: Transaction reference
            description: Description of the transaction
            
        Returns:
            WalletTransaction object
        """
        balance_before = wallet.balance
        balance_after = balance_before + amount
        
        # Create wallet transaction
        wallet_transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='credit',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference=reference,
            description=description,
            status='pending'
        )
        
        # Update wallet balance
        wallet.balance = balance_after
        wallet.save()
        
        # Mark wallet transaction as completed
        wallet_transaction.status = 'completed'
        wallet_transaction.processed_at = timezone.now()
        wallet_transaction.save()
        
        return wallet_transaction

    def _rollback_wallet_transaction(self, wallet_transaction: WalletTransaction):
        """
        Rollback a wallet transaction by crediting the amount back.
        
        Args:
            wallet_transaction: The wallet transaction to rollback
        """
        if wallet_transaction.transaction_type == 'debit':
            # Credit the amount back to the wallet
            wallet = wallet_transaction.wallet
            credit_transaction = self._credit_wallet(
                wallet=wallet,
                amount=wallet_transaction.amount,
                reference=f"R-{wallet_transaction.reference}",
                description=f"Rollback: {wallet_transaction.description}"
            )
            
            # Update original transaction status
            wallet_transaction.status = 'reversed'
            wallet_transaction.save()
            
            return credit_transaction

    def retry_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Retry a failed transaction.
        
        Args:
            transaction_id: ID of the transaction to retry
            
        Returns:
            Dict containing retry result
        """
        transaction = Transaction.objects.get(id=transaction_id)
        
        if transaction.status != 'failed':
            raise InvalidTransactionException("Only failed transactions can be retried")
        
        if transaction.retry_count >= transaction.max_retries:
            raise InvalidTransactionException("Maximum retry attempts reached")
        
        # Update retry count
        transaction.retry_count += 1
        transaction.status = 'pending'
        transaction.save()
        
        # Process the transaction again
        return self.process_transaction(transaction_id)

    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get the status of a transaction.
        
        Args:
            transaction_id: ID of the transaction to check
            
        Returns:
            Dict containing transaction status
        """
        transaction = Transaction.objects.select_related(
            'user', 'product', 'service_type', 'network_provider'
        ).get(id=transaction_id)
        
        return {
            'transaction_id': transaction.id,
            'reference': transaction.reference,
            'status': transaction.status,
            'product': transaction.product.name,
            'phone_number': transaction.phone_number,
            'amount': float(transaction.amount),
            'provider': transaction.provider,
            'created_at': transaction.created_at,
            'completed_at': transaction.completed_at,
            'provider_response': transaction.provider_response
        }