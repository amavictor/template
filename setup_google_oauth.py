#!/usr/bin/env python3
"""
Setup script for Google OAuth configuration in Django allauth.
This script creates the necessary SocialApplication for Google OAuth.
"""

import os
import sys
import django
from decouple import config

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluewave_ecommerce.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


def setup_google_oauth():
    print("🔐 Setting up Google OAuth for TechMart...")
    
    # Get or create the site
    site, created = Site.objects.get_or_create(
        pk=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'TechMart Development'
        }
    )
    
    if created:
        print("✅ Created default site for development")
    else:
        print("✅ Using existing site configuration")
    
    # Get Google OAuth credentials from environment
    client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default='')
    client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
    
    if not client_id or client_id == 'your_google_client_id':
        print("⚠️  WARNING: Google OAuth Client ID not configured")
        print("📝 To enable Google OAuth, follow these steps:")
        print()
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable Google+ API")
        print("4. Go to 'Credentials' and create OAuth 2.0 Client IDs")
        print("5. Add these authorized redirect URIs:")
        print("   - http://localhost:8000/accounts/google/login/callback/")
        print("   - http://127.0.0.1:8000/accounts/google/login/callback/")
        print("6. Update your .env file with:")
        print("   GOOGLE_OAUTH2_CLIENT_ID=your_actual_client_id")
        print("   GOOGLE_OAUTH2_CLIENT_SECRET=your_actual_client_secret")
        print()
        
        # Create a placeholder social app anyway for development
        client_id = 'placeholder_client_id'
        client_secret = 'placeholder_client_secret'
        print("🔧 Creating placeholder Google OAuth app (won't work until configured)")
    
    if not client_secret or client_secret == 'your_google_client_secret':
        print("⚠️  WARNING: Google OAuth Client Secret not configured")
        client_secret = 'placeholder_client_secret'
    
    # Create or update Google Social Application
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google OAuth2',
            'client_id': client_id,
            'secret': client_secret,
        }
    )
    
    if not created:
        # Update existing app
        google_app.client_id = client_id
        google_app.secret = client_secret
        google_app.save()
        print("✅ Updated existing Google OAuth application")
    else:
        print("✅ Created new Google OAuth application")
    
    # Add the site to the social application
    google_app.sites.clear()
    google_app.sites.add(site)
    print("✅ Associated Google OAuth with site")
    
    print("\n🎉 Google OAuth setup completed!")
    
    if client_id != 'placeholder_client_id':
        print("✅ Google OAuth is ready to use")
        print("🌐 Users can now sign in with Google at: http://localhost:8000/accounts/login/")
    else:
        print("⚠️  Remember to configure actual Google OAuth credentials in .env file")
        print("📚 Visit Django allauth documentation for more details:")
        print("   https://django-allauth.readthedocs.io/en/latest/providers.html#google")
    
    print("\n🔑 Test accounts available:")
    print("• admin@bluewave.com / admin123")
    print("• customer@example.com / demo123")
    print("• developer@example.com / dev123")


if __name__ == '__main__':
    setup_google_oauth()