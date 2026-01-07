from rest_framework import serializers
from apps.digital.models import (
    ServiceType, NetworkProvider, DigitalProduct, 
    DigitalTransaction, APIKey, UserPricing
)
from apps.users.models import User
from apps.wallets.models import Wallet


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'


class NetworkProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkProvider
        fields = '__all__'


class DigitalProductSerializer(serializers.ModelSerializer):
    service_type = ServiceTypeSerializer(read_only=True)
    network_provider = NetworkProviderSerializer(read_only=True)
    
    class Meta:
        model = DigitalProduct
        fields = '__all__'


class UserPricingSerializer(serializers.ModelSerializer):
    product = DigitalProductSerializer(read_only=True)
    
    class Meta:
        model = UserPricing
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    product = DigitalProductSerializer(read_only=True)
    service_type = ServiceTypeSerializer(read_only=True)
    network_provider = NetworkProviderSerializer(read_only=True)
    
    class Meta:
        model = DigitalTransaction
        fields = '__all__'


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalTransaction
        fields = ['product', 'phone_number', 'quantity', 'priority']
        read_only_fields = ['user', 'amount', 'price', 'status', 'reference', 'provider']

    def validate_phone_number(self, value):
        # Basic phone number validation
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'is_active', 'is_sandbox', 'ip_whitelist', 
                 'daily_limit', 'monthly_limit', 'current_daily_count', 
                 'current_monthly_count', 'last_used_at', 'created_at']
        read_only_fields = ['key', 'current_daily_count', 'current_monthly_count', 'last_used_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['name', 'is_sandbox', 'ip_whitelist', 'daily_limit', 'monthly_limit']
    
    def create(self, validated_data):
        import uuid
        validated_data['key'] = f"sk_{uuid.uuid4().hex}"
        return super().create(validated_data)