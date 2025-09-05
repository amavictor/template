from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from products.models import Product
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from .serializers import (
    ProductSerializer, 
    CartSerializer, CartItemSerializer,
    WishlistSerializer, WishlistItemSerializer
)
from .authentication import APITokenAuthentication


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Products
    Provides list and detail views for products.
    """
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductSerializer
    authentication_classes = [APITokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'


class CartViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Cart operations
    Allows users to manage their shopping cart.
    """
    serializer_class = CartSerializer
    authentication_classes = [APITokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, status='active')
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response({
                'message': f'{product.name} added to cart',
                'cart_total_items': cart.get_total_items()
            })
            
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product_id')
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            
            return Response({
                'message': 'Item removed from cart',
                'cart_total_items': cart.get_total_items()
            })
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.clear()
            return Response({'message': 'Cart cleared'})
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)


class WishlistViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Wishlist operations
    Allows users to manage their wishlist.
    """
    serializer_class = WishlistSerializer
    authentication_classes = [APITokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's wishlist"""
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to wishlist"""
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id, status='active')
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            
            wishlist_item, created = WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                product=product
            )
            
            if created:
                return Response({
                    'message': f'{product.name} added to wishlist',
                    'wishlist_total_items': wishlist.get_item_count()
                })
            else:
                return Response({
                    'message': 'Item already in wishlist',
                    'wishlist_total_items': wishlist.get_item_count()
                })
            
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from wishlist"""
        product_id = request.data.get('product_id')
        
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            wishlist_item.delete()
            
            return Response({
                'message': 'Item removed from wishlist',
                'wishlist_total_items': wishlist.get_item_count()
            })
            
        except (Wishlist.DoesNotExist, WishlistItem.DoesNotExist):
            return Response({'error': 'Item not found in wishlist'}, status=status.HTTP_404_NOT_FOUND)