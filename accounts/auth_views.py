from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
import pyotp
import qrcode
import io
import base64
import jwt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import User, UserProfile

class LoginView(TemplateView):
    template_name = 'accounts/login.html'
    
    def post(self, request):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"Login attempt: username='{username}', password='{password}'")
            
            if not username or not password:
                messages.error(request, 'Please enter both username and password.')
                return render(request, self.template_name)
            
            # Check if user exists
            try:
                user_exists = User.objects.get(username=username)
                print(f"User found: {user_exists.username}, is_active: {user_exists.is_active}")
            except User.DoesNotExist:
                print(f"User with username '{username}' does not exist")
                messages.error(request, 'Invalid username or password.')
                return render(request, self.template_name)
            
            user = authenticate(request, username=username, password=password)
            print(f"Authentication result: {user}")
            
            if user is not None:
                # Check if user has MFA enabled
                try:
                    profile = user.userprofile
                    if profile.mfa_enabled:
                        # Store user ID for MFA verification step
                        request.session['mfa_user_id'] = user.id
                        return redirect('auth:mfa_verify')
                    else:
                        # If MFA is not enabled, redirect to setup MFA first
                        request.session['mfa_setup_user_id'] = user.id
                        messages.info(request, 'Please set up two-factor authentication to secure your account.')
                        return redirect('auth:mfa_setup')
                except UserProfile.DoesNotExist:
                    login(request, user)
                    # Generate JWT token for the user
                    token = self.generate_jwt_token(user)
                    request.session['jwt_token'] = token
                    messages.success(request, 'Welcome back!')
                    return redirect('home')
                except Exception as e:
                    print(f"Exception during login: {e}")
                    messages.error(request, 'An error occurred during login. Please try again.')
                    return render(request, self.template_name)
            else:
                print("Authentication failed - user is None")
                messages.error(request, 'Invalid username or password.')
                
        except Exception as e:
            print(f"Login exception: {e}")
            messages.error(request, 'Login failed. Please try again.')
            
        return render(request, self.template_name)
    
    def generate_jwt_token(self, user):
        """Generate a JWT token for the authenticated user."""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'iat': int(timezone.now().timestamp()),
            'exp': int((timezone.now() + timedelta(hours=24)).timestamp())  # 24 hour expiry
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

class SignupView(TemplateView):
    template_name = 'accounts/signup.html'
    
    def post(self, request):
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            # Validation
            if not all([username, email, password, password_confirm]):
                messages.error(request, 'All fields are required.')
                return render(request, self.template_name)
            
            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, self.template_name)
            
            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, self.template_name)
                
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return render(request, self.template_name)
                
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, self.template_name)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create UserProfile for MFA
            UserProfile.objects.get_or_create(user=user)
            
            # Redirect to MFA setup (mandatory for new users)
            request.session['mfa_setup_user_id'] = user.id
            messages.success(request, 'Account created successfully! Now set up two-factor authentication to secure your account.')
            return redirect('auth:mfa_setup')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, self.template_name)
    
    def generate_jwt_token(self, user):
        """Generate a JWT token for the authenticated user."""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'iat': int(timezone.now().timestamp()),
            'exp': int((timezone.now() + timedelta(hours=24)).timestamp())  # 24 hour expiry
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# MFA verification is now handled by mfa_views.py MFAVerifyView
# This class is kept for compatibility but redirects to the new view
    
    def generate_jwt_token(self, user):
        """Generate a JWT token for the authenticated user."""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'iat': int(timezone.now().timestamp()),
            'exp': int((timezone.now() + timedelta(hours=24)).timestamp())  # 24 hour expiry
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# MFA setup is now handled by mfa_views.py MFASetupView  
# This class is kept for compatibility but should redirect to new views

def logout_view(request):
    logout(request)
    return redirect('home')