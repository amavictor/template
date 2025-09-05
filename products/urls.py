from django.urls import path
from . import simple_views

app_name = 'products'

urlpatterns = [
    # Product listings
    path('', simple_views.ProductListView.as_view(), name='product_list'),
    
    # Product details
    path('<int:pk>/', simple_views.ProductDetailView.as_view(), name='product_detail'),
]