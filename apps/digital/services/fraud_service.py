from typing import Dict, Any
from apps.users.models import User


class FraudDetectionService:
    """
    Service class for detecting potential fraud in digital transactions.
    """
    
    def __init__(self):
        # Configuration for fraud detection rules
        self.config = {
            'max_daily_amount': 10000,  # Maximum daily transaction amount
            'max_single_transaction': 1000,  # Maximum single transaction amount
            'min_transaction_interval': 60,  # Minimum seconds between transactions
            'max_transactions_per_hour': 50,  # Maximum transactions per hour
        }

    def check_transaction_risk(self, user, phone_number: str, amount: float) -> Dict[str, Any]:
        """
        Check if a transaction poses a fraud risk.
        
        Args:
            user: The user initiating the transaction
            phone_number: The recipient phone number
            amount: The transaction amount
            
        Returns:
            Dict containing fraud check result
        """
        risk_factors = []
        
        # Check if amount is too high
        if amount > self.config['max_single_transaction']:
            risk_factors.append(f"Transaction amount {amount} exceeds limit {self.config['max_single_transaction']}")
        
        # Check for suspicious patterns (simplified for this example)
        recent_transactions_count = self._get_recent_transactions_count(user)
        if recent_transactions_count > self.config['max_transactions_per_hour']:
            risk_factors.append(f"Too many transactions ({recent_transactions_count}) in the last hour")
        
        # Check if phone number is suspicious (simplified)
        if self._is_suspicious_phone_number(phone_number):
            risk_factors.append(f"Suspicious phone number pattern: {phone_number}")
        
        # Check if user is on any watch list (simplified)
        if self._is_user_on_watch_list(user):
            risk_factors.append(f"User {user.email} is on fraud watch list")
        
        is_fraud = len(risk_factors) > 0
        
        return {
            'is_fraud': is_fraud,
            'risk_factors': risk_factors,
            'risk_score': len(risk_factors),
            'reason': '; '.join(risk_factors) if risk_factors else 'No fraud detected'
        }

    def _get_recent_transactions_count(self, user, hours: int = 1) -> int:
        """
        Get the number of recent transactions for a user.
        
        Args:
            user: The user to check
            hours: Number of hours to look back
            
        Returns:
            Number of transactions in the specified time period
        """
        from django.utils import timezone
        from apps.digital.models import Transaction
        from datetime import timedelta
        
        time_threshold = timezone.now() - timedelta(hours=hours)
        
        return Transaction.objects.filter(
            user=user,
            created_at__gte=time_threshold
        ).count()

    def _is_suspicious_phone_number(self, phone_number: str) -> bool:
        """
        Check if a phone number is suspicious.
        
        Args:
            phone_number: The phone number to check
            
        Returns:
            True if the phone number is suspicious, False otherwise
        """
        # Example checks - these would be more sophisticated in a real system
        if len(phone_number) < 10:
            return True
        
        # Check for repeated digits
        if len(set(phone_number)) == 1:
            return True
            
        # Check for sequential digits
        if self._is_sequential(phone_number):
            return True
            
        return False

    def _is_sequential(self, phone_number: str) -> bool:
        """
        Check if phone number has sequential digits.
        
        Args:
            phone_number: The phone number to check
            
        Returns:
            True if the phone number has sequential digits, False otherwise
        """
        # Check forward sequence (e.g., 123456)
        for i in range(len(phone_number) - 2):
            if (int(phone_number[i+1]) == int(phone_number[i]) + 1 and 
                int(phone_number[i+2]) == int(phone_number[i+1]) + 1):
                return True
        
        # Check backward sequence (e.g., 654321)
        for i in range(len(phone_number) - 2):
            if (int(phone_number[i+1]) == int(phone_number[i]) - 1 and 
                int(phone_number[i+2]) == int(phone_number[i+1]) - 1):
                return True
        
        return False

    def _is_user_on_watch_list(self, user) -> bool:
        """
        Check if a user is on a fraud watch list.
        
        Args:
            user: The user to check
            
        Returns:
            True if the user is on the watch list, False otherwise
        """
        # In a real system, this would check against a database of flagged users
        # For now, we'll just return False
        return False