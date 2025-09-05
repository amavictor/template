from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular import openapi


class APITokenSchema(AutoSchema):
    """Schema for API Token operations with proper documentation."""
    
    def get_operation_id(self, path, method):
        """Generate operation IDs for API token endpoints."""
        if 'tokens' in path:
            if method.lower() == 'get' and path.endswith('tokens/'):
                return 'listAPITokens'
            elif method.lower() == 'post' and path.endswith('tokens/'):
                return 'createAPIToken'
            elif method.lower() == 'get' and not path.endswith('tokens/'):
                return 'getAPIToken'
            elif method.lower() == 'put':
                return 'updateAPIToken'
            elif method.lower() == 'patch':
                return 'partialUpdateAPIToken'
            elif method.lower() == 'delete':
                return 'deleteAPIToken'
        return super().get_operation_id(path, method)


# Schema decorators for different endpoints
list_api_tokens_schema = extend_schema(
    operation_id='listAPITokens',
    description='List all API tokens for the authenticated user',
    summary='List API tokens',
    tags=['API Tokens'],
    responses={
        200: 'List of API tokens',
        401: 'Authentication required',
    },
    examples=[
        OpenApiExample(
            'API Token List Response',
            value=[
                {
                    "id": 1,
                    "name": "My App Token",
                    "is_active": True,
                    "expires_at": "2024-12-31T23:59:59Z",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_used": "2024-01-15T10:30:00Z",
                    "is_expired": False,
                    "is_valid": True,
                    "days_until_expiry": 350,
                    "can_read_products": True,
                    "can_manage_cart": True,
                    "can_place_orders": True,
                    "can_manage_wishlist": True
                }
            ]
        )
    ]
)

create_api_token_schema = extend_schema(
    operation_id='createAPIToken',
    description='Create a new API token for the authenticated user',
    summary='Create API token',
    tags=['API Tokens'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Descriptive name for the token',
                    'example': 'My Mobile App'
                },
                'expires_in_days': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 365,
                    'description': 'Number of days until token expires (optional)',
                    'example': 30
                },
                'can_read_products': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Permission to read product data'
                },
                'can_manage_cart': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Permission to manage shopping cart'
                },
                'can_place_orders': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Permission to place orders'
                },
                'can_manage_wishlist': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Permission to manage wishlist'
                }
            },
            'required': ['name']
        }
    },
    responses={
        201: {
            'description': 'API token created successfully',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "name": "My Mobile App",
                        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "is_active": True,
                        "expires_at": "2024-02-01T00:00:00Z",
                        "created_at": "2024-01-01T00:00:00Z",
                        "last_used": None,
                        "is_expired": False,
                        "is_valid": True,
                        "days_until_expiry": 31,
                        "can_read_products": True,
                        "can_manage_cart": True,
                        "can_place_orders": True,
                        "can_manage_wishlist": True
                    }
                }
            }
        },
        400: 'Invalid request data',
        401: 'Authentication required',
    }
)

regenerate_api_token_schema = extend_schema(
    operation_id='regenerateAPIToken',
    description='Regenerate an existing API token (creates new JWT)',
    summary='Regenerate API token',
    tags=['API Tokens'],
    responses={
        200: {
            'description': 'API token regenerated successfully',
            'content': {
                'application/json': {
                    'example': {
                        "message": "API token regenerated successfully",
                        "token": {
                            "id": 1,
                            "name": "My Mobile App",
                            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "is_active": True,
                            "expires_at": "2024-02-01T00:00:00Z",
                            "created_at": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            }
        },
        404: 'Token not found',
        401: 'Authentication required',
    }
)