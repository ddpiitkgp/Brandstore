from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import datetime, json
from .models import Order, Payment, OrderProduct


def payment(request):
    """
    Renders the initial payment page (checkout summary/payment button).
    """
    return render(request, 'payment/payment.html', {'order_number': '', 'total_amount': ''})

def payment_summary(request):
    """
    Renders the initial payment page (checkout summary/payment button).
    """
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        amount = request.POST.get("amount")
        body = json.loads(request.body)

        order = Order.objects.get(order_number=order_id)
        payment = Payment.objects.get(order_number=order_id)

        order = get_object_or_404(
            Order,
            order_id=order_id,
            user=request.user
        )

        context = {
            "order": order,
            "amount": amount,
            "customer_name": order.user.get_full_name(),
            "email": order.user.email,
            "order_id": order.order_id,
            "product_name": order.product_name,
        }
        return render(request, "payments/payment_summary.html", context)

    return redirect("payment")

def payment_response(request):
    """
    Handles the webhook or callback response from the payment gateway.
    Usually processes POST data from PayPal, Stripe, Razorpay, etc.
    """
    # Logic to verify and save payment data goes here
    return HttpResponse("Processing Response...")

def payment_success(request):
    """
    The page shown to the user after a successful transaction.
    """
    return render(request, 'payment/payment_success.html', {'order_number': 'ABC-123'})

def payment_failed(request):
    """
    The page shown to the user if the transaction is declined or cancelled.
    """
    return render(request, 'payment/payment_failed.html', {'order_number': 'ABC-123'})
