#!/usr/bin/env python
"""
Script to create sample API token packages.
"""
import os
import django
import sys
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluewave_ecommerce.settings')
django.setup()

from subscriptions.models import APITokenPackage

def create_api_packages():
    """Create sample API token packages."""
    
    packages = [
        {
            'name': 'Basic API Access',
            'duration': 'week',
            'price': Decimal('9.99'),
            'description': 'Perfect for trying out our API with basic access for one week.',
            'api_calls_per_month': 1000,
            'concurrent_connections': 1,
            'includes_real_time_data': True,
            'includes_historical_data': False,
            'includes_analytics': False,
            'is_featured': False,
            'sort_order': 1,
        },
        {
            'name': 'Professional API Access',
            'duration': 'month',
            'price': Decimal('29.99'),
            'description': 'Ideal for professional developers with extended access and features.',
            'api_calls_per_month': 10000,
            'concurrent_connections': 3,
            'includes_real_time_data': True,
            'includes_historical_data': True,
            'includes_analytics': False,
            'is_featured': True,
            'sort_order': 2,
        },
        {
            'name': 'Enterprise API Access',
            'duration': 'year',
            'price': Decimal('299.99'),
            'description': 'Full enterprise access with all features and priority support.',
            'api_calls_per_month': 100000,
            'concurrent_connections': 10,
            'includes_real_time_data': True,
            'includes_historical_data': True,
            'includes_analytics': True,
            'is_featured': False,
            'sort_order': 3,
        },
    ]
    
    for package_data in packages:
        package, created = APITokenPackage.objects.get_or_create(
            name=package_data['name'],
            duration=package_data['duration'],
            defaults=package_data
        )
        
        if created:
            print(f"Created package: {package.name} ({package.get_duration_display()}) - ${package.price}")
        else:
            print(f"Package already exists: {package.name}")

if __name__ == '__main__':
    create_api_packages()
    print("API token packages created successfully!")