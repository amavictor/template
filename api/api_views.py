from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular import openapi
from products.models import Product
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from .serializers import (
    ProductSerializer, 
    CartSerializer, CartItemSerializer,
    WishlistSerializer, WishlistItemSerializer
)
from .authentication import APITokenAuthentication


@extend_schema(tags=['Products'])
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
    
    @extend_schema(tags=['Cart'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Cart'],
        request=None,  # No request body for GET
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Cart'], 
        exclude=True  # Exclude POST from schema as we use custom actions
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Cart'],
        exclude=True  # Exclude PUT from schema as we use custom actions  
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Cart'],
        exclude=True  # Exclude PATCH from schema as we use custom actions
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(tags=['Cart'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @extend_schema(
        responses={
            200: CartSerializer,
        },
        summary='Get current user cart',
        description='Get the current user\'s shopping cart'
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product_id': {
                        'type': 'integer',
                        'description': 'ID of the product to add to cart',
                        'example': 1
                    },
                    'quantity': {
                        'type': 'integer',
                        'minimum': 1,
                        'default': 1,
                        'description': 'Quantity of the product to add',
                        'example': 2
                    }
                },
                'required': ['product_id']
            }
        },
        responses={
            200: {
                'description': 'Item added to cart successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Product Name added to cart',
                            'cart_total_items': 3
                        }
                    }
                }
            },
            404: {
                'description': 'Product not found',
                'content': {
                    'application/json': {
                        'example': {'error': 'Product not found'}
                    }
                }
            }
        },
        summary='Add item to cart',
        description='Add a product to the user\'s shopping cart'
    )
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
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product_id': {
                        'type': 'integer',
                        'description': 'ID of the product to remove from cart',
                        'example': 1
                    }
                },
                'required': ['product_id']
            }
        },
        responses={
            200: {
                'description': 'Item removed from cart successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Item removed from cart',
                            'cart_total_items': 2
                        }
                    }
                }
            },
            404: {
                'description': 'Item not found in cart',
                'content': {
                    'application/json': {
                        'example': {'error': 'Item not found in cart'}
                    }
                }
            }
        },
        summary='Remove item from cart',
        description='Remove a product from the user\'s shopping cart'
    )
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
    
    @extend_schema(
        request=None,  # No request body needed
        responses={
            200: {
                'description': 'Cart cleared successfully',
                'content': {
                    'application/json': {
                        'example': {'message': 'Cart cleared'}
                    }
                }
            },
            404: {
                'description': 'Cart not found',
                'content': {
                    'application/json': {
                        'example': {'error': 'Cart not found'}
                    }
                }
            }
        },
        summary='Clear cart',
        description='Remove all items from the user\'s shopping cart'
    )
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
    
    @extend_schema(tags=['Wishlist'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Wishlist'],
        request=None,  # No request body for GET
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Wishlist'], 
        exclude=True  # Exclude POST from schema as we use custom actions
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Wishlist'],
        exclude=True  # Exclude PUT from schema as we use custom actions  
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Wishlist'],
        exclude=True  # Exclude PATCH from schema as we use custom actions
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(tags=['Wishlist'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    @extend_schema(
        responses={
            200: WishlistSerializer,
        },
        summary='Get current user wishlist',
        description='Get the current user\'s wishlist'
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's wishlist"""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product_id': {
                        'type': 'integer',
                        'description': 'ID of the product to add to wishlist',
                        'example': 1
                    }
                },
                'required': ['product_id']
            }
        },
        responses={
            200: {
                'description': 'Item added to wishlist successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Product Name added to wishlist',
                            'wishlist_total_items': 3
                        }
                    }
                }
            },
            404: {
                'description': 'Product not found',
                'content': {
                    'application/json': {
                        'example': {'error': 'Product not found'}
                    }
                }
            }
        },
        summary='Add item to wishlist',
        description='Add a product to the user\'s wishlist'
    )
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
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'product_id': {
                        'type': 'integer',
                        'description': 'ID of the product to remove from wishlist',
                        'example': 1
                    }
                },
                'required': ['product_id']
            }
        },
        responses={
            200: {
                'description': 'Item removed from wishlist successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Item removed from wishlist',
                            'wishlist_total_items': 2
                        }
                    }
                }
            },
            404: {
                'description': 'Item not found in wishlist',
                'content': {
                    'application/json': {
                        'example': {'error': 'Item not found in wishlist'}
                    }
                }
            }
        },
        summary='Remove item from wishlist',
        description='Remove a product from the user\'s wishlist'
    )
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