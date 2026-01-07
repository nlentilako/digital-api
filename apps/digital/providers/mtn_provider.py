import requests
import logging
from typing import Dict, Any
from apps.digital.providers.base_provider import BaseProvider
from apps.digital.models import Transaction
from core.exceptions import ProviderException


logger = logging.getLogger(__name__)


class MTNProvider(BaseProvider):
    """
    MTN Provider Implementation
    """
    
    def __init__(self):
        self.base_url = "https://api.mtn.com/v1"  # Placeholder URL
        self.api_key = None  # Will be set from settings
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def purchase(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Execute a purchase transaction with MTN.
        """
        try:
            # Prepare the payload for MTN API
            payload = {
                'recipient_phone': transaction.phone_number,
                'product_code': transaction.product.code,
                'amount': float(transaction.amount),
                'reference': transaction.reference,
                'customer_reference': str(transaction.id)
            }
            
            # Make API call to MTN
            response = requests.post(
                f"{self.base_url}/data-purchase",  # Placeholder endpoint
                json=payload,
                headers=self.headers
            )
            
            response_data = response.json()
            
            # Format and return response
            formatted_response = self.format_response(response_data)
            
            return {
                'status': 'success' if response.status_code == 200 else 'failed',
                'provider_response': formatted_response,
                'transaction_id': formatted_response.get('transaction_id'),
                'message': formatted_response.get('message', 'Transaction processed'),
                'provider': 'MTN'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MTN Provider API error: {str(e)}")
            return self.handle_error(e)
        except Exception as e:
            logger.error(f"MTN Provider unexpected error: {str(e)}")
            return self.handle_error(e)

    def validate_phone_number(self, phone_number: str, network_provider_code: str) -> Dict[str, Any]:
        """
        Validate a phone number with MTN.
        """
        try:
            payload = {
                'phone_number': phone_number,
                'network_code': network_provider_code
            }
            
            response = requests.post(
                f"{self.base_url}/validate-phone",
                json=payload,
                headers=self.headers
            )
            
            response_data = response.json()
            
            return {
                'status': 'success' if response.status_code == 200 else 'failed',
                'valid': response_data.get('valid', False),
                'message': response_data.get('message', 'Phone number validation completed'),
                'provider_response': response_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MTN Phone validation error: {str(e)}")
            return self.handle_error(e)
        except Exception as e:
            logger.error(f"MTN Phone validation unexpected error: {str(e)}")
            return self.handle_error(e)

    def get_balance(self) -> Dict[str, Any]:
        """
        Get MTN provider account balance.
        """
        try:
            response = requests.get(
                f"{self.base_url}/balance",
                headers=self.headers
            )
            
            response_data = response.json()
            
            return {
                'status': 'success' if response.status_code == 200 else 'failed',
                'balance': response_data.get('balance'),
                'currency': response_data.get('currency', 'GHS'),
                'provider_response': response_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MTN Balance check error: {str(e)}")
            return self.handle_error(e)
        except Exception as e:
            logger.error(f"MTN Balance check unexpected error: {str(e)}")
            return self.handle_error(e)

    def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify a transaction with MTN.
        """
        try:
            response = requests.get(
                f"{self.base_url}/verify-transaction/{transaction_id}",
                headers=self.headers
            )
            
            response_data = response.json()
            
            return {
                'status': 'success' if response.status_code == 200 else 'failed',
                'verified': response_data.get('verified', False),
                'status_message': response_data.get('status'),
                'provider_response': response_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MTN Transaction verification error: {str(e)}")
            return self.handle_error(e)
        except Exception as e:
            logger.error(f"MTN Transaction verification unexpected error: {str(e)}")
            return self.handle_error(e)

    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format MTN provider response to standard format.
        """
        return {
            'raw_response': response,
            'status_code': response.get('status_code'),
            'message': response.get('message'),
            'transaction_id': response.get('transaction_id'),
            'reference': response.get('reference'),
            'details': response
        }