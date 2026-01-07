from rest_framework import serializers
from apps.users.models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'user_type', 'is_active', 'date_joined', 'profile', 'username'
        ]
        read_only_fields = ['id', 'date_joined', 'username']