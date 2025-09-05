from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class SignupForm(UserCreationForm):
    """Enhanced signup form with email field."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create UserProfile for MFA
            UserProfile.objects.get_or_create(user=user)
        
        return user


class LoginForm(forms.Form):
    """Login form for username/password authentication."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class MFASetupForm(forms.Form):
    """Form for MFA setup verification."""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;',
            'autocomplete': 'off',
            'inputmode': 'numeric'
        }),
        help_text='Enter the 6-digit code from Microsoft Authenticator'
    )


class MFAVerifyForm(forms.Form):
    """Form for MFA verification during login."""
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;',
            'autocomplete': 'off',
            'inputmode': 'numeric'
        }),
        help_text='Enter the 6-digit code from Microsoft Authenticator'
    )
    backup_code = forms.CharField(
        max_length=9,
        min_length=9,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '0000-0000',
            'style': 'font-size: 1.2rem; letter-spacing: 0.2rem;',
            'autocomplete': 'off'
        }),
        help_text='Or use a backup code'
    )


class MFADisableForm(forms.Form):
    """Form to disable MFA."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to disable MFA'
        }),
        help_text='Enter your password to confirm MFA disable'
    )