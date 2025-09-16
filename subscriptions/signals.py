from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from orders.models import Order, OrderItem
from .models import APITokenPackage, UserAPIToken


@receiver(post_save, sender=Order)
def create_api_tokens_on_payment(sender, instance, created, **kwargs):
    """Create API tokens when order is marked as paid."""
    if not created and instance.payment_status == 'paid':
        # Process order items for API token packages
        for item in instance.items.all():
            # Check if this is an API token product
            if item.product.sku and item.product.sku.startswith('API-'):
                try:
                    # Extract package ID from SKU (format: API-{package_id})
                    package_id = item.product.sku.split('-')[1]
                    package = APITokenPackage.objects.get(id=package_id)
                    
                    # Check if token already exists for this order item
                    if not hasattr(item, 'api_tokens') or not item.api_tokens.exists():
                        # Create API token for each quantity purchased
                        for _ in range(item.quantity):
                            UserAPIToken.create_from_package(
                                user=instance.user,
                                package=package,
                                order_item=item
                            )
                        
                        print(f"Created {item.quantity} API token(s) for user {instance.user.email}")
                
                except (IndexError, ValueError, APITokenPackage.DoesNotExist) as e:
                    print(f"Error creating API token for order {instance.order_number}: {e}")
                    continue