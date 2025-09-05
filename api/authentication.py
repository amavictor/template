from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import APIToken


class APITokenAuthentication(BaseAuthentication):
    """
    Custom authentication class for API tokens.
    Checks for Bearer token in Authorization header.
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            auth_parts = auth_header.split()
            
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'bearer':
                return None
            
            token = auth_parts[1]
            
            # Validate token using APIToken model
            api_token = APIToken.validate_token(token)
            
            if not api_token:
                raise AuthenticationFailed('Invalid or expired token.')
            
            return (api_token.user, api_token)
            
        except Exception as e:
            raise AuthenticationFailed('Invalid token format.')
    
    def authenticate_header(self, request):
        return 'Bearer'