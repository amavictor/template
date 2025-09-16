from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import Cart, CartItem, Wishlist, WishlistItem, SessionCart, SessionCartItem
from products.models import Product, Category

User = get_user_model()


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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

    def test_cart_creation(self):
        self.assertEqual(str(self.cart), f'Cart - {self.user.email}')
        self.assertEqual(self.cart.user, self.user)

    def test_get_total_items_empty_cart(self):
        self.assertEqual(self.cart.get_total_items(), 0)

    def test_get_total_items_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
        
        self.assertEqual(self.cart.get_total_items(), 5)

    def test_get_total_price_empty_cart(self):
        self.assertEqual(self.cart.get_total_price(), 0)

    def test_get_total_price_with_items(self):
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
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 0)

    def test_one_cart_per_user(self):
        # The OneToOneField should ensure only one cart per user
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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

    def test_cart_item_creation(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(str(cart_item), 'Test Product x 2')
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_price_when_added_auto_set(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(cart_item.price_when_added, self.product.price)

    def test_price_when_added_manual_set(self):
        custom_price = Decimal('89.99')
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
            price_when_added=custom_price
        )
        
        self.assertEqual(cart_item.price_when_added, custom_price)

    def test_get_total_price(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        
        expected_total = self.product.price * 3
        self.assertEqual(cart_item.get_total_price(), expected_total)

    def test_price_change_detection(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        original_price = cart_item.price_when_added
        self.assertFalse(cart_item.has_price_changed())
        self.assertEqual(cart_item.get_price_difference(), Decimal('0.00'))
        
        # Change product price
        self.product.price = Decimal('149.99')
        self.product.save()
        
        cart_item.refresh_from_db()
        self.assertTrue(cart_item.has_price_changed())
        self.assertEqual(cart_item.get_price_difference(), Decimal('50.00'))

    def test_price_decrease_detection(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        # Decrease product price
        self.product.price = Decimal('79.99')
        self.product.save()
        
        cart_item.refresh_from_db()
        self.assertTrue(cart_item.has_price_changed())
        self.assertEqual(cart_item.get_price_difference(), Decimal('-20.00'))

    def test_unique_constraint(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        # Creating another cart item with same cart and product should fail
        with self.assertRaises(Exception):  # IntegrityError
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=2
            )


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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
            status='active'
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test description',
            price=Decimal('49.99'),
            product_type='desalination_unit',
            category=self.category,
            status='active'
        )
        
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_wishlist_creation(self):
        self.assertEqual(str(self.wishlist), f'Wishlist - {self.user.email}')
        self.assertEqual(self.wishlist.user, self.user)

    def test_get_item_count_empty_wishlist(self):
        self.assertEqual(self.wishlist.get_item_count(), 0)

    def test_get_item_count_with_items(self):
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product2)
        
        self.assertEqual(self.wishlist.get_item_count(), 2)

    def test_clear_wishlist(self):
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product2)
        
        self.assertEqual(self.wishlist.get_item_count(), 2)
        
        self.wishlist.clear()
        self.assertEqual(self.wishlist.get_item_count(), 0)
        self.assertEqual(WishlistItem.objects.filter(wishlist=self.wishlist).count(), 0)

    def test_one_wishlist_per_user(self):
        # The OneToOneField should ensure only one wishlist per user
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)


class WishlistItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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
            status='active'
        )
        
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_wishlist_item_creation(self):
        wishlist_item = WishlistItem.objects.create(
            wishlist=self.wishlist,
            product=self.product,
            note='This looks great!'
        )
        
        expected_str = f'{self.product.name} in {self.user.email} wishlist'
        self.assertEqual(str(wishlist_item), expected_str)
        self.assertEqual(wishlist_item.note, 'This looks great!')

    def test_wishlist_item_without_note(self):
        wishlist_item = WishlistItem.objects.create(
            wishlist=self.wishlist,
            product=self.product
        )
        
        self.assertEqual(wishlist_item.note, '')

    def test_unique_constraint(self):
        WishlistItem.objects.create(
            wishlist=self.wishlist,
            product=self.product
        )
        
        # Creating another wishlist item with same wishlist and product should fail
        with self.assertRaises(Exception):  # IntegrityError
            WishlistItem.objects.create(
                wishlist=self.wishlist,
                product=self.product
            )


