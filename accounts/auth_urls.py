from django.urls import path
from . import auth_views, mfa_views

app_name = 'auth'

urlpatterns = [
    # Basic Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', auth_views.SignupView.as_view(), name='signup'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # MFA Views
    path('mfa/setup/', mfa_views.MFASetupView.as_view(), name='mfa_setup'),
    path('mfa/verify-setup/', mfa_views.MFAVerifySetupView.as_view(), name='mfa_verify_setup'),
    path('mfa/verify/', mfa_views.MFAVerifyView.as_view(), name='mfa_verify'),
    path('mfa/backup-codes/', mfa_views.MFABackupCodesView.as_view(), name='mfa_backup_codes'),
    path('mfa/disable/', mfa_views.MFADisableView.as_view(), name='mfa_disable'),
    path('mfa/regenerate-codes/', mfa_views.MFARegenerateBackupCodesView.as_view(), name='mfa_regenerate_codes'),
    
    # Legacy MFA routes (redirect to new views)
    path('verify-mfa/', mfa_views.MFAVerifyView.as_view(), name='verify_mfa'),
    path('setup-mfa/', mfa_views.MFASetupView.as_view(), name='setup_mfa'),
]