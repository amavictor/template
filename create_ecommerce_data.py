#!/usr/bin/env python3
"""
Create sample data for modern ecommerce site with API service
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluewave_ecommerce.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from products.models import Category, Product
from accounts.models import User


def create_ecommerce_data():
    print("🛍️ Creating modern ecommerce data...")
    
    # Create Categories
    print("\n📂 Creating categories...")
    
    electronics = Category.objects.get_or_create(
        name="Electronics",
        slug="electronics",
        defaults={
            'description': 'Latest smartphones, laptops, tablets and tech accessories',
            'category_type': 'hardware'
        }
    )[0]
    
    fashion = Category.objects.get_or_create(
        name="Fashion & Clothing", 
        slug="fashion-clothing",
        defaults={
            'description': 'Trendy clothes, shoes, and fashion accessories',
            'category_type': 'hardware'
        }
    )[0]
    
    home_garden = Category.objects.get_or_create(
        name="Home & Garden",
        slug="home-garden",
        defaults={
            'description': 'Home decor, furniture, garden tools and supplies',
            'category_type': 'hardware'
        }
    )[0]
    
    books = Category.objects.get_or_create(
        name="Books & Media",
        slug="books-media",
        defaults={
            'description': 'Books, audiobooks, movies and digital media',
            'category_type': 'service'
        }
    )[0]
    
    api_services = Category.objects.get_or_create(
        name="API Services",
        slug="api-services",
        defaults={
            'description': 'Developer API access plans and data services',
            'category_type': 'subscription'
        }
    )[0]
    
    print(f"✅ Created {Category.objects.count()} categories")
    
    # Create Electronics Products
    print("\n📱 Creating electronics products...")
    
    smartphone = Product.objects.get_or_create(
        name="iPhone 15 Pro Max",
        slug="iphone-15-pro-max",
        defaults={
            'description': '''The most advanced iPhone ever. The iPhone 15 Pro Max features:

• 6.7-inch Super Retina XDR display with ProMotion
• A17 Pro chip with 6-core GPU for incredible performance
• Pro camera system with 48MP Main, Ultra Wide, and Telephoto cameras
• Action button for quick access to your favorite features
• USB-C connector for universal charging
• Titanium design for durability and lightweight feel
• Up to 29 hours of video playback

Available in Natural Titanium, Blue Titanium, White Titanium, and Black Titanium.

What's in the box:
• iPhone 15 Pro Max
• USB-C to USB-C Cable
• Documentation

Perfect for photography enthusiasts, professionals, and anyone who wants the best mobile technology available.''',
            'short_description': 'Latest iPhone with titanium design, A17 Pro chip, and advanced camera system',
            'product_type': 'desalination_unit',  # Reusing existing choices
            'category': electronics,
            'price': Decimal('1199.99'),
            'compare_at_price': Decimal('1299.99'),
            'sku': 'APPLE-IPH15PM-128GB',
            'stock_quantity': 50,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    laptop = Product.objects.get_or_create(
        name="MacBook Air M2",
        slug="macbook-air-m2",
        defaults={
            'description': '''Redesigned around the next-generation M2 chip, MacBook Air is strikingly thin and brings exceptional speed and power efficiency within an incredibly portable design.

Key Features:
• M2 chip with 8-core CPU and up to 10-core GPU
• 13.6-inch Liquid Retina display with 500 nits of brightness
• 1080p FaceTime HD camera
• Four-speaker sound system with Spatial Audio
• Up to 18 hours of battery life
• 8GB unified memory, 256GB SSD storage
• Two Thunderbolt ports, headphone jack, MagSafe charging
• Backlit Magic Keyboard and Touch ID

Available in Midnight, Starlight, Silver, and Space Gray.

Perfect for students, professionals, and creatives who need powerful performance in a lightweight package.''',
            'short_description': 'Ultra-thin laptop with M2 chip, 13.6" Retina display, and all-day battery',
            'product_type': 'desalination_unit',
            'category': electronics,
            'price': Decimal('1099.99'),
            'compare_at_price': Decimal('1199.99'),
            'sku': 'APPLE-MBA-M2-256GB',
            'stock_quantity': 25,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    headphones = Product.objects.get_or_create(
        name="AirPods Pro (2nd Gen)",
        slug="airpods-pro-2nd-gen",
        defaults={
            'description': '''AirPods Pro (2nd generation) feature richer audio experiences. So you can lose yourself in music and podcasts, and get on calls with crystal-clear sound.

Advanced Features:
• Active Noise Cancellation reduces unwanted background noise
• Adaptive Transparency lets outside sounds in while reducing loud environmental noise
• Personalized Spatial Audio with dynamic head tracking
• Multiple ear tips (XS, S, M, L) for a customizable fit
• Touch control lets you swipe to adjust volume
• Up to 6 hours of listening time with ANC enabled
• Up to 30 hours total listening time with MagSafe Charging Case
• Sweat and water resistant (IPX4)

What's included:
• AirPods Pro
• MagSafe Charging Case
• Silicone ear tips (4 sizes)
• Lightning to USB-C Cable
• Documentation''',
            'short_description': 'Premium wireless earbuds with active noise cancellation and spatial audio',
            'product_type': 'desalination_unit',
            'category': electronics,
            'price': Decimal('249.99'),
            'sku': 'APPLE-APP-2ND-GEN',
            'stock_quantity': 100,
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    # Fashion Products
    print("\n👕 Creating fashion products...")
    
    sneakers = Product.objects.get_or_create(
        name="Nike Air Max 270",
        slug="nike-air-max-270",
        defaults={
            'description': '''The Nike Air Max 270 delivers visible comfort with the largest Max Air unit yet, offering a super-soft ride that feels as impossible as it looks.

Features:
• Nike's biggest heel Max Air unit yet delivers soft, all-day comfort
• Engineered mesh upper is lightweight and breathable
• Foam midsole feels soft and comfortable
• Rubber outsole with waffle-inspired pattern adds traction and durability
• Pull tabs on tongue and heel for easy on and off

Available in multiple colorways including:
• Black/White/Solar Red
• Triple Black
• White/Black/Total Orange
• Navy/Wolf Grey/White

Perfect for everyday wear, casual outings, or light athletic activities.
Runs true to size for most people.''',
            'short_description': 'Iconic sneakers with maximum air cushioning for all-day comfort',
            'product_type': 'desalination_unit',
            'category': fashion,
            'price': Decimal('150.00'),
            'compare_at_price': Decimal('170.00'),
            'sku': 'NIKE-AM270-BLK-10',
            'stock_quantity': 75,
            'status': 'active'
        }
    )[0]
    
    jacket = Product.objects.get_or_create(
        name="Levi's Trucker Jacket",
        slug="levis-trucker-jacket",
        defaults={
            'description': '''The classic denim jacket that started it all. Levi's Trucker Jacket is an iconic piece that never goes out of style.

Details:
• 100% cotton denim construction
• Classic point collar and button front closure  
• Two chest pockets with button flaps
• Two side entry pockets
• Adjustable button tabs at waist
• Rigid denim that will soften and fade beautifully over time
• Machine washable

Available sizes: XS, S, M, L, XL, XXL
Available washes:
• Dark Stonewash
• Medium Stonewash  
• Light Stonewash
• Black

The perfect layering piece that works with everything in your wardrobe. From casual weekend looks to smart-casual office attire.''',
            'short_description': 'Timeless denim jacket in classic trucker style, perfect for layering',
            'product_type': 'desalination_unit',
            'category': fashion,
            'price': Decimal('79.99'),
            'sku': 'LEVIS-TRUCK-DARK-M',
            'stock_quantity': 60,
            'status': 'active'
        }
    )[0]
    
    # Home & Garden Products  
    print("\n🏠 Creating home & garden products...")
    
    coffee_maker = Product.objects.get_or_create(
        name="Ninja Specialty Coffee Maker",
        slug="ninja-specialty-coffee-maker",
        defaults={
            'description': '''The Ninja Specialty Coffee Maker brews super-rich coffee concentrate that you can use to create delicious coffeehouse-style drinks.

Features:
• 6 brew sizes: Cup, Travel, XL Cup, XL Travel, XL Multi-Serve, Carafe
• 5 brew styles: Classic, Rich, Over Ice, Cold Brew, Specialty Concentrate
• Built-in frother creates silky-smooth hot or cold foam
• Fold-away frother tucks away to save space
• Removable water reservoir holds up to 50 oz.
• Permanent filter included - no paper filters needed
• Auto-iQ one-touch intelligence
• Dishwasher-safe parts for easy cleanup

What's Included:
• Ninja Specialty Coffee Maker
• 50 oz. Water Reservoir
• 10-Cup Glass Carafe
• Ninja Hot & Cold 18 oz. Tumbler
• Permanent Filter
• Frothing Whisk
• Scoop & Recipe Guide

Perfect for coffee enthusiasts who want café-quality drinks at home.''',
            'short_description': 'Versatile coffee maker with built-in frother for café-style drinks at home',
            'product_type': 'desalination_unit',
            'category': home_garden,
            'price': Decimal('179.99'),
            'compare_at_price': Decimal('199.99'),
            'sku': 'NINJA-SCM-CM401',
            'stock_quantity': 30,
            'status': 'active'
        }
    )[0]
    
    # API Service Products
    print("\n🔌 Creating API service products...")
    
    basic_api = Product.objects.get_or_create(
        name="Basic API Access",
        slug="basic-api-access",
        defaults={
            'description': '''Get started with our API services. Perfect for developers and small projects.

What's Included:
• 10,000 API calls per month
• Basic endpoints access
• Standard rate limiting
• Email support
• API documentation access
• Basic analytics dashboard
• 99.9% uptime SLA

Supported Endpoints:
• User management
• Product data
• Order processing  
• Basic analytics
• Webhook notifications

Perfect for:
• Individual developers
• Small projects
• Testing and prototyping
• Learning API integration

Generate your API tokens directly from your dashboard after purchase.
Tokens can be configured with custom expiry times up to 1 year.''',
            'short_description': 'Entry-level API access with 10K calls/month and basic endpoints',
            'product_type': 'data_subscription',
            'category': api_services,
            'price': Decimal('29.99'),
            'sku': 'API-BASIC-MONTHLY',
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    pro_api = Product.objects.get_or_create(
        name="Professional API Access", 
        slug="professional-api-access",
        defaults={
            'description': '''Advanced API access for growing businesses and professional developers.

What's Included:
• 100,000 API calls per month
• All endpoints access
• Priority rate limiting
• Priority email & chat support
• Advanced analytics dashboard
• Custom webhooks
• 99.95% uptime SLA
• Advanced authentication options

Supported Endpoints:
• Complete user management
• Full product catalog access
• Advanced order management
• Detailed analytics & reporting
• Custom webhook configurations
• Bulk operations
• Real-time notifications

Perfect for:
• Growing businesses
• E-commerce integrations
• Mobile app backends
• Third-party integrations
• Production applications

Generate unlimited API tokens with custom expiry times.
Advanced token management with scoped permissions.''',
            'short_description': 'Professional API access with 100K calls/month and advanced features',
            'product_type': 'data_subscription', 
            'category': api_services,
            'price': Decimal('199.99'),
            'sku': 'API-PRO-MONTHLY',
            'status': 'active',
            'is_featured': True
        }
    )[0]
    
    enterprise_api = Product.objects.get_or_create(
        name="Enterprise API Access",
        slug="enterprise-api-access", 
        defaults={
            'description': '''Enterprise-grade API solution for large-scale applications and businesses.

What's Included:
• 1,000,000 API calls per month
• Complete API access
• No rate limiting
• Dedicated account manager
• 24/7 phone & chat support
• Custom SLA options (up to 99.99%)
• Advanced security features
• Custom endpoint development
• White-label options available

Enterprise Features:
• Custom authentication methods
• IP whitelisting
• Advanced monitoring & alerts
• Custom data exports
• Priority feature requests
• Direct developer access
• On-premise deployment options

Perfect for:
• Large enterprises
• High-traffic applications
• Mission-critical systems
• Custom integrations
• Reseller partnerships

Includes dedicated support for API token architecture and security implementation.''',
            'short_description': 'Enterprise API solution with 1M calls/month and dedicated support',
            'product_type': 'data_subscription',
            'category': api_services, 
            'price': Decimal('999.99'),
            'sku': 'API-ENT-MONTHLY',
            'status': 'active'
        }
    )[0]
    
    print(f"✅ Created {Product.objects.count()} products")
    
    # Create sample users
    print("\n👤 Creating sample users...")
    
    # Keep existing admin user
    admin_user = User.objects.filter(email='admin@bluewave.com').first()
    if admin_user:
        print("✅ Admin user already exists")
    
    # Create/update customer user
    customer, created = User.objects.get_or_create(
        email='customer@example.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
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
    
    # Create developer user
    developer, created = User.objects.get_or_create(
        email='developer@example.com',
        defaults={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'user_type': 'customer', 
            'is_active': True
        }
    )
    if created:
        developer.set_password('dev123')
        developer.save()
        print("✅ Created developer@example.com / dev123")
    else:
        print("✅ Developer account already exists")
    
    print(f"\n🎉 Modern ecommerce data creation complete!")
    print(f"📊 Total products: {Product.objects.count()}")
    print(f"📂 Total categories: {Category.objects.count()}")
    print(f"🛍️ Physical products: {Product.objects.filter(product_type='desalination_unit').count()}")
    print(f"🔌 API services: {Product.objects.filter(product_type='data_subscription').count()}")
    
    print(f"\n🔑 Login credentials:")
    print(f"Admin: admin@bluewave.com / admin123")
    print(f"Customer: customer@example.com / demo123") 
    print(f"Developer: developer@example.com / dev123")
    
    print(f"\n🌐 Visit your site:")
    print(f"• Homepage: http://localhost:8000/")
    print(f"• Products: http://localhost:8000/products/")
    print(f"• Admin: http://localhost:8000/admin/")
    print(f"• API Docs: http://localhost:8000/api/docs/ (coming soon)")

if __name__ == '__main__':
    create_ecommerce_data()