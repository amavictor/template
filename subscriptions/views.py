from django.shortcuts import render

def dashboard(request):
    return render(request, 'subscriptions/dashboard.html')

def my_subscriptions(request):
    return render(request, 'subscriptions/my_subscriptions.html')

def subscription_detail(request, subscription_id):
    return render(request, 'subscriptions/detail.html')
