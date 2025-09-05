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
                        request.session['pre_2fa_user_id'] = user.id
                        return redirect('auth:verify_mfa')
                    else:
                        login(request, user)
                        # Generate JWT token for the user
                        token = self.generate_jwt_token(user)
                        request.session['jwt_token'] = token
                        messages.success(request, 'Welcome back!')
                        return redirect('home')
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
            
            # Auto-login the user after successful registration
            login(request, user)
            # Generate JWT token for the new user
            token = self.generate_jwt_token(user)
            request.session['jwt_token'] = token
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('home')
            
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

class MFAVerificationView(TemplateView):
    template_name = 'accounts/verify_mfa.html'
    
    def dispatch(self, request, *args, **kwargs):
        if 'pre_2fa_user_id' not in request.session:
            return redirect('auth:login')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            user_id = request.session.get('pre_2fa_user_id')
            token = request.POST.get('token')
            
            if not token:
                messages.error(request, 'Please enter a verification code.')
                return render(request, self.template_name)
            
            if not token.isdigit() or len(token) != 6:
                messages.error(request, 'Verification code must be 6 digits.')
                return render(request, self.template_name)
            
            user = User.objects.get(id=user_id)
            profile = user.userprofile
            
            totp = pyotp.TOTP(profile.mfa_secret)
            if totp.verify(token):
                del request.session['pre_2fa_user_id']
                login(request, user)
                # Generate JWT token for the user after MFA verification
                jwt_token = self.generate_jwt_token(user)
                request.session['jwt_token'] = jwt_token
                messages.success(request, 'Successfully logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
                
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('auth:login')
        except Exception as e:
            messages.error(request, 'Verification failed. Please try again.')
            return redirect('auth:login')
            
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

class SetupMFAView(TemplateView):
    template_name = 'accounts/setup_mfa.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        if not profile.mfa_secret:
            profile.mfa_secret = pyotp.random_base32()
            profile.save()
        
        # Generate QR code
        totp = pyotp.TOTP(profile.mfa_secret)
        qr_uri = totp.provisioning_uri(
            name=request.user.email,
            issuer_name='TechMart'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_img = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'secret': profile.mfa_secret,
            'qr_code': qr_code_img
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        token = request.POST.get('token')
        
        try:
            profile = request.user.userprofile
            totp = pyotp.TOTP(profile.mfa_secret)
            
            if totp.verify(token):
                profile.mfa_enabled = True
                profile.save()
                messages.success(request, 'MFA has been enabled successfully!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
            
        return self.get(request)

def logout_view(request):
    logout(request)
    return redirect('home')