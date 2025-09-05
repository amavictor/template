from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from products.models import Product
from .models import Cart, CartItem, Wishlist, WishlistItem


class CartView(TemplateView):
    """Display cart contents."""
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.request.user)
                context['cart'] = cart
                context['cart_items'] = cart.items.all()
                context['total_price'] = cart.get_total_price()
                context['total_items'] = cart.get_total_items()
            except Cart.DoesNotExist:
                context['cart'] = None
                context['cart_items'] = []
                context['total_price'] = 0
                context['total_items'] = 0
        else:
            # For anonymous users, show empty cart with login message
            context['cart'] = None
            context['cart_items'] = []
            context['total_price'] = 0
            context['total_items'] = 0
        return context


class WishlistView(LoginRequiredMixin, TemplateView):
    """Display wishlist contents."""
    template_name = 'cart/wishlist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            wishlist = Wishlist.objects.get(user=self.request.user)
            context['wishlist'] = wishlist
            context['wishlist_items'] = wishlist.items.all()
        except Wishlist.DoesNotExist:
            context['wishlist'] = None
            context['wishlist_items'] = []
        return context


@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(LoginRequiredMixin, TemplateView):
    """Add product to cart."""
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in to add items to cart'}, status=401)
        
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = get_object_or_404(Product, id=product_id, status='active')
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart',
                'cart_count': cart.get_total_items()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromCartView(LoginRequiredMixin, TemplateView):
    """Remove product from cart."""
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in'}, status=401)
        
        product_id = request.POST.get('product_id')
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'cart_count': cart.get_total_items(),
                'total_price': float(cart.get_total_price())
            })
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Item not found in cart'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCartQuantityView(LoginRequiredMixin, TemplateView):
    """Update cart item quantity."""
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in'}, status=401)
        
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be positive'}, status=400)
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'cart_count': cart.get_total_items(),
                'total_price': float(cart.get_total_price()),
                'item_total': float(cart_item.get_total_price())
            })
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Item not found in cart'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class AddToWishlistView(LoginRequiredMixin, TemplateView):
    """Add product to wishlist."""
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in to add items to wishlist'}, status=401)
        
        product_id = request.POST.get('product_id')
        
        try:
            product = get_object_or_404(Product, id=product_id, status='active')
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            
            wishlist_item, created = WishlistItem.objects.get_or_create(
                wishlist=wishlist,
                product=product
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} added to wishlist',
                    'wishlist_count': wishlist.get_item_count()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Item already in wishlist'
                })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromWishlistView(LoginRequiredMixin, TemplateView):
    """Remove product from wishlist."""
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please log in'}, status=401)
        
        product_id = request.POST.get('product_id')
        
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            wishlist_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from wishlist',
                'wishlist_count': wishlist.get_item_count()
            })
            
        except (Wishlist.DoesNotExist, WishlistItem.DoesNotExist):
            return JsonResponse({'error': 'Item not found in wishlist'}, status=404)