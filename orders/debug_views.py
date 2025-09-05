from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import redirect
from cart.models import Cart, CartItem
import logging

logger = logging.getLogger(__name__)

class DebugCheckoutView(LoginRequiredMixin, View):
    """Debug view to test checkout functionality."""
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Debug checkout called for user: {request.user.id}")
        
        try:
            # Get user's cart
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            logger.info(f"Cart found with {cart_items.count()} items")
            
            if not cart_items.exists():
                return HttpResponse("Cart is empty - this should redirect to cart with error message")
            
            # For now, just return a success message
            item_names = [item.product.name for item in cart_items]
            return HttpResponse(f"Checkout would process these items: {', '.join(item_names)}")
            
        except Cart.DoesNotExist:
            logger.error("Cart not found for user")
            return HttpResponse("Cart not found - this should redirect to cart")
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            return HttpResponse(f"Error: {str(e)}")