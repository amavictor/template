from django.shortcuts import render

def order_history(request):
    return render(request, 'orders/history.html')

def order_detail(request, order_id):
    return render(request, 'orders/detail.html')

def checkout(request):
    return render(request, 'orders/checkout.html')
