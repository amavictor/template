from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user with username and password."""
        if not username:
            raise ValueError('The Username field must be set')
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(
            username=username,
            email=email or '',
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser with username and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for BlueWave Solutions.
    Extends Django's AbstractUser to add custom fields.
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('customer', 'Customer'),
    )
    
    email = models.EmailField(_('email address'), blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer',
        help_text=_('Designates the type of user.')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Phone number for contact purposes.')
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Company name for business customers.')
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Use username as primary field
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def is_admin_user(self):
        """Check if user is an administrator."""
        return self.user_type == 'admin' or self.is_superuser
    
    def is_customer_user(self):
        """Check if user is a customer."""
        return self.user_type == 'customer'
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class UserProfile(models.Model):
    """
    User profile for MFA and additional settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    mfa_backup_codes = models.TextField(blank=True, help_text=_('JSON array of backup codes'))
    
    def __str__(self):
        return f'{self.user.email} Profile'
    
    def generate_mfa_secret(self):
        """Generate a new MFA secret key."""
        import pyotp
        self.mfa_secret = pyotp.random_base32()
        self.save()
        return self.mfa_secret
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation."""
        import pyotp
        if not self.mfa_secret:
            self.generate_mfa_secret()
        
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name="TechMart"
        )
    
    def verify_totp(self, token):
        """Verify TOTP token."""
        import pyotp
        if not self.mfa_secret:
            return False
        
        totp = pyotp.TOTP(self.mfa_secret)
        # Allow for 1 period of clock skew (30 seconds before/after)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self):
        """Generate backup codes for MFA."""
        import secrets
        import json
        
        codes = []
        for _ in range(8):
            code = '-'.join([
                ''.join(secrets.choice('0123456789') for _ in range(4)),
                ''.join(secrets.choice('0123456789') for _ in range(4))
            ])
            codes.append(code)
        
        self.mfa_backup_codes = json.dumps(codes)
        self.save()
        return codes
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code."""
        import json
        
        if not self.mfa_backup_codes:
            return False
        
        try:
            codes = json.loads(self.mfa_backup_codes)
            if code in codes:
                codes.remove(code)
                self.mfa_backup_codes = json.dumps(codes)
                self.save()
                return True
        except (json.JSONDecodeError, ValueError):
            pass
        
        return False
    
    class Meta:
        db_table = 'accounts_userprofile'


class Profile(models.Model):
    """
    Extended user profile for additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('Brief description about the user.')
    )
    address = models.TextField(
        blank=True,
        help_text=_('User\'s address for shipping purposes.')
    )
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Profile picture.')
    )
    birth_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True, help_text=_('Personal or company website.'))
    
    # Preferences
    newsletter_subscription = models.BooleanField(
        default=True,
        help_text=_('Subscribe to newsletter updates.')
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications.')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.email} Profile'
    
    class Meta:
        db_table = 'accounts_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class APIToken(models.Model):
    """
    Model for storing API tokens for ecommerce API access.
    Users can create and manage their own tokens.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens')
    name = models.CharField(
        max_length=100,
        help_text=_('Descriptive name for this token.')
    )
    token = models.CharField(
        max_length=500,  # Increased length for longer tokens
        unique=True,
        help_text=_('The actual JWT token string.')
    )
    token_length = models.IntegerField(
        default=32,
        help_text=_('Custom token length (characters). Min: 16, Max: 128.')
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Token expiration date. Leave blank for no expiration.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Last time this token was used.')
    )
    
    # Token permissions for ecommerce operations
    can_read_products = models.BooleanField(
        default=True,
        help_text=_('Permission to read product data.')
    )
    can_manage_cart = models.BooleanField(
        default=True,
        help_text=_('Permission to manage shopping cart.')
    )
    can_place_orders = models.BooleanField(
        default=True,
        help_text=_('Permission to place orders.')
    )
    can_manage_wishlist = models.BooleanField(
        default=True,
        help_text=_('Permission to manage wishlist.')
    )
    
    def __str__(self):
        return f'{self.user.email} - {self.name}'
    
    def is_expired(self):
        """Check if token is expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def generate_jwt_token(self):
        """Generate a JWT token for this API key."""
        import jwt
        import secrets
        import string
        from django.conf import settings
        from django.utils import timezone
        
        # Generate a random token with custom length
        alphabet = string.ascii_letters + string.digits
        random_token = ''.join(secrets.choice(alphabet) for _ in range(min(max(self.token_length, 16), 128)))
        
        payload = {
            'api_key_id': self.id,
            'user_id': self.user.id,
            'user_email': self.user.email,
            'token_name': self.name,
            'random_token': random_token,
            'iat': int(timezone.now().timestamp()),
        }
        
        if self.expires_at:
            payload['exp'] = int(self.expires_at.timestamp())
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def save(self, *args, **kwargs):
        """Override save to generate JWT token if not exists."""
        if not self.token:
            super().save(*args, **kwargs)  # Save first to get ID
            self.token = self.generate_jwt_token()
            super().save(update_fields=['token'])
        else:
            super().save(*args, **kwargs)
    
    @classmethod
    def validate_token(cls, token_string):
        """Validate a JWT token and return the associated APIToken instance."""
        import jwt
        from django.conf import settings
        from django.utils import timezone
        
        try:
            payload = jwt.decode(token_string, settings.SECRET_KEY, algorithms=['HS256'])
            api_key_id = payload.get('api_key_id')
            
            if not api_key_id:
                return None
            
            api_token = cls.objects.select_related('user').get(
                id=api_key_id,
                is_active=True
            )
            
            if api_token.is_expired():
                return None
            
            # Update last used timestamp
            api_token.last_used = timezone.now()
            api_token.save(update_fields=['last_used'])
            
            return api_token
            
        except (jwt.InvalidTokenError, cls.DoesNotExist):
            return None
    
    class Meta:
        db_table = 'accounts_apitoken'
        verbose_name = _('API Token')
        verbose_name_plural = _('API Tokens')
        ordering = ['-created_at']
