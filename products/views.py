from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Product, Category, Review


class HomeView(TemplateView):
    """Homepage with featured products and company info."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_featured=True,
            status='active'
        )[:6]
        context['desalination_units'] = Product.objects.filter(
            product_type='desalination_unit',
            status='active'
        )[:3]
        context['data_subscriptions'] = Product.objects.filter(
            product_type='data_subscription',
            status='active'
        )[:3]
        return context


class ProductListView(ListView):
    """Product listing page with search and filtering."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='active')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        # Category filtering
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Product type filtering
        product_type = self.request.GET.get('type')
        if product_type in ['desalination_unit', 'data_subscription']:
            queryset = queryset.filter(product_type=product_type)
        
        # Price filtering
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['name', '-name', 'price', '-price', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_type'] = self.request.GET.get('type', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Product detail page with specifications and reviews."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(status='active')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get reviews
        context['reviews'] = Review.objects.filter(
            product=product,
            is_approved=True
        ).order_by('-created_at')
        
        # Calculate average rating
        reviews = context['reviews']
        if reviews:
            context['average_rating'] = sum(r.rating for r in reviews) / len(reviews)
            context['rating_distribution'] = {
                5: reviews.filter(rating=5).count(),
                4: reviews.filter(rating=4).count(),
                3: reviews.filter(rating=3).count(),
                2: reviews.filter(rating=2).count(),
                1: reviews.filter(rating=1).count(),
            }
        
        # Related products - simplified without category filtering
        context['related_products'] = Product.objects.filter(
            status='active'
        ).exclude(id=product.id)[:4]
        
        # Check if user can review and if item is in cart
        if self.request.user.is_authenticated:
            context['can_review'] = not Review.objects.filter(
                product=product,
                user=self.request.user
            ).exists()
            
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
        
        return context


class CategoryProductsView(ListView):
    """Products filtered by category."""
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_active=True
        )
        return Product.objects.filter(
            category=self.category,
            status='active'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class AddReviewView(LoginRequiredMixin, TemplateView):
    """Add a product review (AJAX endpoint)."""
    
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if not all([product_id, rating, comment]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id, status='active')
            rating = int(rating)
            
            if not 1 <= rating <= 5:
                return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
            
            # Check if user already reviewed this product
            if Review.objects.filter(product=product, user=request.user).exists():
                return JsonResponse({'error': 'You have already reviewed this product'}, status=400)
            
            # Create review
            review = Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                title=title,
                comment=comment
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Review submitted successfully! It will be visible after approval.'
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid rating value'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)


def search_suggestions(request):
    """AJAX endpoint for search autocomplete."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(short_description__icontains=query),
        status='active'
    )[:10]
    
    suggestions = [
        {
            'name': product.name,
            'url': product.get_absolute_url(),
            'price': str(product.price),
            'image': product.main_image.url if product.main_image else None
        }
        for product in products
    ]
    
    return JsonResponse({'suggestions': suggestions})
