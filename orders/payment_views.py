import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from cart.models import Cart, CartItem
from .models import Order, OrderItem

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(LoginRequiredMixin, View):
    """Create Stripe Checkout Session and redirect to Stripe."""
    
    def post(self, request, *args, **kwargs):
        print(f"Checkout POST called for user: {request.user.id}")  # Debug log
        
        # Check if Stripe is configured
        if not settings.STRIPE_SECRET_KEY:
            messages.error(request, 'Payment system is not configured. Please contact support.')
            return redirect('cart:cart_detail')
        
        try:
            # Get user's cart
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            print(f"Found cart with {cart_items.count()} items")  # Debug log
            
            if not cart_items.exists():
                messages.error(request, 'Your cart is empty.')
                return redirect('cart:cart_detail')
            
            # Create line items for Stripe
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                            'description': item.product.short_description or '',
                        },
                        'unit_amount': int(item.product.price * 100),  # Convert to cents
                    },
                    'quantity': item.quantity,
                })
            
            print(f"Created {len(line_items)} line items for Stripe")  # Debug log
            
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('orders:checkout_success')
                ) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(
                    reverse('cart:cart_detail')
                ),
                customer_email=request.user.email,
                metadata={
                    'user_id': request.user.id,
                }
            )
            
            print(f"Created Stripe session: {checkout_session.id}")  # Debug log
            print(f"Redirecting to: {checkout_session.url}")  # Debug log
            
            return redirect(checkout_session.url, code=303)
            
        except Cart.DoesNotExist:
            print("Cart does not exist")  # Debug log
            messages.error(request, 'Cart not found.')
            return redirect('cart:cart_detail')
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")  # Debug log
            messages.error(request, f'Payment system error: {str(e)}')
            return redirect('cart:cart_detail')
        except Exception as e:
            print(f"General error: {str(e)}")  # Debug log
            messages.error(request, f'Checkout error: {str(e)}')
            return redirect('cart:cart_detail')


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    """Handle successful checkout from Stripe."""
    template_name = 'orders/checkout_success.html'
    
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        
        if not session_id:
            messages.error(request, 'Invalid checkout session.')
            return redirect('cart:cart_detail')
        
        try:
            # Retrieve the checkout session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            if checkout_session.payment_status != 'paid':
                messages.error(request, 'Payment was not completed.')
                return redirect('cart:cart_detail')
            
            # Check if order already exists for this session
            existing_order = Order.objects.filter(
                stripe_payment_intent_id=checkout_session.payment_intent
            ).first()
            
            if existing_order:
                # Order already exists, redirect to confirmation
                return redirect('orders:order_confirmation', order_id=existing_order.id)
            
            # Get user's cart
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            if not cart_items.exists():
                messages.error(request, 'Cart is empty.')
                return redirect('cart:cart_detail')
            
            # Calculate totals
            subtotal = sum(item.get_total_price() for item in cart_items)
            tax_amount = Decimal('0.00')
            shipping_amount = Decimal('0.00')
            total_amount = subtotal + tax_amount + shipping_amount
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                status='paid',
                payment_status='paid',
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_amount=shipping_amount,
                total_amount=total_amount,
                stripe_payment_intent_id=checkout_session.payment_intent,
                # Basic billing details from user
                billing_first_name=request.user.first_name or 'Customer',
                billing_last_name=request.user.last_name or '',
                billing_email=request.user.email,
                billing_phone='',
                billing_address_line1='Address provided to Stripe',
                billing_city='',
                billing_state='',
                billing_postal_code='',
                billing_country='US',
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku or '',
                    unit_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                    total_price=cart_item.get_total_price()
                )
            
            # Clear the cart
            cart_items.delete()
            
            # Redirect to confirmation page
            return redirect('orders:order_confirmation', order_id=order.id)
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Stripe error: {str(e)}')
            return redirect('cart:cart_detail')
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found.')
            return redirect('cart:cart_detail')
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('cart:cart_detail')


class OrderConfirmationView(LoginRequiredMixin, TemplateView):
    """Order confirmation page after successful payment."""
    template_name = 'orders/order_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, user=self.request.user)
            context['order'] = order
        except Order.DoesNotExist:
            context['order'] = None
            
        return context


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Handle Stripe webhooks for payment confirmation."""
    
    def post(self, request, *args, **kwargs):
        # If no webhook secret is configured, webhook verification is disabled
        if not settings.STRIPE_WEBHOOK_SECRET:
            return HttpResponse("Webhook verification disabled", status=200)
            
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_success(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failed(payment_intent)
        else:
            print(f'Unhandled event type: {event["type"]}')
        
        return HttpResponse(status=200)
    
    def _handle_payment_success(self, payment_intent):
        """Handle successful payment confirmation."""
        try:
            order = Order.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            if order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.status = 'paid'
                order.save()
                print(f'Order {order.order_number} marked as paid via webhook')
        except Order.DoesNotExist:
            print(f'Order not found for payment intent: {payment_intent["id"]}')
    
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        try:
            order = Order.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            order.payment_status = 'failed'
            order.status = 'cancelled'
            order.save()
            print(f'Order {order.order_number} marked as failed via webhook')
        except Order.DoesNotExist:
            print(f'Order not found for payment intent: {payment_intent["id"]}')


class OrderListView(LoginRequiredMixin, TemplateView):
    """List user's orders."""
    template_name = 'orders/order_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        return context


class OrderDetailView(LoginRequiredMixin, TemplateView):
    """View individual order details."""
    template_name = 'orders/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, user=self.request.user)
            context['order'] = order
        except Order.DoesNotExist:
            context['order'] = None
            
        return context