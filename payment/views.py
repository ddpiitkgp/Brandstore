from django.shortcuts import render, redirect
from django.http import HttpResponse

def payment(request):
    """
    Renders the initial payment page (checkout summary/payment button).
    """
    return render(request, 'payment/payment.html', {'order_number': '', 'total_amount': ''})

def paymentfor(request):
    """
    Renders the initial payment page (checkout summary/payment button).
    """
    return render(request, 'payment/payment.html', {'order_number': 'ABC-123', 'total_amount': ''})

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
