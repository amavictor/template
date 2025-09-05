from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product


class Cart(models.Model):
    """Shopping cart for authenticated users."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Cart - {self.user.email}'
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """Get total price of all items in cart."""
        return sum(item.get_total_price() for item in self.items.all())
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()
    
    class Meta:
        db_table = 'cart_cart'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')


class CartItem(models.Model):
    """Individual items in a shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store price at time of adding to cart (for price change tracking)
    price_when_added = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """Set price when added if not already set."""
        if not self.price_when_added:
            self.price_when_added = self.product.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def get_total_price(self):
        """Get total price for this cart item."""
        return self.product.price * self.quantity
    
    def get_price_difference(self):
        """Get difference between current price and price when added."""
        return self.product.price - self.price_when_added
    
    def has_price_changed(self):
        """Check if product price has changed since adding to cart."""
        return self.product.price != self.price_when_added
    
    class Meta:
        db_table = 'cart_cartitem'
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'product']
        ordering = ['-added_at']


class Wishlist(models.Model):
    """User wishlist for saving products."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Wishlist - {self.user.email}'
    
    def get_item_count(self):
        """Get total number of items in wishlist."""
        return self.items.count()
    
    def clear(self):
        """Remove all items from wishlist."""
        self.items.all().delete()
    
    class Meta:
        db_table = 'cart_wishlist'
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')


class WishlistItem(models.Model):
    """Individual items in a user's wishlist."""
    
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    # Optional note from user
    note = models.TextField(blank=True, help_text=_('Optional note about this item'))
    
    def __str__(self):
        return f'{self.product.name} in {self.wishlist.user.email} wishlist'
    
    class Meta:
        db_table = 'cart_wishlistitem'
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']


class SessionCart(models.Model):
    """Cart for anonymous users using session."""
    
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Session Cart - {self.session_key}'
    
    def get_total_items(self):
        """Get total number of items in session cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """Get total price of all items in session cart."""
        return sum(item.get_total_price() for item in self.items.all())
    
    def clear(self):
        """Remove all items from session cart."""
        self.items.all().delete()
    
    def merge_with_user_cart(self, user):
        """Merge session cart with user's cart when they log in."""
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        for session_item in self.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=session_item.product,
                defaults={
                    'quantity': session_item.quantity,
                    'price_when_added': session_item.price_when_added,
                }
            )
            
            if not created:
                # If item already exists in user cart, add quantities
                cart_item.quantity += session_item.quantity
                cart_item.save()
        
        # Clear session cart after merging
        self.clear()
    
    class Meta:
        db_table = 'cart_sessioncart'
        verbose_name = _('Session Cart')
        verbose_name_plural = _('Session Carts')


class SessionCartItem(models.Model):
    """Individual items in a session cart."""
    
    session_cart = models.ForeignKey(SessionCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store price at time of adding to cart
    price_when_added = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """Set price when added if not already set."""
        if not self.price_when_added:
            self.price_when_added = self.product.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity} (Session)'
    
    def get_total_price(self):
        """Get total price for this session cart item."""
        return self.product.price * self.quantity
    
    def get_price_difference(self):
        """Get difference between current price and price when added."""
        return self.product.price - self.price_when_added
    
    def has_price_changed(self):
        """Check if product price has changed since adding to cart."""
        return self.product.price != self.price_when_added
    
    class Meta:
        db_table = 'cart_sessioncartitem'
        verbose_name = _('Session Cart Item')
        verbose_name_plural = _('Session Cart Items')
        unique_together = ['session_cart', 'product']
        ordering = ['-added_at']
