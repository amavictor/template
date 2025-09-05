from django.shortcuts import get_object_or_404
from .models import Cart, SessionCart


def cart(request):
    """
    Context processor to make cart information available in all templates.
    """
    cart_obj = None
    total_items = 0
    total_price = 0
    
    if request.user.is_authenticated:
        try:
            cart_obj = Cart.objects.get(user=request.user)
            total_items = cart_obj.get_total_items()
            total_price = cart_obj.get_total_price()
        except Cart.DoesNotExist:
            pass
    else:
        # Handle anonymous user cart using session
        session_key = request.session.session_key
        if session_key:
            try:
                session_cart = SessionCart.objects.get(session_key=session_key)
                total_items = session_cart.get_total_items()
                total_price = session_cart.get_total_price()
            except SessionCart.DoesNotExist:
                pass
    
    return {
        'cart': cart_obj,
        'cart_total_items': total_items,
        'cart_total_price': total_price,
    }