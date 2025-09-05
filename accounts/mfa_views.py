import io
import base64
import qrcode
import json
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import UserProfile
from .forms import MFASetupForm, MFAVerifyForm


class MFASetupView(TemplateView):
    """Setup MFA with Microsoft Authenticator."""
    template_name = 'auth/mfa_setup.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated OR has a setup session
        if not request.user.is_authenticated:
            setup_user_id = request.session.get('mfa_setup_user_id')
            if not setup_user_id:
                messages.error(request, 'Invalid session. Please log in.')
                return redirect('auth:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_setup_user(self):
        """Get the user who needs MFA setup."""
        if self.request.user.is_authenticated:
            return self.request.user
        else:
            setup_user_id = self.request.session.get('mfa_setup_user_id')
            if setup_user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    return User.objects.get(id=setup_user_id)
                except User.DoesNotExist:
                    return None
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        setup_user = self.get_setup_user()
        if not setup_user:
            return context
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=setup_user)
        
        # Generate QR code for Microsoft Authenticator
        totp_uri = user_profile.get_totp_uri()
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64 for template
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        context.update({
            'qr_code_base64': qr_code_base64,
            'secret_key': user_profile.mfa_secret,
            'app_name': 'TechMart',
            'user_email': setup_user.email or setup_user.username,
            'mfa_enabled': user_profile.mfa_enabled,
            'setup_user': setup_user,
        })
        
        return context


class MFAVerifySetupView(View):
    """Verify MFA setup with test code."""
    
    def get_setup_user(self, request):
        """Get the user who is setting up MFA."""
        if request.user.is_authenticated:
            return request.user
        else:
            setup_user_id = request.session.get('mfa_setup_user_id')
            if setup_user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    return User.objects.get(id=setup_user_id)
                except User.DoesNotExist:
                    return None
        return None
    
    def post(self, request, *args, **kwargs):
        setup_user = self.get_setup_user(request)
        if not setup_user:
            messages.error(request, 'Invalid session. Please log in.')
            return redirect('auth:login')
        
        user_profile, created = UserProfile.objects.get_or_create(user=setup_user)
        verification_code = request.POST.get('verification_code', '').strip()
        
        if not verification_code:
            messages.error(request, 'Please enter the verification code.')
            return redirect('auth:mfa_setup')
        
        # Verify the code
        if user_profile.verify_totp(verification_code):
            # Enable MFA
            user_profile.mfa_enabled = True
            user_profile.save()
            
            # Generate backup codes
            backup_codes = user_profile.generate_backup_codes()
            
            # Store backup codes in session to show them once
            request.session['mfa_backup_codes'] = backup_codes
            
            # Complete the login process after MFA setup
            if not request.user.is_authenticated:
                from django.contrib.auth import login
                from .auth_views import LoginView
                
                # Log the user in
                login(request, setup_user)
                
                # Generate JWT token
                login_view = LoginView()
                jwt_token = login_view.generate_jwt_token(setup_user)
                
                # Store token
                request.session['jwt_token'] = jwt_token
                
                # Clear setup session
                request.session.pop('mfa_setup_user_id', None)
                
                messages.success(request, f'MFA enabled successfully! Welcome, {setup_user.get_full_name() or setup_user.username}!')
            else:
                messages.success(request, 'MFA has been successfully enabled!')
            
            return redirect('auth:mfa_backup_codes')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return redirect('auth:mfa_setup')


class MFABackupCodesView(LoginRequiredMixin, TemplateView):
    """Show backup codes after MFA setup."""
    template_name = 'auth/mfa_backup_codes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get backup codes from session (only shown once)
        backup_codes = self.request.session.pop('mfa_backup_codes', None)
        context['backup_codes'] = backup_codes
        
        return context


class MFAVerifyView(View):
    """Verify MFA code during login."""
    template_name = 'auth/mfa_verify.html'
    
    def get(self, request, *args, **kwargs):
        # Check if user is in MFA verification state
        if not request.session.get('mfa_user_id'):
            messages.error(request, 'Invalid MFA session.')
            return redirect('auth:login')
        
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('mfa_user_id')
        if not user_id:
            messages.error(request, 'Invalid MFA session.')
            return redirect('auth:login')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'Invalid MFA session.')
            return redirect('auth:login')
        
        verification_code = request.POST.get('verification_code', '').strip()
        backup_code = request.POST.get('backup_code', '').strip()
        
        # Try TOTP code first
        if verification_code and user_profile.verify_totp(verification_code):
            return self._complete_mfa_login(request, user)
        
        # Try backup code
        elif backup_code and user_profile.verify_backup_code(backup_code):
            messages.warning(request, 'You used a backup code. Consider generating new backup codes.')
            return self._complete_mfa_login(request, user)
        
        else:
            messages.error(request, 'Invalid verification code or backup code.')
            return render(request, self.template_name)
    
    def _complete_mfa_login(self, request, user):
        """Complete MFA login and issue JWT token."""
        from django.contrib.auth import login
        from .auth_views import LoginView
        
        # Clear MFA session
        request.session.pop('mfa_user_id', None)
        
        # Log user in
        login(request, user)
        
        # Generate JWT token
        login_view = LoginView()
        jwt_token = login_view.generate_jwt_token(user)
        
        # Store token and user data
        response = redirect('home')
        response.set_cookie('jwt_token', jwt_token, max_age=86400, httponly=True)
        
        # Store user data in localStorage via template
        request.session['login_success'] = {
            'token': jwt_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }
        
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return response


class MFADisableView(LoginRequiredMixin, View):
    """Disable MFA for user account."""
    
    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Verify password before disabling MFA
            password = request.POST.get('password')
            if not request.user.check_password(password):
                messages.error(request, 'Invalid password.')
                return redirect('auth:mfa_setup')
            
            # Disable MFA
            user_profile.mfa_enabled = False
            user_profile.mfa_secret = ''
            user_profile.mfa_backup_codes = ''
            user_profile.save()
            
            messages.success(request, 'MFA has been disabled.')
            return redirect('auth:mfa_setup')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'MFA profile not found.')
            return redirect('auth:mfa_setup')


class MFARegenerateBackupCodesView(LoginRequiredMixin, View):
    """Regenerate backup codes."""
    
    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            if not user_profile.mfa_enabled:
                messages.error(request, 'MFA is not enabled.')
                return redirect('auth:mfa_setup')
            
            # Verify password
            password = request.POST.get('password')
            if not request.user.check_password(password):
                messages.error(request, 'Invalid password.')
                return redirect('auth:mfa_setup')
            
            # Generate new backup codes
            backup_codes = user_profile.generate_backup_codes()
            
            # Store in session to show once
            request.session['mfa_backup_codes'] = backup_codes
            
            messages.success(request, 'New backup codes generated!')
            return redirect('auth:mfa_backup_codes')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'MFA profile not found.')
            return redirect('auth:mfa_setup')