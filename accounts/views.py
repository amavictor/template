from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import APIToken
import secrets
import json


@login_required
def dashboard(request):
    """User dashboard with account overview and API tokens."""
    user_tokens = APIToken.objects.filter(user=request.user).order_by('-created_at')
    
    # Count active vs expired tokens
    active_tokens = user_tokens.filter(expires_at__gt=timezone.now())
    expired_tokens = user_tokens.filter(expires_at__lte=timezone.now())
    
    context = {
        'user': request.user,
        'api_tokens': user_tokens[:10],  # Show last 10 tokens
        'active_token_count': active_tokens.count(),
        'expired_token_count': expired_tokens.count(),
        'total_token_count': user_tokens.count(),
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    """User profile management page."""
    if request.method == 'POST':
        # Handle profile updates
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')


@login_required
def api_tokens(request):
    """API token management page."""
    user_tokens = APIToken.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'api_tokens': user_tokens,
        'active_tokens': user_tokens.filter(expires_at__gt=timezone.now()),
        'expired_tokens': user_tokens.filter(expires_at__lte=timezone.now()),
    }
    
    return render(request, 'accounts/api_tokens.html', context)


@login_required
@require_POST
def create_api_token(request):
    """Create a new API token for the user."""
    try:
        data = json.loads(request.body)
        token_name = data.get('name', '').strip()
        expires_in_days = data.get('expires_in_days', None)
        
        if not token_name:
            return JsonResponse({'error': 'Token name is required'}, status=400)
        
        # Check if user already has a token with this name
        if APIToken.objects.filter(user=request.user, name=token_name).exists():
            return JsonResponse({'error': 'Token with this name already exists'}, status=400)
        
        # Limit number of active tokens per user
        active_tokens = APIToken.objects.filter(
            user=request.user, 
            is_active=True
        ).count()
        
        if active_tokens >= 10:  # Max 10 active tokens
            return JsonResponse({
                'error': 'Maximum number of active tokens reached (10). Please delete some expired tokens.'
            }, status=400)
        
        expires_at = None
        if expires_in_days:
            expires_in_days = int(expires_in_days)
            if expires_in_days < 1 or expires_in_days > 365:
                return JsonResponse({'error': 'Expiry must be between 1 and 365 days'}, status=400)
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Create the token (JWT will be generated automatically)
        api_token = APIToken.objects.create(
            user=request.user,
            name=token_name,
            expires_at=expires_at
        )
        
        return JsonResponse({
            'success': True,
            'token': {
                'id': api_token.id,
                'name': api_token.name,
                'key': api_token.token,  # JWT token - only show on creation
                'expires_at': api_token.expires_at.isoformat() if api_token.expires_at else None,
                'created_at': api_token.created_at.isoformat(),
            },
            'message': 'API token created successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required
@require_POST
def delete_api_token(request, token_id):
    """Delete an API token."""
    try:
        token = get_object_or_404(APIToken, id=token_id, user=request.user)
        token_name = token.name
        token.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Token "{token_name}" deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required 
@require_POST
def regenerate_api_token(request, token_id):
    """Regenerate an API token (creates new JWT token)."""
    try:
        old_token = get_object_or_404(APIToken, id=token_id, user=request.user)
        
        # Clear the old token to force regeneration of JWT
        old_token.token = ''
        old_token.created_at = timezone.now()
        old_token.save()  # This will trigger JWT regeneration
        
        return JsonResponse({
            'success': True,
            'token': {
                'id': old_token.id,
                'name': old_token.name,
                'key': old_token.token,  # Show new JWT token
                'expires_at': old_token.expires_at.isoformat() if old_token.expires_at else None,
                'created_at': old_token.created_at.isoformat(),
            },
            'message': 'API token regenerated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)
