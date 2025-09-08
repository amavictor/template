from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal

from products.models import Product, Category
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from .authentication import APITokenAuthentication

User = get_user_model()


class APITokenAuthenticationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

    def test_token_authentication(self):
        auth = APITokenAuthentication()
        request = type('MockRequest', (), {})()
        request.META = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        
        user, token = auth.authenticate(request)
        self.assertEqual(user, self.user)
        self.assertEqual(token, self.token)

    def test_invalid_token(self):
        auth = APITokenAuthentication()
        request = type('MockRequest', (), {})()
        request.META = {'HTTP_AUTHORIZATION': 'Token invalid_token'}
        
        result = auth.authenticate(request)
        self.assertIsNone(result)


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
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
            status='active',
            stock_quantity=10
        )

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_product_list_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_product_not_listed(self):
        inactive_product = Product.objects.create(
            name='Inactive Product',
            description='Inactive description',
            price=Decimal('49.99'),
            product_type='desalination_unit',
            category=self.category,
            status='inactive',
            stock_quantity=5
        )
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)  # Only active product


class CartViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
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
            status='active',
            stock_quantity=10
        )

    def test_get_current_cart(self):
        url = reverse('cart-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)

    def test_add_item_to_cart(self):
        url = reverse('cart-add-item')
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('added to cart', response.data['message'])
        self.assertEqual(response.data['cart_total_items'], 2)
        
        # Verify cart item was created
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_existing_item_to_cart(self):
        # First, add an item
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        # Add the same item again
        url = reverse('cart-add-item')
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 3)  # 1 + 2

    def test_add_nonexistent_product_to_cart(self):
        url = reverse('cart-add-item')
        data = {'product_id': 99999, 'quantity': 1}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Product not found')

    def test_add_inactive_product_to_cart(self):
        inactive_product = Product.objects.create(
            name='Inactive Product',
            description='Inactive description',
            price=Decimal('49.99'),
            product_type='desalination_unit',
            category=self.category,
            status='inactive',
            stock_quantity=5
        )
        
        url = reverse('cart-add-item')
        data = {'product_id': inactive_product.id, 'quantity': 1}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Product not found')

    def test_remove_item_from_cart(self):
        # First, add an item
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        url = reverse('cart-remove-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Item removed from cart')
        self.assertEqual(response.data['cart_total_items'], 0)
        
        # Verify cart item was deleted
        with self.assertRaises(CartItem.DoesNotExist):
            CartItem.objects.get(cart=cart, product=self.product)

    def test_remove_nonexistent_item_from_cart(self):
        url = reverse('cart-remove-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found in cart')

    def test_clear_cart(self):
        # First, add some items
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        url = reverse('cart-clear')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Cart cleared')
        
        # Verify cart is empty
        self.assertEqual(cart.get_total_items(), 0)

    def test_clear_empty_cart(self):
        url = reverse('cart-clear')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Cart not found')


class WishlistViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
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
            status='active',
            stock_quantity=10
        )

    def test_get_current_wishlist(self):
        url = reverse('wishlist-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_count'], 0)

    def test_add_item_to_wishlist(self):
        url = reverse('wishlist-add-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('added to wishlist', response.data['message'])
        self.assertEqual(response.data['wishlist_total_items'], 1)
        
        # Verify wishlist item was created
        wishlist = Wishlist.objects.get(user=self.user)
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product=self.product)
        self.assertIsNotNone(wishlist_item)

    def test_add_duplicate_item_to_wishlist(self):
        # First, add an item
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product)
        
        # Try to add the same item again
        url = reverse('wishlist-add-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already in wishlist', response.data['message'])
        self.assertEqual(response.data['wishlist_total_items'], 1)

    def test_add_nonexistent_product_to_wishlist(self):
        url = reverse('wishlist-add-item')
        data = {'product_id': 99999}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Product not found')

    def test_add_inactive_product_to_wishlist(self):
        inactive_product = Product.objects.create(
            name='Inactive Product',
            description='Inactive description',
            price=Decimal('49.99'),
            product_type='desalination_unit',
            category=self.category,
            status='inactive',
            stock_quantity=5
        )
        
        url = reverse('wishlist-add-item')
        data = {'product_id': inactive_product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Product not found')

    def test_remove_item_from_wishlist(self):
        # First, add an item
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product)
        
        url = reverse('wishlist-remove-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Item removed from wishlist')
        self.assertEqual(response.data['wishlist_total_items'], 0)
        
        # Verify wishlist item was deleted
        with self.assertRaises(WishlistItem.DoesNotExist):
            WishlistItem.objects.get(wishlist=wishlist, product=self.product)

    def test_remove_nonexistent_item_from_wishlist(self):
        url = reverse('wishlist-remove-item')
        data = {'product_id': self.product.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found in wishlist')


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )
        
        self.product1 = Product.objects.create(
            name='Test Product 1',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=10
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test description',
            price=Decimal('49.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=5
        )
        
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_string_representation(self):
        self.assertEqual(str(self.cart), f'Cart - {self.user.email}')

    def test_get_total_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
        
        self.assertEqual(self.cart.get_total_items(), 5)

    def test_get_total_price(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)
        
        expected_total = (Decimal('99.99') * 2) + (Decimal('49.99') * 1)
        self.assertEqual(self.cart.get_total_price(), expected_total)

    def test_clear_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)
        
        self.assertEqual(self.cart.get_total_items(), 3)
        
        self.cart.clear()
        self.assertEqual(self.cart.get_total_items(), 0)


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
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
            status='active',
            stock_quantity=10
        )
        
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_string_representation(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(str(cart_item), 'Test Product x 2')

    def test_cart_item_price_when_added_auto_set(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertEqual(cart_item.price_when_added, self.product.price)

    def test_get_total_price(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        expected_total = self.product.price * 3
        self.assertEqual(cart_item.get_total_price(), expected_total)

    def test_price_change_detection(self):
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        original_price = cart_item.price_when_added
        
        # Change product price
        self.product.price = Decimal('149.99')
        self.product.save()
        
        cart_item.refresh_from_db()
        self.assertTrue(cart_item.has_price_changed())
        self.assertEqual(cart_item.get_price_difference(), Decimal('50.00'))


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            category_type='hardware'
        )

    def test_product_string_representation(self):
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

    def test_slug_auto_generation(self):
        product = Product.objects.create(
            name='Test Product Name',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=10
        )
        self.assertEqual(product.slug, 'test-product-name')

    def test_is_in_stock_physical_product(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=5
        )
        self.assertTrue(product.is_in_stock())
        
        product.stock_quantity = 0
        product.save()
        self.assertFalse(product.is_in_stock())

    def test_is_in_stock_subscription(self):
        product = Product.objects.create(
            name='Test Subscription',
            description='Test description',
            price=Decimal('29.99'),
            product_type='data_subscription',
            category=self.category,
            status='active',
            stock_quantity=0
        )
        self.assertTrue(product.is_in_stock())  # Subscriptions always in stock

    def test_is_low_stock(self):
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

    def test_get_discount_percentage(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('80.00'),
            compare_at_price=Decimal('100.00'),
            product_type='desalination_unit',
            category=self.category,
            status='active',
            stock_quantity=10
        )
        self.assertEqual(product.get_discount_percentage(), 20)
        
        # Test no discount
        product.compare_at_price = None
        product.save()
        self.assertEqual(product.get_discount_percentage(), 0)