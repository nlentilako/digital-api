from rest_framework import serializers
from apps.wallets.models import Wallet, WalletTransaction


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']