class SessionCartModelTest(TestCase):
    def setUp(self):
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
        
        self.session_cart = SessionCart.objects.create(session_key='test_session_123')

    def test_session_cart_creation(self):
        self.assertEqual(str(self.session_cart), 'Session Cart - test_session_123')
        self.assertEqual(self.session_cart.session_key, 'test_session_123')

    def test_get_total_items_empty_cart(self):
        self.assertEqual(self.session_cart.get_total_items(), 0)

    def test_get_total_items_with_items(self):
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product1,
            quantity=2
        )
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product2,
            quantity=3
        )
        
        self.assertEqual(self.session_cart.get_total_items(), 5)

    def test_get_total_price_with_items(self):
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product1,
            quantity=2
        )
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product2,
            quantity=1
        )
        
        expected_total = (Decimal('99.99') * 2) + (Decimal('49.99') * 1)
        self.assertEqual(self.session_cart.get_total_price(), expected_total)

    def test_clear_session_cart(self):
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product1,
            quantity=2
        )
        
        self.assertEqual(self.session_cart.get_total_items(), 2)
        
        self.session_cart.clear()
        self.assertEqual(self.session_cart.get_total_items(), 0)

    def test_merge_with_user_cart_new_cart(self):
        user = User.objects.create_user(
            username='testuser_session',
            email='test@example.com',
            password='testpass123'
        )
        
        # Add items to session cart
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product1,
            quantity=2,
            price_when_added=Decimal('99.99')
        )
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product2,
            quantity=1,
            price_when_added=Decimal('49.99')
        )
        
        # Merge with user cart
        self.session_cart.merge_with_user_cart(user)
        
        # Check user cart was created and items transferred
        user_cart = Cart.objects.get(user=user)
        self.assertEqual(user_cart.get_total_items(), 3)
        
        # Check session cart is empty
        self.assertEqual(self.session_cart.get_total_items(), 0)

    def test_merge_with_existing_user_cart(self):
        user = User.objects.create_user(
            username='testuser_session',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create existing user cart with items
        user_cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=user_cart, product=self.product1, quantity=1)
        
        # Add items to session cart
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product1,  # Same product as in user cart
            quantity=2
        )
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product2,  # Different product
            quantity=1
        )
        
        # Merge with user cart
        self.session_cart.merge_with_user_cart(user)
        
        # Check quantities were combined for existing product
        cart_item1 = CartItem.objects.get(cart=user_cart, product=self.product1)
        self.assertEqual(cart_item1.quantity, 3)  # 1 + 2
        
        # Check new product was added
        cart_item2 = CartItem.objects.get(cart=user_cart, product=self.product2)
        self.assertEqual(cart_item2.quantity, 1)
        
        # Check total items
        self.assertEqual(user_cart.get_total_items(), 4)
        
        # Check session cart is empty
        self.assertEqual(self.session_cart.get_total_items(), 0)


class SessionCartItemModelTest(TestCase):
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
        
        self.session_cart = SessionCart.objects.create(session_key='test_session_123')

    def test_session_cart_item_creation(self):
        session_item = SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(str(session_item), 'Test Product x 2 (Session)')
        self.assertEqual(session_item.quantity, 2)

    def test_price_when_added_auto_set(self):
        session_item = SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(session_item.price_when_added, self.product.price)

    def test_get_total_price(self):
        session_item = SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product,
            quantity=3
        )
        
        expected_total = self.product.price * 3
        self.assertEqual(session_item.get_total_price(), expected_total)

    def test_price_change_methods(self):
        session_item = SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product,
            quantity=1
        )
        
        # Initially no price change
        self.assertFalse(session_item.has_price_changed())
        self.assertEqual(session_item.get_price_difference(), Decimal('0.00'))
        
        # Change product price
        self.product.price = Decimal('149.99')
        self.product.save()
        
        session_item.refresh_from_db()
        self.assertTrue(session_item.has_price_changed())
        self.assertEqual(session_item.get_price_difference(), Decimal('50.00'))

    def test_unique_constraint(self):
        SessionCartItem.objects.create(
            session_cart=self.session_cart,
            product=self.product,
            quantity=1
        )
        
        # Creating another session cart item with same session cart and product should fail
        with self.assertRaises(Exception):  # IntegrityError
            SessionCartItem.objects.create(
                session_cart=self.session_cart,
                product=self.product,
                quantity=2
            )
