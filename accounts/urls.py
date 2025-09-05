from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'accounts'

# API URLs
api_urlpatterns = [
    path('tokens/', api_views.APITokenListCreateView.as_view(), name='api_token_list_create'),
    path('tokens/<int:pk>/', api_views.APITokenDetailView.as_view(), name='api_token_detail'),
    path('tokens/<int:pk>/regenerate/', api_views.regenerate_api_token, name='api_token_regenerate'),
    path('tokens/<int:pk>/toggle/', api_views.toggle_api_token, name='api_token_toggle'),
]

urlpatterns = [
    # User dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # API Token management (web interface)
    path('api-tokens/', views.api_tokens, name='api_tokens'),
    path('api-tokens/create/', views.create_api_token, name='create_api_token'),
    path('api-tokens/<int:token_id>/delete/', views.delete_api_token, name='delete_api_token'),
    path('api-tokens/<int:token_id>/regenerate/', views.regenerate_api_token, name='regenerate_api_token'),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
]