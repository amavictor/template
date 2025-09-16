from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from accounts.models import APIToken
from subscriptions.models import UserAPIToken


class APITokenAuthentication(JWTAuthentication):
    """
    Custom authentication class for API tokens.
    Supports both JWT tokens from accounts app and subscription-based JWT tokens.
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Handle both "Bearer <token>" formats
            auth_parts = auth_header.split()
            
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'bearer':
                return None
            
            token = auth_parts[1]
            
            # First try to authenticate as a regular JWT token
            try:
                validated_token = UntypedToken(token)
                user = self.get_user(validated_token)
                
                # Check if this is a subscription token
                try:
                    user_api_token = UserAPIToken.objects.get(
                        token_key=token,
                        user=user,
                        status='active'
                    )
                    
                    if user_api_token.is_valid():
                        # Track API usage for subscription tokens
                        user_api_token.increment_usage()
                        return (user, user_api_token)
                    else:
                        raise AuthenticationFailed('Subscription token has expired.')
                        
                except UserAPIToken.DoesNotExist:
                    # Regular JWT token, not a subscription token
                    pass
                
                # Try legacy JWT token from accounts app
                try:
                    api_token = APIToken.validate_token(token)
                    if api_token:
                        return (api_token.user, api_token)
                except:
                    pass
                
                # Default JWT authentication
                return (user, validated_token)
                
            except (InvalidToken, TokenError):
                # Try legacy JWT token from accounts app as fallback
                try:
                    api_token = APIToken.validate_token(token)
                    if api_token:
                        return (api_token.user, api_token)
                except:
                    pass
                
                raise AuthenticationFailed('Invalid or expired token.')
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            raise AuthenticationFailed('Invalid token format.')
    
    def authenticate_header(self, request):
        return 'Bearer'