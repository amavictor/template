from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Subscription, 
    SubscriptionStatusHistory, 
    SubscriptionInvoice,
    APITokenPackage,
    UserAPIToken,
    APIUsageLog,
    EnvironmentalDataPoint,
    DataAlert
)


@admin.register(APITokenPackage)
class APITokenPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price', 'api_calls_per_month', 'is_active', 'is_featured', 'created_at')
    list_filter = ('duration', 'is_active', 'is_featured', 'includes_real_time_data', 'includes_historical_data')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'price')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'duration', 'price', 'description')
        }),
        ('Features', {
            'fields': ('api_calls_per_month', 'concurrent_connections', 'includes_real_time_data', 
                      'includes_historical_data', 'includes_analytics')
        }),
        ('Display Options', {
            'fields': ('is_active', 'is_featured', 'sort_order')
        }),
    )


@admin.register(UserAPIToken)
class UserAPITokenAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'package_name', 'token_key', 'status', 'expires_at', 'api_calls_used', 'days_remaining_display')
    list_filter = ('status', 'package__duration', 'expires_at')
    search_fields = ('user__email', 'token__key', 'package__name')
    readonly_fields = ('token_key', 'purchased_at', 'days_remaining_display', 'last_used_at')
    ordering = ('-purchased_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def package_name(self, obj):
        return obj.package.name
    package_name.short_description = 'Package'
    package_name.admin_order_field = 'package__name'
    
    def token_key(self, obj):
        return f"{obj.token.key[:8]}...{obj.token.key[-4:]}"
    token_key.short_description = 'Token'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining()
        if days > 0:
            return format_html('<span style="color: green;">{} days</span>', days)
        else:
            return format_html('<span style="color: red;">Expired</span>')
    days_remaining_display.short_description = 'Days Remaining'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'package', 'status')
        }),
        ('Token Details', {
            'fields': ('token_key', 'purchased_at', 'expires_at', 'days_remaining_display')
        }),
        ('Usage Tracking', {
            'fields': ('api_calls_used', 'last_used_at')
        }),
        ('Payment Info', {
            'fields': ('order_item',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscription_number', 'user', 'product', 'status', 'billing_cycle', 'next_billing_date', 'created_at')
    list_filter = ('status', 'billing_cycle', 'auto_renew', 'created_at')
    search_fields = ('subscription_number', 'user__email', 'product__name')
    readonly_fields = ('subscription_number', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('subscription_number', 'user', 'product', 'order_item')
        }),
        ('Status', {
            'fields': ('status', 'auto_renew')
        }),
        ('Billing', {
            'fields': ('price', 'billing_cycle', 'start_date', 'end_date', 'next_billing_date')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Usage Tracking', {
            'fields': ('api_calls_this_month', 'api_calls_total', 'last_api_call'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'endpoint', 'method', 'response_code', 'request_timestamp')
    list_filter = ('method', 'response_code', 'request_timestamp')
    search_fields = ('subscription__subscription_number', 'endpoint')
    readonly_fields = ('request_timestamp',)
    ordering = ('-request_timestamp',)


@admin.register(EnvironmentalDataPoint)
class EnvironmentalDataPointAdmin(admin.ModelAdmin):
    list_display = ('buoy_id', 'metric_type', 'value', 'unit', 'recorded_at', 'quality_score', 'is_anomaly')
    list_filter = ('metric_type', 'is_anomaly', 'recorded_at')
    search_fields = ('buoy_id',)
    ordering = ('-recorded_at',)


@admin.register(DataAlert)
class DataAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_id', 'title', 'severity', 'status', 'data_point', 'created_at')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('alert_id', 'title', 'data_point__buoy_id')
    ordering = ('-created_at',)
