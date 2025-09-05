# Google OAuth Setup Guide

This guide explains how to configure Google OAuth authentication for your TechMart Django application.

## Prerequisites

The application is already configured to use Google OAuth with django-allauth. You just need to obtain credentials from Google Cloud Console.

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Make note of your project ID

### 2. Enable Google APIs

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Google+ API** (for basic profile info)
   - **Google Identity and Access Management (IAM) API**

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the application name: "TechMart"
   - Add your email as a developer email
   - Add scopes: `email`, `profile`, `openid`

4. For the OAuth 2.0 Client ID:
   - Application type: "Web application"
   - Name: "TechMart Django App"
   - Authorized JavaScript origins:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`

### 4. Configure Environment Variables

1. Copy your Client ID and Client Secret from Google Cloud Console
2. Update your `.env` file:

```env
GOOGLE_OAUTH2_CLIENT_ID=your_actual_client_id_here
GOOGLE_OAUTH2_CLIENT_SECRET=your_actual_client_secret_here
```

### 5. Update Social Application (Optional)

If you need to update the credentials after setup, run:

```bash
source bluewave_env/bin/activate
python setup_google_oauth.py
```

## Testing Google OAuth

1. Start your Django development server:
   ```bash
   source bluewave_env/bin/activate
   python manage.py runserver
   ```

2. Navigate to: `http://localhost:8000/accounts/login/`

3. Click the "Continue with Google" button

4. You should be redirected to Google's OAuth consent screen

5. After authorization, you'll be redirected back to your application

## Troubleshooting

### Common Issues

1. **"Error 400: redirect_uri_mismatch"**
   - Ensure your redirect URIs in Google Cloud Console exactly match the ones listed above
   - Check that you're accessing the site via the same domain (localhost vs 127.0.0.1)

2. **"OAuth consent screen needs verification"**
   - For development, add yourself as a test user in the OAuth consent screen
   - For production, submit your app for verification

3. **"Access blocked: This app's request is invalid"**
   - Make sure you've enabled the required APIs in Google Cloud Console
   - Check that your OAuth consent screen is properly configured

### Development vs Production

**Development:**
- Use `http://localhost:8000` and `http://127.0.0.1:8000`
- Add yourself as a test user in OAuth consent screen
- No need for app verification

**Production:**
- Use your actual domain (e.g., `https://yourdomain.com`)
- Update redirect URIs to use HTTPS
- Submit app for verification if needed
- Consider using environment-specific .env files

## Security Notes

- Never commit your actual Client ID and Secret to version control
- Use environment variables for all sensitive configuration
- In production, use HTTPS for all OAuth callbacks
- Regularly rotate your OAuth credentials

## Additional Resources

- [Django-allauth Google Provider Documentation](https://django-allauth.readthedocs.io/en/latest/providers.html#google)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

## Support

If you encounter issues with Google OAuth setup, check:
1. Django logs for detailed error messages
2. Google Cloud Console logs
3. Browser developer tools for network errors
4. Django-allauth documentation for provider-specific issues