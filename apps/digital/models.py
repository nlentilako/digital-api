from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal


class ServiceType(models.Model):
    """Digital service types like Data, Airtime, WAEC, etc."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)  # e.g., 'DATA', 'AIRTIME', 'WAEC'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class NetworkProvider(models.Model):
    """Network providers like MTN, Vodafone, AirtelTigo"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)  # e.g., 'MTN', 'VODAFONE', 'AIRTEL'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DigitalProduct(models.Model):
    """Digital products like data bundles, airtime denominations, etc."""
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    network_provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, unique=True)
    denomination = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., 1GB, 500MB, 100GHS
    size = models.CharField(max_length=50, null=True, blank=True)  # e.g., '1GB', '500MB' for data
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserPricing(models.Model):
    """Pricing for different user roles"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Transaction(models.Model):
    """Digital service transaction"""
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.CharField(max_length=50, unique=True, primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE)
    network_provider = models.ForeignKey(NetworkProvider, on_delete=models.CASCADE, null=True, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)  # Recipient phone number
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount debited from wallet
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    quantity = models.IntegerField(default=1)  # Quantity of products
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    reference = models.CharField(max_length=100, unique=True)  # External reference from provider
    provider_response = models.JSONField(default=dict, blank=True)  # Raw response from provider
    provider_transaction_id = models.CharField(max_length=100, blank=True)  # Transaction ID from provider
    provider = models.CharField(max_length=100)  # Provider name
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    initiated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.status}"


class APIKey(models.Model):
    """API keys for resellers and external integrations"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_sandbox = models.BooleanField(default=False)
    ip_whitelist = models.JSONField(default=list, blank=True)  # List of allowed IPs
    daily_limit = models.IntegerField(default=1000)  # Daily transaction limit
    monthly_limit = models.IntegerField(default=10000)  # Monthly transaction limit
    current_daily_count = models.IntegerField(default=0)
    current_monthly_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class TransactionLog(models.Model):
    """Log of all transaction changes for audit trail"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    status_before = models.CharField(max_length=20)
    status_after = models.CharField(max_length=20)
    action = models.CharField(max_length=50)  # e.g., 'status_change', 'retry', 'refund'
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction.id} - {self.action}"