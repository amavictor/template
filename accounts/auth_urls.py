from django.urls import path
from . import auth_views

app_name = 'auth'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', auth_views.SignupView.as_view(), name='signup'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('verify-mfa/', auth_views.MFAVerificationView.as_view(), name='verify_mfa'),
    path('setup-mfa/', auth_views.SetupMFAView.as_view(), name='setup_mfa'),
]