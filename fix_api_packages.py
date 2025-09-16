#!/usr/bin/env python
"""
Script to fix existing API token packages and products with proper descriptions.
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluewave_ecommerce.settings')
django.setup()

from subscriptions.models import APITokenPackage
from products.models import Product

def fix_api_packages():
    """Fix existing API token packages and products."""
    
    packages = APITokenPackage.objects.all()
    
    for package in packages:
        print(f"Checking package: {package.name}")
        
        # Update package description if it's empty
        if not package.description:
            package.description = f"API access for {package.get_duration_display().lower()} with {package.api_calls_per_month} calls/month"
            package.save()
            print(f"  - Updated package description: {package.description}")
        
        # Find and update related product
        product_name = f"API Token - {package.name}"
        try:
            product = Product.objects.get(name=product_name)
            
            # Update product descriptions if they're empty
            updated = False
            if not product.description:
                product.description = package.description
                updated = True
                print(f"  - Updated product description")
            
            if not product.short_description:
                product.short_description = package.description
                updated = True
                print(f"  - Updated product short_description")
            
            if updated:
                product.save()
                
        except Product.DoesNotExist:
            print(f"  - No product found for package: {package.name}")

if __name__ == '__main__':
    fix_api_packages()
    print("API packages and products fixed successfully!")