from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product, Review, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model - simplified for admin use."""
    
    list_display = ('name', 'price', 'stock_quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'short_description', 'sku', 'environmental_matrix')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('🌱 Environmental Matrix', {
            'fields': ('environmental_matrix',),
            'description': '''<strong>Examples of environmental impact information:</strong><br/>
                • <strong>CO2 Impact:</strong> "Reduces CO2 emissions by 45% compared to traditional alternatives"<br/>
                • <strong>Energy Efficiency:</strong> "ENERGY STAR certified with 80% energy savings"<br/>
                • <strong>Materials:</strong> "Made from 90% recycled ocean plastic"<br/>
                • <strong>Sustainability:</strong> "Carbon neutral manufacturing process"<br/>
                • <strong>Recyclability:</strong> "100% recyclable at end of life"<br/>
                • <strong>Certifications:</strong> "FSC certified, GREENGUARD Gold certified"'''
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'compare_at_price', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('SEO (Optional)', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Only Product admin is registered - other models hidden from admin
