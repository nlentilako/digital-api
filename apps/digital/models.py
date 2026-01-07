import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal
from apps.users.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('data', 'Data'),
        ('airtime', 'Airtime'),
        ('voucher', 'Voucher'),
        ('sms', 'SMS'),
    ]
    
    NETWORK_CHOICES = [
        ('mtn', 'MTN'),
        ('telecel', 'Telecel'),
        ('airteltigo', 'AirtelTigo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    network = models.CharField(max_length=50, choices=NETWORK_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    agent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_amount = models.CharField(max_length=20, null=True, blank=True)
    validity_days = models.IntegerField(null=True, blank=True)
    sms_count = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    image = models.URLField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    stock = models.IntegerField(default=-1)  # -1 means unlimited
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Wallet'),
        ('paystack', 'Paystack'),
        ('card', 'Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recipient_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    transaction = models.ForeignKey('WalletTransaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    api_response = models.JSONField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class BulkOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bulk_orders')
    total_recipients = models.IntegerField()
    successful_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recipients = models.JSONField()
    results = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.batch_number


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PROVIDER_CHOICES = [
        ('paystack', 'Paystack'),
        ('stripe', 'Stripe'),
        ('momo', 'MoMo'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('order', 'Order'),
        ('wallet_funding', 'Wallet Funding'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_reference = models.CharField(max_length=200, null=True, blank=True)
    provider_response = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


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


class DigitalTransaction(models.Model):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    key_prefix = models.CharField(max_length=20)  # First 12 chars
    key_hash = models.CharField(max_length=64, unique=True)  # SHA256 hash
    environment = models.CharField(max_length=10, default='test')  # test, live
    status = models.CharField(max_length=20, default='active')  # active, inactive, revoked, expired
    permissions = models.JSONField(default=list)  # Allowed scopes
    rate_limit = models.IntegerField(default=1000)  # Requests/hour
    allowed_ips = models.JSONField(default=list)  # IP whitelist
    last_used_at = models.DateTimeField(null=True, blank=True)
    total_requests = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class TransactionLog(models.Model):
    """Log of all transaction changes for audit trail"""
    transaction = models.ForeignKey(DigitalTransaction, on_delete=models.CASCADE)
    status_before = models.CharField(max_length=20)
    status_after = models.CharField(max_length=20)
    action = models.CharField(max_length=50)  # e.g., 'status_change', 'retry', 'refund'
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction.id} - {self.action}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('system', 'System'),
        ('promo', 'Promotion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class ChatRoom(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_chat_rooms')
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject


class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    attachment_url = models.URLField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.email} in {self.room.subject}"


class CMSPages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    meta_title = models.CharField(max_length=200, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    user_email = models.EmailField(max_length=254, null=True, blank=True)  # Preserved email
    user_role = models.CharField(max_length=50, null=True, blank=True)  # Role at time of action
    action = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    resource_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, blank=True)
    request_path = models.CharField(max_length=500, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} - {self.user_email or 'N/A'}"