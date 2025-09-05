"""
URL configuration for BlueWave Solutions eCommerce platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.simple_views import HomeView

# Import admin customization
from . import admin as custom_admin

urlpatterns = [
    # Main site
    path('', HomeView.as_view(), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('auth/', include('accounts.auth_urls')),
    
    # Apps
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('my-account/', include('accounts.urls')),
    
    # API
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
