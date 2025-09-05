from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from .models import APIToken


class APIKeyAuthentication(BaseAuthentication):
    """
    API Key authentication using JWT tokens.
    
    Clients should authenticate by passing the JWT token in the Authorization header,
    prepended with the string "Bearer ".  For example:
    
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
    """
    
    keyword = 'Bearer'
    model = APIToken
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        auth_parts = auth_header.split()
        
        if not auth_parts or auth_parts[0].lower() != self.keyword.lower():
            return None
        
        if len(auth_parts) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth_parts) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)
        
        token = auth_parts[1]
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        """
        Authenticate the token and return the user and APIToken instance.
        """
        api_token = APIToken.validate_token(token)
        
        if not api_token:
            raise AuthenticationFailed(_('Invalid token.'))
        
        if not api_token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))
        
        return (api_token.user, api_token)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return f'{self.keyword} realm="api"'