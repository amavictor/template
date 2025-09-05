from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('<uuid:subscription_id>/', views.subscription_detail, name='subscription_detail'),
]