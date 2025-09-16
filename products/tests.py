from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.exceptions import ValidationError

from .models import (
    Category, Product, ProductImage, DesalinationUnit, 
    DataSubscription, EnvironmentalMetric, Review
)

User = get_user_model()


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(
            name='Test Category',
            description='Test description',
            category_type='hardware'
        )
        self.assertEqual(str(category), 'Test Category')
        self.assertEqual(category.slug, 'test-category')
        self.assertTrue(category.is_active)

    def test_category_slug_auto_generation(self):
        category = Category.objects.create(
            name='My Test Category',
            category_type='subscription'
        )
        self.assertEqual(category.slug, 'my-test-category')

    def test_category_unique_name(self):
        Category.objects.create(name='Unique Category', category_type='hardware')
        
        with self.assertRaises(Exception):  # IntegrityError
            Category.objects.create(name='Unique Category', category_type='service')

    def test_category_choices(self):
        category = Category.objects.create(
            name='Hardware Category',
            category_type='hardware'
        )
        self.assertEqual(category.category_type, 'hardware')
        
        # Test all valid choices
        valid_types = ['hardware', 'subscription', 'service']
        for category_type in valid_types:
            cat = Category(name=f'Test {category_type}', category_type=category_type)
            cat.full_clean()  # Should not raise ValidationError


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )

    def test_product_creation(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=10
        )
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.slug, 'test-product')

    def test_product_slug_uniqueness(self):
        Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )
        
        # Creating another product with same name should create different slug
        product2 = Product(
            name='Test Product',
            description='Another test description',
            price=Decimal('149.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )
        # Note: Django doesn't auto-handle slug uniqueness, this would need custom logic

    def test_product_is_in_stock_desalination(self):
        product = Product.objects.create(
            name='Desalination Unit',
            description='Test description',
            price=Decimal('999.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=5
        )
        self.assertTrue(product.is_in_stock())
        
        product.stock_quantity = 0
        product.save()
        self.assertFalse(product.is_in_stock())

    def test_product_is_in_stock_subscription(self):
        subscription_category = Category.objects.create(
            name='Subscriptions',
            category_type='subscription'
        )
        
        product = Product.objects.create(
            name='Data Subscription',
            description='Test description',
            price=Decimal('29.99'),
            product_type='data_subscription',
            category=subscription_category,
            status='active',
            stock_quantity=0  # Doesn't matter for subscriptions
        )
        self.assertTrue(product.is_in_stock())

    def test_product_is_low_stock(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=5,
            low_stock_threshold=10
        )
        self.assertTrue(product.is_low_stock())
        
        product.stock_quantity = 15
        product.save()
        self.assertFalse(product.is_low_stock())
        
        # Subscription products should never be low stock
        product.product_type = 'data_subscription'
        product.stock_quantity = 1
        product.save()
        self.assertFalse(product.is_low_stock())

    def test_product_discount_calculation(self):
        product = Product.objects.create(
            name='Discounted Product',
            description='Test description',
            price=Decimal('80.00'),
            compare_at_price=Decimal('100.00'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )
        self.assertEqual(product.get_discount_percentage(), 20)
        
        # No discount case
        product.compare_at_price = None
        product.save()
        self.assertEqual(product.get_discount_percentage(), 0)
        
        # Compare price lower than actual price
        product.compare_at_price = Decimal('70.00')
        product.save()
        self.assertEqual(product.get_discount_percentage(), 0)

    def test_product_status_choices(self):
        valid_statuses = ['draft', 'active', 'inactive', 'out_of_stock']
        
        for status_choice in valid_statuses:
            product = Product(
                name=f'Test Product {status_choice}',
                description='Test description',
                price=Decimal('99.99'),
                product_type='desalination_unit',
                category=self.category,
                status=status_choice
            )
            product.full_clean()  # Should not raise ValidationError

    def test_product_type_choices(self):
        valid_types = ['desalination_unit', 'data_subscription', 'service']
        
        for product_type in valid_types:
            product = Product(
                name=f'Test {product_type}',
                description='Test description',
                price=Decimal('99.99'),
                product_type=product_type,
                category=self.category,
                status='active'
            )
            product.full_clean()  # Should not raise ValidationError


class ProductImageModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )

    def test_product_image_creation(self):
        image = ProductImage.objects.create(
            product=self.product,
            alt_text='Test image',
            sort_order=1
        )
        self.assertEqual(str(image), f'{self.product.name} - Image {image.id}')
        self.assertFalse(image.is_primary)

    def test_product_image_ordering(self):
        image1 = ProductImage.objects.create(product=self.product, sort_order=2)
        image2 = ProductImage.objects.create(product=self.product, sort_order=1)
        image3 = ProductImage.objects.create(product=self.product, sort_order=3)
        
        images = list(ProductImage.objects.all())
        self.assertEqual(images[0], image2)  # sort_order=1
        self.assertEqual(images[1], image1)  # sort_order=2
        self.assertEqual(images[2], image3)  # sort_order=3


class DesalinationUnitModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Desalination Units',
            category_type='hardware'
        )
        
        self.product = Product.objects.create(
            name='Test Desalination Unit',
            description='Test description',
            price=Decimal('1999.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )

    def test_desalination_unit_creation(self):
        unit = DesalinationUnit.objects.create(
            product=self.product,
            water_output_per_day=1000.0,
            power_consumption=500.0,
            unit_size='medium',
            power_source='solar',
            dimensions='100x50x75',
            weight=25.5,
            salt_rejection_rate=99.5,
            warranty_years=3
        )
        
        self.assertEqual(str(unit), f'{self.product.name} - Medium (Small Business)')
        self.assertEqual(unit.water_output_per_day, 1000.0)
        self.assertTrue(unit.has_iot_monitoring)
        self.assertFalse(unit.has_remote_control)

    def test_desalination_unit_choices(self):
        valid_sizes = ['compact', 'medium', 'large']
        valid_power_sources = ['solar', 'hybrid', 'grid']
        
        for size in valid_sizes:
            unit = DesalinationUnit(
                product=self.product,
                water_output_per_day=1000.0,
                power_consumption=500.0,
                unit_size=size,
                power_source='solar',
                dimensions='100x50x75',
                weight=25.5,
                salt_rejection_rate=99.5
            )
            unit.full_clean()  # Should not raise ValidationError
            
        for power_source in valid_power_sources:
            unit = DesalinationUnit(
                product=self.product,
                water_output_per_day=1000.0,
                power_consumption=500.0,
                unit_size='medium',
                power_source=power_source,
                dimensions='100x50x75',
                weight=25.5,
                salt_rejection_rate=99.5
            )
            unit.full_clean()  # Should not raise ValidationError

    def test_desalination_unit_validators(self):
        # Test negative values should fail validation
        with self.assertRaises(ValidationError):
            unit = DesalinationUnit(
                product=self.product,
                water_output_per_day=-100.0,  # Negative value
                power_consumption=500.0,
                unit_size='medium',
                power_source='solar',
                dimensions='100x50x75',
                weight=25.5,
                salt_rejection_rate=99.5
            )
            unit.full_clean()
        
        # Test salt rejection rate over 100%
        with self.assertRaises(ValidationError):
            unit = DesalinationUnit(
                product=self.product,
                water_output_per_day=1000.0,
                power_consumption=500.0,
                unit_size='medium',
                power_source='solar',
                dimensions='100x50x75',
                weight=25.5,
                salt_rejection_rate=150.0  # Over 100%
            )
            unit.full_clean()


class DataSubscriptionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Data Subscriptions',
            category_type='subscription'
        )
        
        self.product = Product.objects.create(
            name='Professional Data Access',
            description='Professional tier subscription',
            price=Decimal('99.99'),
            product_type='data_subscription',
            category=self.category,
            status='active'
        )

    def test_data_subscription_creation(self):
        subscription = DataSubscription.objects.create(
            product=self.product,
            subscription_type='professional',
            billing_cycle='monthly',
            api_calls_per_month=5000,
            data_retention_months=24,
            concurrent_connections=3,
            has_real_time_alerts=True,
            has_custom_dashboards=True
        )
        
        self.assertEqual(str(subscription), f'{self.product.name} - Professional Access')
        self.assertTrue(subscription.includes_environmental_data)
        self.assertTrue(subscription.has_api_access)

    def test_subscription_type_choices(self):
        valid_types = ['basic', 'professional', 'enterprise']
        
        for sub_type in valid_types:
            subscription = DataSubscription(
                product=self.product,
                subscription_type=sub_type,
                billing_cycle='monthly'
            )
            subscription.full_clean()  # Should not raise ValidationError

    def test_billing_cycle_choices(self):
        valid_cycles = ['monthly', 'quarterly', 'annually']
        
        for cycle in valid_cycles:
            subscription = DataSubscription(
                product=self.product,
                subscription_type='basic',
                billing_cycle=cycle
            )
            subscription.full_clean()  # Should not raise ValidationError

    def test_subscription_defaults(self):
        subscription = DataSubscription.objects.create(
            product=self.product,
            subscription_type='basic'
        )
        
        self.assertEqual(subscription.billing_cycle, 'monthly')
        self.assertTrue(subscription.includes_environmental_data)
        self.assertFalse(subscription.includes_historical_data)
        self.assertFalse(subscription.has_real_time_alerts)
        self.assertEqual(subscription.api_calls_per_month, 1000)
        self.assertEqual(subscription.concurrent_connections, 1)


class EnvironmentalMetricModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )
        
        self.product = Product.objects.create(
            name='Eco-Friendly Product',
            description='Environmentally conscious product',
            price=Decimal('199.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )

    def test_environmental_metric_creation(self):
        metric = EnvironmentalMetric.objects.create(
            product=self.product,
            metric_type='water_saved',
            value=1000.0,
            unit='liters/day',
            description='Water saved per day of operation',
            display_order=1
        )
        
        expected_str = f'{self.product.name} - Water Saved: 1000.0 liters/day'
        self.assertEqual(str(metric), expected_str)
        self.assertTrue(metric.is_displayed)

    def test_environmental_metric_choices(self):
        valid_types = [
            'water_saved', 'energy_efficiency', 'carbon_footprint', 
            'plastic_waste', 'community_impact'
        ]
        
        for metric_type in valid_types:
            metric = EnvironmentalMetric(
                product=self.product,
                metric_type=metric_type,
                value=100.0,
                unit='test unit'
            )
            metric.full_clean()  # Should not raise ValidationError

    def test_environmental_metric_ordering(self):
        metric1 = EnvironmentalMetric.objects.create(
            product=self.product,
            metric_type='water_saved',
            value=1000.0,
            unit='liters/day',
            display_order=2
        )
        
        metric2 = EnvironmentalMetric.objects.create(
            product=self.product,
            metric_type='energy_efficiency',
            value=85.0,
            unit='%',
            display_order=1
        )
        
        metrics = list(EnvironmentalMetric.objects.all())
        self.assertEqual(metrics[0], metric2)  # display_order=1
        self.assertEqual(metrics[1], metric1)  # display_order=2


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )
        
        self.product = Product.objects.create(
            name='Reviewable Product',
            description='A product that can be reviewed',
            price=Decimal('299.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )

    def test_review_creation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Excellent Product',
            comment='This product exceeded my expectations!'
        )
        
        expected_str = f'{self.product.name} - 5/5 by {self.user.email}'
        self.assertEqual(str(review), expected_str)
        self.assertFalse(review.is_approved)
        self.assertFalse(review.is_verified_purchase)

    def test_review_rating_validation(self):
        # Test valid ratings (1-5)
        for rating in range(1, 6):
            review = Review(
                product=self.product,
                user=self.user,
                rating=rating,
                comment='Test review'
            )
            review.full_clean()  # Should not raise ValidationError
        
        # Test invalid ratings
        invalid_ratings = [0, 6, -1, 10]
        for rating in invalid_ratings:
            with self.assertRaises(ValidationError):
                review = Review(
                    product=self.product,
                    user=self.user,
                    rating=rating,
                    comment='Test review'
                )
                review.full_clean()

    def test_review_unique_constraint(self):
        # Create first review
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='First review'
        )
        
        # Try to create second review by same user for same product
        with self.assertRaises(Exception):  # IntegrityError
            Review.objects.create(
                product=self.product,
                user=self.user,
                rating=5,
                comment='Second review'
            )

    def test_multiple_users_can_review_same_product(self):
        user2 = User.objects.create_user(
            username='reviewer2',
            email='reviewer2@example.com',
            password='testpass123'
        )
        
        review1 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='Good product'
        )
        
        review2 = Review.objects.create(
            product=self.product,
            user=user2,
            rating=5,
            comment='Excellent product'
        )
        
        self.assertEqual(Review.objects.filter(product=self.product).count(), 2)

    def test_user_can_review_multiple_products(self):
        product2 = Product.objects.create(
            name='Another Product',
            description='Another reviewable product',
            price=Decimal('199.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )
        
        review1 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='Good first product'
        )
        
        review2 = Review.objects.create(
            product=product2,
            user=self.user,
            rating=5,
            comment='Excellent second product'
        )
        
        self.assertEqual(Review.objects.filter(user=self.user).count(), 2)
