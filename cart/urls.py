from django.urls import path
from . import simple_views

app_name = 'cart'

urlpatterns = [
    path('', simple_views.CartView.as_view(), name='cart_detail'),
    path('add/', simple_views.AddToCartView.as_view(), name='add_to_cart'),
    path('update/', simple_views.UpdateCartQuantityView.as_view(), name='update_cart'),
    path('remove/', simple_views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('wishlist/', simple_views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', simple_views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/', simple_views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]