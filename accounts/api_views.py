from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from .models import APIToken
from .serializers import APITokenSerializer, CreateAPITokenSerializer
from .schema import list_api_tokens_schema, create_api_token_schema, regenerate_api_token_schema


class APITokenListCreateView(generics.ListCreateAPIView):
    """
    List user's API tokens or create a new one.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = APITokenSerializer
    
    @list_api_tokens_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @create_api_token_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        return APIToken.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAPITokenSerializer
        return APITokenSerializer
    
    def perform_create(self, serializer):
        # Check token limit
        active_tokens = APIToken.objects.filter(
            user=self.request.user, 
            is_active=True
        ).count()
        
        if active_tokens >= 10:
            raise ValidationError('Maximum number of active tokens reached (10)')
        
        serializer.save(user=self.request.user)


class APITokenDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an API token.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = APITokenSerializer
    
    def get_queryset(self):
        return APIToken.objects.filter(user=self.request.user)


@regenerate_api_token_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_api_token(request, pk):
    """
    Regenerate an API token by creating a new JWT.
    """
    try:
        api_token = APIToken.objects.get(pk=pk, user=request.user)
    except APIToken.DoesNotExist:
        return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Clear the old token to force JWT regeneration
    api_token.token = ''
    api_token.created_at = timezone.now()
    api_token.save()
    
    serializer = APITokenSerializer(api_token)
    return Response({
        'message': 'API token regenerated successfully',
        'token': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_api_token(request, pk):
    """
    Toggle an API token's active status.
    """
    try:
        api_token = APIToken.objects.get(pk=pk, user=request.user)
    except APIToken.DoesNotExist:
        return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
    
    api_token.is_active = not api_token.is_active
    api_token.save()
    
    serializer = APITokenSerializer(api_token)
    status_text = 'activated' if api_token.is_active else 'deactivated'
    
    return Response({
        'message': f'API token {status_text} successfully',
        'token': serializer.data
    })