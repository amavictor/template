from django.urls import path
from . import views, payment_views, debug_views

app_name = 'orders'

urlpatterns = [
    # Simple Checkout Flow
    path('checkout/', payment_views.CheckoutView.as_view(), name='checkout'),
    path('checkout/success/', payment_views.CheckoutSuccessView.as_view(), name='checkout_success'),
    path('confirmation/<uuid:order_id>/', payment_views.OrderConfirmationView.as_view(), name='order_confirmation'),
    
    # Order Management
    path('', payment_views.OrderListView.as_view(), name='order_list'),
    path('<uuid:order_id>/', payment_views.OrderDetailView.as_view(), name='order_detail'),
    
    # Optional Webhooks (not needed for basic flow)
    path('stripe/webhook/', payment_views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # Legacy URLs (keep for compatibility)
    path('history/', views.order_history, name='order_history'),
]