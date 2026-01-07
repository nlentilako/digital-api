from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    """Base exception class for API exceptions"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        super().__init__(detail, code)
        if status_code is not None:
            self.status_code = status_code


class InsufficientFundsException(BaseAPIException):
    """Raised when user has insufficient funds for a transaction"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient funds in wallet.'
    default_code = 'insufficient_funds'


class InvalidTransactionException(BaseAPIException):
    """Raised when a transaction is invalid"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Transaction is invalid.'
    default_code = 'invalid_transaction'


class ProviderException(BaseAPIException):
    """Raised when there's an error with a provider"""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Provider error occurred.'
    default_code = 'provider_error'


class FraudDetectedException(BaseAPIException):
    """Raised when fraud is detected"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Fraud detected in transaction.'
    default_code = 'fraud_detected'


class WalletLockedException(BaseAPIException):
    """Raised when wallet is locked"""
    status_code = status.HTTP_423_LOCKED
    default_detail = 'Wallet is locked.'
    default_code = 'wallet_locked'


class ServiceNotAvailableException(BaseAPIException):
    """Raised when a digital service is not available"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Service is not available.'
    default_code = 'service_not_available'


class RateLimitExceededException(BaseAPIException):
    """Raised when rate limit is exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded.'
    default_code = 'rate_limit_exceeded'