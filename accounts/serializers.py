from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import User, APIToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'phone', 'company', 'date_joined', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'user_type']


class APITokenSerializer(serializers.ModelSerializer):
    """
    Serializer for APIToken model.
    """
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = APIToken
        fields = [
            'id', 'name', 'is_active', 'expires_at', 'created_at', 'updated_at',
            'last_used', 'is_expired', 'is_valid', 'days_until_expiry',
            'can_read_products', 'can_manage_cart', 'can_place_orders', 'can_manage_wishlist'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_used']
    
    def get_days_until_expiry(self, obj):
        """Calculate days until token expires."""
        if not obj.expires_at:
            return None
        
        now = timezone.now()
        if obj.expires_at <= now:
            return 0
        
        delta = obj.expires_at - now
        return delta.days


class APITokenWithKeySerializer(APITokenSerializer):
    """
    Serializer for APIToken that includes the actual token key.
    Only used when creating or regenerating tokens.
    """
    token = serializers.CharField(read_only=True)
    
    class Meta(APITokenSerializer.Meta):
        fields = APITokenSerializer.Meta.fields + ['token']


class CreateAPITokenSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new API tokens.
    """
    expires_in_days = serializers.IntegerField(required=False, min_value=1, max_value=365)
    
    class Meta:
        model = APIToken
        fields = [
            'name', 'expires_in_days', 'can_read_products', 
            'can_manage_cart', 'can_place_orders', 'can_manage_wishlist'
        ]
    
    def validate_name(self, value):
        """Validate that token name is unique for this user."""
        user = self.context['request'].user
        if APIToken.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError('Token with this name already exists')
        return value
    
    def create(self, validated_data):
        """Create a new API token with optional expiration."""
        expires_in_days = validated_data.pop('expires_in_days', None)
        
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        validated_data['expires_at'] = expires_at
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return the created token with the JWT key."""
        return APITokenWithKeySerializer(instance, context=self.context).data


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User profile management.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'company']
    
    def update(self, instance, validated_data):
        """Update user profile."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance