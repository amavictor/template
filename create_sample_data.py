#!/usr/bin/env python3
"""
Script to create sample data for BlueWave Solutions eCommerce platform.
Run this after setting up the Django project to populate the database with demo content.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluewave_ecommerce.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from products.models import Category, Product, DesalinationUnit, DataSubscription, EnvironmentalMetric
from accounts.models import User


def create_sample_data():
    print("🌊 Creating sample data for BlueWave Solutions...")
    
    # Create Categories
    print("\n📂 Creating categories...")
    cat_desalination = Category.objects.get_or_create(
        name="Desalination Units",
        slug="desalination-units",
        defaults={
            'description': 'Solar-powered water purification systems for clean drinking water',
            'category_type': 'hardware'
        }
    )[0]
    
    cat_data = Category.objects.get_or_create(
        name="Data Subscriptions", 
        slug="data-subscriptions",
        defaults={
            'description': 'Environmental monitoring and data access services',
            'category_type': 'subscription'
        }
    )[0]
    
    print(f"✅ Created categories: {cat_desalination.name}, {cat_data.name}")
    
    # Create Desalination Unit Products
    print("\n🏭 Creating desalination unit products...")
    
    # Compact Unit
    compact_unit = Product.objects.get_or_create(
        name="AquaPure Compact",
        slug="aquapure-compact",
        defaults={
            'description': '''The AquaPure Compact is perfect for personal and small family use. This solar-powered desalination unit provides up to 20 liters of fresh drinking water per day from seawater or brackish water sources.

            Key Features:
            • 100% solar powered operation
            • Produces 20L of fresh water daily
            • Built-in IoT monitoring system
            • Compact design fits in small spaces
            • 99.9% salt removal efficiency
            • Automatic cleaning cycles
            • Mobile app integration

            Perfect for:
            • Small households (1-4 people)
            • Off-grid living
            • Emergency preparedness
            • Beach houses and cabins
            • Disaster relief situations''',
            'short_description': 'Compact solar-powered desalination unit producing 20L/day of fresh water',
            'product_type': 'desalination_unit',
            'category': cat_desalination,
            'price': Decimal('2999.99'),
            'compare_at_price': Decimal('3499.99'),
            'sku': 'BWS-AP-COMPACT-001',
            'stock_quantity': 25,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    # Create corresponding DesalinationUnit details
    DesalinationUnit.objects.get_or_create(
        product=compact_unit,
        defaults={
            'water_output_per_day': 20.0,
            'power_consumption': 150.0,
            'unit_size': 'compact',
            'power_source': 'solar',
            'dimensions': '60 x 40 x 35',
            'weight': 15.5,
            'operating_temperature_min': -5,
            'operating_temperature_max': 50,
            'salt_rejection_rate': 99.9,
            'has_iot_monitoring': True,
            'has_remote_control': True,
            'warranty_years': 3
        }
    )
    
    # Medium Unit
    medium_unit = Product.objects.get_or_create(
        name="AquaPure Professional",
        slug="aquapure-professional", 
        defaults={
            'description': '''The AquaPure Professional is designed for small businesses, restaurants, and larger families. This robust solar-powered system produces up to 50 liters of pristine drinking water daily.

            Key Features:
            • Enhanced solar panel array
            • Produces 50L of fresh water daily
            • Advanced IoT monitoring with predictive maintenance
            • Modular design for easy maintenance
            • 99.95% salt removal efficiency
            • Integrated water quality testing
            • Remote monitoring dashboard
            • Backup battery system

            Perfect for:
            • Small businesses and restaurants
            • Large families (5-12 people)
            • Community centers
            • Small hotels and B&Bs
            • Agricultural operations''',
            'short_description': 'Professional-grade solar desalination system producing 50L/day',
            'product_type': 'desalination_unit',
            'category': cat_desalination,
            'price': Decimal('7999.99'),
            'compare_at_price': Decimal('8999.99'),
            'sku': 'BWS-AP-PRO-001',
            'stock_quantity': 12,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    DesalinationUnit.objects.get_or_create(
        product=medium_unit,
        defaults={
            'water_output_per_day': 50.0,
            'power_consumption': 300.0,
            'unit_size': 'medium',
            'power_source': 'hybrid',
            'dimensions': '120 x 80 x 60',
            'weight': 45.2,
            'operating_temperature_min': -10,
            'operating_temperature_max': 60,
            'salt_rejection_rate': 99.95,
            'has_iot_monitoring': True,
            'has_remote_control': True,
            'warranty_years': 5
        }
    )
    
    # Industrial Unit
    industrial_unit = Product.objects.get_or_create(
        name="AquaPure Industrial",
        slug="aquapure-industrial",
        defaults={
            'description': '''The AquaPure Industrial is our flagship high-capacity desalination system designed for industrial applications, large communities, and emergency response operations.

            Key Features:
            • High-efficiency solar array with grid backup
            • Produces 200L of fresh water daily
            • Enterprise-grade IoT monitoring
            • Redundant filtration systems
            • 99.98% salt removal efficiency
            • Real-time water quality monitoring
            • Automated maintenance alerts
            • 24/7 remote support included
            • Modular expansion capability

            Perfect for:
            • Industrial facilities
            • Large communities (50+ people)
            • Emergency response teams
            • Military installations
            • Large-scale agricultural operations
            • Water bottling facilities''',
            'short_description': 'Industrial-scale solar desalination system producing 200L/day',
            'product_type': 'desalination_unit',
            'category': cat_desalination,
            'price': Decimal('24999.99'),
            'sku': 'BWS-AP-IND-001',
            'stock_quantity': 3,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    DesalinationUnit.objects.get_or_create(
        product=industrial_unit,
        defaults={
            'water_output_per_day': 200.0,
            'power_consumption': 800.0,
            'unit_size': 'large',
            'power_source': 'hybrid',
            'dimensions': '200 x 150 x 120',
            'weight': 150.0,
            'operating_temperature_min': -15,
            'operating_temperature_max': 65,
            'salt_rejection_rate': 99.98,
            'has_iot_monitoring': True,
            'has_remote_control': True,
            'warranty_years': 7
        }
    )
    
    print(f"✅ Created {Product.objects.filter(product_type='desalination_unit').count()} desalination units")
    
    # Create Data Subscription Products
    print("\n📊 Creating data subscription products...")
    
    # Basic Plan
    basic_plan = Product.objects.get_or_create(
        name="Environmental Data Basic",
        slug="environmental-data-basic",
        defaults={
            'description': '''Get started with our basic environmental monitoring data plan. Perfect for students, researchers, and small organizations.

            What's Included:
            • Real-time environmental data from 50+ IoT buoys
            • Basic water quality metrics (pH, salinity, temperature)
            • Historical data access (last 6 months)
            • 1,000 API calls per month
            • Email support
            • Basic data export (CSV)
            • Community forum access

            Data Sources:
            • Coastal water monitoring stations
            • Offshore IoT buoy network
            • Automated data quality checks
            • 15-minute data refresh intervals''',
            'short_description': 'Basic environmental monitoring data access for researchers and students',
            'product_type': 'data_subscription',
            'category': cat_data,
            'price': Decimal('29.99'),
            'sku': 'BWS-DATA-BASIC-M',
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    DataSubscription.objects.get_or_create(
        product=basic_plan,
        defaults={
            'subscription_type': 'basic',
            'billing_cycle': 'monthly',
            'includes_environmental_data': True,
            'includes_historical_data': True,
            'includes_raw_telemetry': False,
            'includes_predictive_analytics': False,
            'api_calls_per_month': 1000,
            'data_retention_months': 6,
            'concurrent_connections': 1,
            'has_real_time_alerts': False,
            'has_custom_dashboards': False,
            'has_data_export': True,
            'has_api_access': True
        }
    )
    
    # Professional Plan
    pro_plan = Product.objects.get_or_create(
        name="Environmental Data Professional", 
        slug="environmental-data-professional",
        defaults={
            'description': '''Advanced environmental data access for professional researchers, NGOs, and government agencies.

            What's Included:
            • Real-time data from 200+ monitoring stations
            • Advanced water quality metrics (dissolved oxygen, turbidity, conductivity, nitrates)
            • Historical data access (last 5 years)
            • 10,000 API calls per month
            • Priority email and phone support
            • Advanced data export (JSON, XML, CSV)
            • Custom data visualizations
            • Real-time alerts and notifications
            • Custom dashboards
            • Data quality scores and anomaly detection

            Perfect for:
            • Research institutions
            • Government agencies
            • Environmental consultancies
            • NGOs and non-profits
            • Policy makers''',
            'short_description': 'Professional environmental data with advanced analytics and 5-year history',
            'product_type': 'data_subscription',
            'category': cat_data,
            'price': Decimal('199.99'),
            'sku': 'BWS-DATA-PRO-M',
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    DataSubscription.objects.get_or_create(
        product=pro_plan,
        defaults={
            'subscription_type': 'professional',
            'billing_cycle': 'monthly', 
            'includes_environmental_data': True,
            'includes_historical_data': True,
            'includes_raw_telemetry': True,
            'includes_predictive_analytics': True,
            'api_calls_per_month': 10000,
            'data_retention_months': 60,
            'concurrent_connections': 5,
            'has_real_time_alerts': True,
            'has_custom_dashboards': True,
            'has_data_export': True,
            'has_api_access': True
        }
    )
    
    # Enterprise Plan
    enterprise_plan = Product.objects.get_or_create(
        name="Environmental Data Enterprise",
        slug="environmental-data-enterprise",
        defaults={
            'description': '''Enterprise-level environmental data solution with unlimited access and dedicated support.

            What's Included:
            • Full access to global monitoring network (500+ stations)
            • Complete environmental metrics suite
            • Unlimited historical data access
            • 100,000 API calls per month
            • Dedicated account manager
            • Custom data integrations
            • White-label solutions
            • Advanced machine learning analytics
            • Predictive modeling tools
            • Custom reporting and dashboards
            • 24/7 technical support
            • On-site training and consultation
            • Raw IoT telemetry access

            Perfect for:
            • Large corporations
            • Government departments
            • International organizations
            • Research consortiums
            • Data resellers''',
            'short_description': 'Enterprise environmental data solution with unlimited access and dedicated support',
            'product_type': 'data_subscription', 
            'category': cat_data,
            'price': Decimal('999.99'),
            'sku': 'BWS-DATA-ENT-M',
            'status': 'active'
        }
    )[0]
    
    DataSubscription.objects.get_or_create(
        product=enterprise_plan,
        defaults={
            'subscription_type': 'enterprise',
            'billing_cycle': 'monthly',
            'includes_environmental_data': True,
            'includes_historical_data': True,
            'includes_raw_telemetry': True,
            'includes_predictive_analytics': True,
            'api_calls_per_month': 100000,
            'data_retention_months': 120,
            'concurrent_connections': 25,
            'has_real_time_alerts': True,
            'has_custom_dashboards': True,
            'has_data_export': True,
            'has_api_access': True
        }
    )
    
    print(f"✅ Created {Product.objects.filter(product_type='data_subscription').count()} data subscription plans")
    
    # Add Environmental Metrics to products
    print("\n🌱 Adding environmental impact metrics...")
    
    # Metrics for Compact Unit
    EnvironmentalMetric.objects.get_or_create(
        product=compact_unit,
        metric_type='water_saved',
        defaults={
            'value': 7300,
            'unit': 'liters/year',
            'description': 'Fresh water production capacity per year',
            'is_displayed': True,
            'display_order': 1
        }
    )
    
    EnvironmentalMetric.objects.get_or_create(
        product=compact_unit,
        metric_type='carbon_footprint',
        defaults={
            'value': 0,
            'unit': 'kg CO2/year', 
            'description': '100% solar powered - zero carbon emissions',
            'is_displayed': True,
            'display_order': 2
        }
    )
    
    EnvironmentalMetric.objects.get_or_create(
        product=compact_unit,
        metric_type='plastic_waste',
        defaults={
            'value': 2400,
            'unit': 'bottles prevented/year',
            'description': 'Plastic water bottles prevented from waste',
            'is_displayed': True,
            'display_order': 3
        }
    )
    
    # Metrics for Professional Unit  
    EnvironmentalMetric.objects.get_or_create(
        product=medium_unit,
        metric_type='water_saved',
        defaults={
            'value': 18250,
            'unit': 'liters/year',
            'description': 'Fresh water production capacity per year',
            'is_displayed': True,
            'display_order': 1
        }
    )
    
    EnvironmentalMetric.objects.get_or_create(
        product=medium_unit,
        metric_type='community_impact',
        defaults={
            'value': 12,
            'unit': 'people served',
            'description': 'Number of people with reliable water access',
            'is_displayed': True,
            'display_order': 2
        }
    )
    
    print("✅ Added environmental impact metrics")
    
    # Create a sample customer user
    print("\n👤 Creating sample customer account...")
    customer, created = User.objects.get_or_create(
        email='customer@example.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Customer', 
            'user_type': 'customer',
            'is_active': True
        }
    )
    if created:
        customer.set_password('demo123')
        customer.save()
        print("✅ Created customer@example.com / demo123")
    else:
        print("✅ Customer account already exists")
    
    print(f"\n🎉 Sample data creation complete!")
    print(f"📊 Total products created: {Product.objects.count()}")
    print(f"📂 Total categories: {Category.objects.count()}")
    print(f"🏭 Desalination units: {Product.objects.filter(product_type='desalination_unit').count()}")
    print(f"📈 Data subscriptions: {Product.objects.filter(product_type='data_subscription').count()}")
    
    print(f"\n🔑 Login credentials:")
    print(f"Admin: admin@bluewave.com / admin123")
    print(f"Customer: customer@example.com / demo123")
    
    print(f"\n🌐 You can now visit:")
    print(f"• Homepage: http://localhost:8000/")
    print(f"• Products: http://localhost:8000/products/") 
    print(f"• Admin: http://localhost:8000/admin/")
    
if __name__ == '__main__':
    create_sample_data()