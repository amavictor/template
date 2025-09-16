from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import APITokenPackage, UserAPIToken, Subscription
from cart.models import Cart, CartItem
from products.models import Product

def dashboard(request):
    return render(request, 'subscriptions/dashboard.html')

def my_subscriptions(request):
    return render(request, 'subscriptions/my_subscriptions.html')

def subscription_detail(request, subscription_id):
    return render(request, 'subscriptions/detail.html')

@login_required
def api_settings(request):
    """API token settings and subscription packages."""
    packages = APITokenPackage.objects.filter(is_active=True)
    user_tokens = UserAPIToken.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'packages': packages,
        'user_tokens': user_tokens,
    }
    return render(request, 'subscriptions/api_settings.html', context)

@login_required
@require_POST
def purchase_api_package(request):
    """Add API token package to cart and redirect to checkout."""
    try:
        data = json.loads(request.body)
        package_id = data.get('package_id')
        
        package = get_object_or_404(APITokenPackage, id=package_id, is_active=True)
        
        # Create a temporary product for the API package if it doesn't exist
        product, created = Product.objects.get_or_create(
            name=f"API Token - {package.name}",
            defaults={
                'description': package.description or f"API access for {package.get_duration_display()}",
                'short_description': package.description or f"API access for {package.get_duration_display()}",
                'price': package.price,
                'product_type': 'service',
                'status': 'active',
                'sku': f'API-{package.id}',
            }
        )
        
        # Add to cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if this package is already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            messages.info(request, f'{package.name} is already in your cart.')
        else:
            messages.success(request, f'{package.name} has been added to your cart.')
        
        return JsonResponse({
            'success': True,
            'message': f'{package.name} added to cart',
            'redirect_url': '/cart/'  # Redirect to cart page
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def token_details(request, token_id):
    """Display details of a specific API token."""
    token = get_object_or_404(UserAPIToken, id=token_id, user=request.user)
    
    context = {
        'user_token': token,
    }
    return render(request, 'subscriptions/token_details.html', context)
