from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta


def convert_tokens_to_jwt(apps, schema_editor):
    """Convert existing DRF tokens to JWT tokens."""
    UserAPIToken = apps.get_model('subscriptions', 'UserAPIToken')
    
    for user_token in UserAPIToken.objects.all():
        try:
            # Import here to avoid issues during migration
            from rest_framework_simplejwt.tokens import AccessToken
            import uuid
            
            # Generate new JWT token
            token = AccessToken.for_user(user_token.user)
            
            # Add custom claims
            token['subscription_id'] = str(uuid.uuid4())
            token['package_id'] = user_token.package.id
            token['package_name'] = user_token.package.name
            token['api_calls_limit'] = user_token.package.api_calls_per_month
            token['expires_at'] = user_token.expires_at.isoformat()
            
            # Set token expiration
            remaining_time = user_token.expires_at - timezone.now()
            if remaining_time.total_seconds() > 0:
                token.set_exp(lifetime=remaining_time)
            
            # Update the token_key field
            user_token.token_key = str(token)
            user_token.save()
            
            print(f"Converted token for user {user_token.user.email}")
            
        except Exception as e:
            print(f"Error converting token for user {user_token.user.email}: {e}")
            # If conversion fails, mark token as expired
            user_token.status = 'expired'
            user_token.save()


def reverse_conversion(apps, schema_editor):
    """Reverse operation - not implemented as it's not easily reversible."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('subscriptions', '0002_apitokenpackage_userapitoken'),
    ]

    operations = [
        # Add the new token_key field
        migrations.AddField(
            model_name='userapitoken',
            name='token_key',
            field=models.CharField(default='', help_text='JWT token for API access', max_length=1000),
            preserve_default=False,
        ),
        
        # Run the data migration
        migrations.RunPython(convert_tokens_to_jwt, reverse_conversion),
        
        # Remove the old token field
        migrations.RemoveField(
            model_name='userapitoken',
            name='token',
        ),
        
        # Make token_key unique
        migrations.AlterField(
            model_name='userapitoken',
            name='token_key',
            field=models.CharField(help_text='JWT token for API access', max_length=1000, unique=True),
        ),
    ]