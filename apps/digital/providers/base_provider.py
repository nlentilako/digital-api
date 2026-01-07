from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from apps.digital.models import Transaction


class BaseProvider(ABC):
    """
    Abstract base class for all digital service providers.
    All providers must implement these methods.
    """
    
    @abstractmethod
    def purchase(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Execute a purchase transaction with the provider.
        
        Args:
            transaction: The transaction object containing purchase details
            
        Returns:
            Dict containing provider response
        """
        pass

    @abstractmethod
    def validate_phone_number(self, phone_number: str, network_provider_code: str) -> Dict[str, Any]:
        """
        Validate a phone number with the provider.
        
        Args:
            phone_number: The phone number to validate
            network_provider_code: The network provider code (e.g., 'MTN', 'VODAFONE')
            
        Returns:
            Dict containing validation response
        """
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """
        Get the provider account balance.
        
        Returns:
            Dict containing balance information
        """
        pass

    @abstractmethod
    def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify a transaction with the provider.
        
        Args:
            transaction_id: The transaction ID to verify
            
        Returns:
            Dict containing verification response
        """
        pass

    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the provider response to a standard format.
        
        Args:
            response: Raw response from provider
            
        Returns:
            Formatted response
        """
        return response

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors from provider API calls.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Formatted error response
        """
        return {
            'status': 'error',
            'message': str(error),
            'provider_response': None,
            'transaction_id': None,
        }