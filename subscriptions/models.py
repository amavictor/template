from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product, DataSubscription
from orders.models import OrderItem
import uuid


class Subscription(models.Model):
    """Active data subscriptions for users."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
    )
    
    # Subscription identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='subscription',
        blank=True,
        null=True,
        help_text=_('The order item that created this subscription')
    )
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Pricing and billing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Subscription price at time of purchase')
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=DataSubscription.BILLING_CYCLES,
        default='monthly'
    )
    
    # Subscription period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    
    # Usage tracking
    api_calls_this_month = models.IntegerField(default=0)
    api_calls_total = models.IntegerField(default=0)
    last_api_call = models.DateTimeField(blank=True, null=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """Generate subscription number if not set."""
        if not self.subscription_number:
            import time
            import random
            timestamp = str(int(time.time()))[-6:]
            random_num = str(random.randint(100, 999))
            self.subscription_number = f'SUB{timestamp}{random_num}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Subscription {self.subscription_number} - {self.user.email} - {self.product.name}'
    
    def is_active(self):
        """Check if subscription is currently active."""
        return self.status == 'active'
    
    def is_expired(self):
        """Check if subscription has expired."""
        if not self.end_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.end_date
    
    def days_until_renewal(self):
        """Get days until next renewal."""
        if not self.next_billing_date:
            return None
        from django.utils import timezone
        delta = self.next_billing_date - timezone.now()
        return delta.days if delta.days >= 0 else 0
    
    def get_data_subscription_details(self):
        """Get related DataSubscription model if it exists."""
        try:
            return self.product.data_subscription
        except DataSubscription.DoesNotExist:
            return None
    
    def can_access_environmental_data(self):
        """Check if subscription allows environmental data access."""
        details = self.get_data_subscription_details()
        return details and details.includes_environmental_data and self.is_active()
    
    def can_access_historical_data(self):
        """Check if subscription allows historical data access."""
        details = self.get_data_subscription_details()
        return details and details.includes_historical_data and self.is_active()
    
    def can_access_raw_telemetry(self):
        """Check if subscription allows raw telemetry access."""
        details = self.get_data_subscription_details()
        return details and details.includes_raw_telemetry and self.is_active()
    
    def get_remaining_api_calls(self):
        """Get remaining API calls for this month."""
        details = self.get_data_subscription_details()
        if not details:
            return 0
        return max(0, details.api_calls_per_month - self.api_calls_this_month)
    
    def increment_api_usage(self):
        """Increment API usage counter."""
        from django.utils import timezone
        self.api_calls_this_month += 1
        self.api_calls_total += 1
        self.last_api_call = timezone.now()
        self.save(update_fields=['api_calls_this_month', 'api_calls_total', 'last_api_call'])
    
    def reset_monthly_usage(self):
        """Reset monthly API usage counter."""
        self.api_calls_this_month = 0
        self.save(update_fields=['api_calls_this_month'])
    
    class Meta:
        db_table = 'subscriptions_subscription'
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['subscription_number']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['stripe_subscription_id']),
        ]


class SubscriptionStatusHistory(models.Model):
    """Track status changes for subscriptions."""
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Subscription.STATUS_CHOICES)
    reason = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Reason for status change')
    )
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.subscription.subscription_number} - {self.get_status_display()}'
    
    class Meta:
        db_table = 'subscriptions_subscriptionstatushistory'
        verbose_name = _('Subscription Status History')
        verbose_name_plural = _('Subscription Status Histories')
        ordering = ['-created_at']


class SubscriptionInvoice(models.Model):
    """Invoices for subscription billing."""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
    )
    
    # Invoice identification
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Relationships
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Invoice details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Billing period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Stripe integration
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    
    # Usage details (for usage-based billing)
    api_calls_used = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Generate invoice number if not set."""
        if not self.invoice_number:
            import time
            import random
            timestamp = str(int(time.time()))[-6:]
            random_num = str(random.randint(100, 999))
            self.invoice_number = f'INV{timestamp}{random_num}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Invoice {self.invoice_number} - {self.subscription.subscription_number}'
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.status == 'paid':
            return False
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    def days_overdue(self):
        """Get number of days overdue."""
        if not self.is_overdue():
            return 0
        from django.utils import timezone
        delta = timezone.now() - self.due_date
        return delta.days
    
    class Meta:
        db_table = 'subscriptions_subscriptioninvoice'
        verbose_name = _('Subscription Invoice')
        verbose_name_plural = _('Subscription Invoices')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['due_date']),
        ]


class APIUsageLog(models.Model):
    """Log API usage for subscriptions."""
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage_logs')
    
    # Request details
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_code = models.IntegerField()
    
    # Usage tracking
    request_timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField(blank=True, null=True)
    bytes_transferred = models.IntegerField(blank=True, null=True)
    
    # Request metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.subscription.subscription_number} - {self.endpoint} - {self.request_timestamp}'
    
    class Meta:
        db_table = 'subscriptions_apiusagelog'
        verbose_name = _('API Usage Log')
        verbose_name_plural = _('API Usage Logs')
        ordering = ['-request_timestamp']
        indexes = [
            models.Index(fields=['subscription', 'request_timestamp']),
            models.Index(fields=['endpoint']),
        ]


class EnvironmentalDataPoint(models.Model):
    """Environmental data points from IoT buoys."""
    
    METRIC_TYPES = (
        ('salinity', 'Salinity (ppm)'),
        ('ph', 'pH Level'),
        ('temperature', 'Temperature (°C)'),
        ('dissolved_oxygen', 'Dissolved Oxygen (mg/L)'),
        ('turbidity', 'Turbidity (NTU)'),
        ('conductivity', 'Conductivity (µS/cm)'),
        ('nitrates', 'Nitrates (mg/L)'),
        ('phosphates', 'Phosphates (mg/L)'),
        ('chlorophyll', 'Chlorophyll-a (µg/L)'),
    )
    
    # Data identification
    buoy_id = models.CharField(max_length=50)
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    
    # Data values
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    
    # Location (optional)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Quality indicators
    quality_score = models.FloatField(
        blank=True,
        null=True,
        help_text=_('Data quality score from 0.0 to 1.0')
    )
    is_anomaly = models.BooleanField(default=False)
    
    # Timestamps
    recorded_at = models.DateTimeField(help_text=_('When the data was recorded by the buoy'))
    received_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.buoy_id} - {self.get_metric_type_display()}: {self.value} {self.unit}'
    
    class Meta:
        db_table = 'subscriptions_environmentaldatapoint'
        verbose_name = _('Environmental Data Point')
        verbose_name_plural = _('Environmental Data Points')
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['buoy_id', 'metric_type', 'recorded_at']),
            models.Index(fields=['recorded_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]


class DataAlert(models.Model):
    """Alerts for environmental data anomalies."""
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    )
    
    # Alert identification
    alert_id = models.CharField(max_length=50, unique=True, blank=True)
    
    # Related data
    data_point = models.ForeignKey(
        EnvironmentalDataPoint,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    # Alert details
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Alert conditions
    threshold_value = models.FloatField(blank=True, null=True)
    condition = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('e.g., "greater_than", "less_than", "equals"')
    )
    
    # Resolution
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Generate alert ID if not set."""
        if not self.alert_id:
            import time
            import random
            timestamp = str(int(time.time()))[-6:]
            random_num = str(random.randint(100, 999))
            self.alert_id = f'ALT{timestamp}{random_num}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Alert {self.alert_id} - {self.title}'
    
    class Meta:
        db_table = 'subscriptions_dataalert'
        verbose_name = _('Data Alert')
        verbose_name_plural = _('Data Alerts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['data_point']),
        ]
