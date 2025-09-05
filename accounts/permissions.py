from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedForUnsafeMethods(BasePermission):
    """
    Custom permission that allows:
    - Anyone to read (GET, HEAD, OPTIONS)
    - Only authenticated users for unsafe methods (POST, PUT, PATCH, DELETE)
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to authenticated users.
        return request.user and request.user.is_authenticated


class CanManageCart(BasePermission):
    """
    Permission for cart management operations.
    Requires authentication and cart management permission.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is authenticated via API key
        if hasattr(request, 'auth') and hasattr(request.auth, 'can_manage_cart'):
            return request.auth.can_manage_cart
        
        # Allow if authenticated via session/JWT
        return True


class CanPlaceOrders(BasePermission):
    """
    Permission for order placement operations.
    Requires authentication and order placement permission.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is authenticated via API key
        if hasattr(request, 'auth') and hasattr(request.auth, 'can_place_orders'):
            return request.auth.can_place_orders
        
        # Allow if authenticated via session/JWT
        return True


class CanManageWishlist(BasePermission):
    """
    Permission for wishlist management operations.
    Requires authentication and wishlist management permission.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is authenticated via API key
        if hasattr(request, 'auth') and hasattr(request.auth, 'can_manage_wishlist'):
            return request.auth.can_manage_wishlist
        
        # Allow if authenticated via session/JWT
        return True


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user,
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_authenticated and request.user.is_admin_user()


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object or admin.
        return obj.user == request.user or (request.user and request.user.is_admin_user())


class GuestUserRestriction(BasePermission):
    """
    Restricts guest users from performing certain actions.
    Guest users can browse products but cannot add to cart, wishlist, or purchase.
    """
    
    def has_permission(self, request, view):
        # Allow all safe methods (GET, HEAD, OPTIONS) for guests
        if request.method in SAFE_METHODS:
            return True
        
        # For unsafe methods, require authentication
        if not request.user or not request.user.is_authenticated:
            self.message = "You must be logged in to perform this action. Please sign in with Google."
            return False
        
        return True