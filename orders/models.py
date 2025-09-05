from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product
import uuid


class Order(models.Model):
    """Customer orders for products and subscriptions."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    # Order identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Customer information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Billing information
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address_line1 = models.CharField(max_length=255)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    
    # Shipping information (can be same as billing)
    shipping_first_name = models.CharField(max_length=50, blank=True)
    shipping_last_name = models.CharField(max_length=50, blank=True)
    shipping_address_line1 = models.CharField(max_length=255, blank=True)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    
    # Payment information
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    
    # Order tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=50, blank=True)
    
    # Notes and additional info
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """Generate order number if not set."""
        if not self.order_number:
            # Generate order number: BW + timestamp + random
            import time
            import random
            timestamp = str(int(time.time()))[-6:]
            random_num = str(random.randint(100, 999))
            self.order_number = f'BW{timestamp}{random_num}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Order {self.order_number} - {self.user.email}'
    
    def get_full_billing_address(self):
        """Get formatted billing address."""
        address_parts = [
            f'{self.billing_first_name} {self.billing_last_name}',
            self.billing_address_line1,
        ]
        if self.billing_address_line2:
            address_parts.append(self.billing_address_line2)
        
        address_parts.extend([
            f'{self.billing_city}, {self.billing_state} {self.billing_postal_code}',
            self.billing_country
        ])
        return '\n'.join(address_parts)
    
    def get_full_shipping_address(self):
        """Get formatted shipping address."""
        if not self.shipping_first_name:
            return self.get_full_billing_address()
        
        address_parts = [
            f'{self.shipping_first_name} {self.shipping_last_name}',
            self.shipping_address_line1,
        ]
        if self.shipping_address_line2:
            address_parts.append(self.shipping_address_line2)
        
        address_parts.extend([
            f'{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}',
            self.shipping_country
        ])
        return '\n'.join(address_parts)
    
    def is_subscription_order(self):
        """Check if this order contains subscription items."""
        return self.items.filter(product__product_type='data_subscription').exists()
    
    def is_physical_order(self):
        """Check if this order contains physical items."""
        return self.items.filter(product__product_type='desalination_unit').exists()
    
    class Meta:
        db_table = 'orders_order'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]


class OrderItem(models.Model):
    """Individual items within an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Product details at time of purchase
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    
    # Pricing at time of purchase
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # For subscription items
    subscription_start_date = models.DateTimeField(blank=True, null=True)
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Set product details and calculate total price."""
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku and self.product.sku:
            self.product_sku = self.product.sku
        if not self.unit_price:
            self.unit_price = self.product.price
        
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product_name} x {self.quantity} - {self.order.order_number}'
    
    class Meta:
        db_table = 'orders_orderitem'
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        ordering = ['id']


class OrderStatusHistory(models.Model):
    """Track status changes for orders."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.order.order_number} - {self.get_status_display()}'
    
    class Meta:
        db_table = 'orders_orderstatushistory'
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-created_at']


class ShippingMethod(models.Model):
    """Available shipping methods."""
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery estimates
    min_delivery_days = models.IntegerField(default=1)
    max_delivery_days = models.IntegerField(default=7)
    
    # Availability
    is_active = models.BooleanField(default=True)
    countries = models.TextField(
        blank=True,
        help_text=_('Comma-separated list of country codes. Leave blank for all countries.')
    )
    
    # Requirements
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Minimum order amount for this shipping method')
    )
    max_weight = models.FloatField(
        blank=True,
        null=True,
        help_text=_('Maximum weight in kg for this shipping method')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} - ${self.price}'
    
    def get_delivery_estimate(self):
        """Get delivery estimate string."""
        if self.min_delivery_days == self.max_delivery_days:
            return f'{self.min_delivery_days} day{"s" if self.min_delivery_days > 1 else ""}'
        return f'{self.min_delivery_days}-{self.max_delivery_days} days'
    
    class Meta:
        db_table = 'orders_shippingmethod'
        verbose_name = _('Shipping Method')
        verbose_name_plural = _('Shipping Methods')
        ordering = ['price']


class Coupon(models.Model):
    """Discount coupons for orders."""
    
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Percentage (0-100) or fixed amount')
    )
    
    # Usage limits
    usage_limit = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum number of times this coupon can be used')
    )
    usage_count = models.IntegerField(default=0)
    usage_limit_per_user = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum uses per user')
    )
    
    # Amount limits
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Minimum order amount to use this coupon')
    )
    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Maximum discount amount (for percentage discounts)')
    )
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Applicable products/categories
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        help_text=_('Leave empty to apply to all products')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.code} - {self.name}'
    
    def is_valid(self):
        """Check if coupon is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (not self.usage_limit or self.usage_count < self.usage_limit)
        )
    
    def can_be_used_by_user(self, user):
        """Check if coupon can be used by a specific user."""
        if not self.is_valid():
            return False
        
        if self.usage_limit_per_user:
            user_usage = OrderCoupon.objects.filter(
                coupon=self,
                order__user=user
            ).count()
            return user_usage < self.usage_limit_per_user
        
        return True
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount for given order amount."""
        if not self.is_valid() or order_amount < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (order_amount * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        
        elif self.discount_type == 'fixed_amount':
            return min(self.discount_value, order_amount)
        
        return 0
    
    class Meta:
        db_table = 'orders_coupon'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']


class OrderCoupon(models.Model):
    """Track coupon usage in orders."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.coupon.code} used in {self.order.order_number}'
    
    class Meta:
        db_table = 'orders_ordercoupon'
        verbose_name = _('Order Coupon')
        verbose_name_plural = _('Order Coupons')
        unique_together = ['order', 'coupon']
