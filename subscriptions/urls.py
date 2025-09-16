from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('api-settings/', views.api_settings, name='api_settings'),
    path('purchase-api-package/', views.purchase_api_package, name='purchase_api_package'),
    path('token/<int:token_id>/', views.token_details, name='token_details'),
    path('<uuid:subscription_id>/', views.subscription_detail, name='subscription_detail'),
]