from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """Product categories for organizing items."""
    
    CATEGORY_TYPES = (
        ('hardware', 'Hardware Products'),
        ('subscription', 'Data Subscriptions'),
        ('service', 'Services'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='hardware')
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products_category'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']


class Product(models.Model):
    """Core product model for desalination units and subscriptions."""
    
    PRODUCT_TYPES = (
        ('desalination_unit', 'Desalination Unit'),
        ('data_subscription', 'Data Subscription'),
        ('service', 'Service'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    
    # Environmental Impact
    environmental_matrix = models.TextField(
        blank=True, 
        null=True,
        help_text=_('Environmental impact and sustainability information (e.g., CO2 effect, energy efficiency, recyclability)'),
        verbose_name=_('Environmental Matrix')
    )
    
    # Product Type and Category
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory (for physical products)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    
    # Product Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Images
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Get URL for this product."""
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def is_in_stock(self):
        """Check if product is in stock."""
        if self.product_type == 'data_subscription':
            return True  # Subscriptions are always in stock
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """Check if product has low stock."""
        if self.product_type == 'data_subscription':
            return False
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    def get_discount_percentage(self):
        """Calculate discount percentage if compare_at_price is set."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0
    
    class Meta:
        db_table = 'products_product'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'product_type']),
            models.Index(fields=['category', 'status']),
        ]


class ProductImage(models.Model):
    """Additional product images."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} - Image {self.id}'
    
    class Meta:
        db_table = 'products_productimage'
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['sort_order']


class DesalinationUnit(models.Model):
    """Extended model for desalination unit specific attributes."""
    
    UNIT_SIZES = (
        ('compact', 'Compact (Personal Use)'),
        ('medium', 'Medium (Small Business)'),
        ('large', 'Large (Industrial)'),
    )
    
    POWER_SOURCES = (
        ('solar', 'Solar Powered'),
        ('hybrid', 'Hybrid (Solar + Battery)'),
        ('grid', 'Grid Connected'),
    )
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='desalination_unit')
    
    # Technical Specifications
    water_output_per_day = models.FloatField(
        help_text=_('Water output in liters per day'),
        validators=[MinValueValidator(0)]
    )
    power_consumption = models.FloatField(
        help_text=_('Power consumption in watts'),
        validators=[MinValueValidator(0)]
    )
    unit_size = models.CharField(max_length=20, choices=UNIT_SIZES)
    power_source = models.CharField(max_length=20, choices=POWER_SOURCES)
    
    # Physical Specifications
    dimensions = models.CharField(max_length=100, help_text=_('L x W x H in cm'))
    weight = models.FloatField(help_text=_('Weight in kg'), validators=[MinValueValidator(0)])
    
    # Environmental Specifications
    operating_temperature_min = models.IntegerField(default=-10)
    operating_temperature_max = models.IntegerField(default=60)
    salt_rejection_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Salt rejection rate as percentage')
    )
    
    # Features
    has_iot_monitoring = models.BooleanField(default=True)
    has_remote_control = models.BooleanField(default=False)
    warranty_years = models.IntegerField(default=2)
    
    def __str__(self):
        return f'{self.product.name} - {self.get_unit_size_display()}'
    
    class Meta:
        db_table = 'products_desalinationunit'
        verbose_name = _('Desalination Unit')
        verbose_name_plural = _('Desalination Units')


class DataSubscription(models.Model):
    """Extended model for data subscription specific attributes."""
    
    SUBSCRIPTION_TYPES = (
        ('basic', 'Basic Access'),
        ('professional', 'Professional Access'),
        ('enterprise', 'Enterprise Access'),
    )
    
    BILLING_CYCLES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    )
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='data_subscription')
    
    # Subscription Details
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Data Access Permissions
    includes_environmental_data = models.BooleanField(default=True)
    includes_historical_data = models.BooleanField(default=False)
    includes_raw_telemetry = models.BooleanField(default=False)
    includes_predictive_analytics = models.BooleanField(default=False)
    
    # Usage Limits
    api_calls_per_month = models.IntegerField(
        default=1000,
        help_text=_('Number of API calls allowed per month')
    )
    data_retention_months = models.IntegerField(
        default=12,
        help_text=_('How long data is retained in months')
    )
    concurrent_connections = models.IntegerField(
        default=1,
        help_text=_('Number of concurrent API connections allowed')
    )
    
    # Features
    has_real_time_alerts = models.BooleanField(default=False)
    has_custom_dashboards = models.BooleanField(default=False)
    has_data_export = models.BooleanField(default=True)
    has_api_access = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.product.name} - {self.get_subscription_type_display()}'
    
    class Meta:
        db_table = 'products_datasubscription'
        verbose_name = _('Data Subscription')
        verbose_name_plural = _('Data Subscriptions')


class EnvironmentalMetric(models.Model):
    """Environmental metrics data that can be displayed on product pages."""
    
    METRIC_TYPES = (
        ('water_saved', 'Water Saved'),
        ('energy_efficiency', 'Energy Efficiency'),
        ('carbon_footprint', 'Carbon Footprint Reduction'),
        ('plastic_waste', 'Plastic Waste Prevented'),
        ('community_impact', 'Community Impact'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='environmental_metrics')
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=50, help_text=_('e.g., liters/day, kWh, kg CO2'))
    description = models.TextField(blank=True)
    
    # Display options
    is_displayed = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.product.name} - {self.get_metric_type_display()}: {self.value} {self.unit}'
    
    class Meta:
        db_table = 'products_environmentalmetric'
        verbose_name = _('Environmental Metric')
        verbose_name_plural = _('Environmental Metrics')
        ordering = ['display_order']


class Review(models.Model):
    """Product reviews and ratings."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Review status
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.product.name} - {self.rating}/5 by {self.user.email}'
    
    class Meta:
        db_table = 'products_review'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['product', 'user']
