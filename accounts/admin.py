from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, APIToken

# Hide User and Profile models from admin - only show API tokens


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    """Admin configuration for API Token model - simplified for admin use."""
    
    list_display = ('name', 'user', 'token_length', 'is_active', 'expires_at', 'last_used', 'created_at')
    list_filter = ('is_active', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'name')
    readonly_fields = ('token', 'created_at', 'updated_at', 'last_used')
    
    fieldsets = (
        (_('Token Configuration'), {
            'fields': ('user', 'name', 'token_length', 'is_active', 'expires_at'),
            'description': 'Configure API token settings. Token will be auto-generated.'
        }),
        (_('Generated Token'), {
            'fields': ('token', 'last_used'),
            'classes': ('collapse',),
            'description': 'Auto-generated JWT token for API access.'
        }),
        (_('API Permissions'), {
            'fields': ('can_read_products', 'can_manage_cart', 'can_place_orders', 'can_manage_wishlist'),
            'classes': ('collapse',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Handle JWT token generation on save."""
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)
