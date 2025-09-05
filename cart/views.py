from django.shortcuts import render
from django.http import JsonResponse

def cart_detail(request):
    return render(request, 'cart/cart.html')

def add_to_cart(request):
    return JsonResponse({'success': True, 'cart_count': 1})

def update_cart(request):
    return JsonResponse({'success': True})

def remove_from_cart(request):
    return JsonResponse({'success': True})

def wishlist(request):
    return render(request, 'cart/wishlist.html')

def add_to_wishlist(request):
    return JsonResponse({'success': True})
