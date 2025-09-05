from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Product


class HomeView(TemplateView):
    """Simple homepage with featured products."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_featured=True,
            status='active'
        )[:6]
        return context


class ProductListView(ListView):
    """Simple product listing page."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='active')
        
        # Simple search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    """Simple product detail page."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(status='active')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Related products (just other active products)
        context['related_products'] = Product.objects.filter(
            status='active'
        ).exclude(id=product.id)[:4]
        
        # Check if user is authenticated and if item is in cart
        if self.request.user.is_authenticated:
            # Check if product is in user's cart
            from cart.models import CartItem
            context['in_cart'] = CartItem.objects.filter(
                cart__user=self.request.user,
                product=product
            ).exists()
            
            # Get cart item quantity if it exists
            try:
                cart_item = CartItem.objects.get(
                    cart__user=self.request.user,
                    product=product
                )
                context['cart_quantity'] = cart_item.quantity
            except CartItem.DoesNotExist:
                context['cart_quantity'] = 0
        else:
            context['in_cart'] = False
            context['cart_quantity'] = 0
        
        return context