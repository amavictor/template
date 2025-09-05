from rest_framework import serializers
from products.models import Product
from cart.models import Cart, CartItem, Wishlist, WishlistItem


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku',
            'short_description', 'description', 'environmental_matrix', 
            'price', 'compare_at_price', 'main_image', 'stock_quantity', 
            'is_featured', 'created_at'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Item model."""
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'added_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_price'] = instance.get_total_price()
        return data


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_items'] = instance.get_total_items()
        data['total_price'] = instance.get_total_price()
        return data


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist Item model."""
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'added_at', 'note']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""
    items = WishlistItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'item_count', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['item_count'] = instance.get_item_count()
        return data