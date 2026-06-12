from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404
import datetime, json
from .models import Order, Payment, OrderProduct, PaymentHistory
from store.models import ProductVariation, Product

from decimal import Decimal
import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from greatkart.services import send_email


def payment(request):
    """
    Renders the initial payment page (checkout summary/payment button).
    """
    return render(request, 'payment/payment.html', {'order_number': '', 'total_amount': ''})

def payment_summary(request):

    if request.method == "POST":

        frm_order_id = request.POST.get("order_id")
        frm_amount = request.POST.get("amount")

        order = Order.objects.filter( order_number=frm_order_id).first()
        orderproduct = OrderProduct.objects.filter(order_id=order.id).first()
        product_variation = ProductVariation.objects.filter(id=orderproduct.product_variation_id).first()
        order_detail = OrderProduct.objects.filter(order=order)

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_order = client.order.create({
            "amount": int(float(frm_amount) * 100),
            "currency": "INR",
            "receipt": frm_order_id,
            "payment_capture": 1
        })

        context = {
            "order": order,
            "amount": frm_amount,
            "customer_name": order.full_name(),
            "email": order.user.email,
            "order_id": order.order_number,
            "product_name": product_variation.product.product_name,
            "order_detail": order_detail,
            "frm_amount": frm_amount,
            # Razorpay
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        }

        return render(
            request,
            "payment/payment_summary.html",
            context
        )

    return redirect("payment")

def payment_response(request):

    if request.method != "POST":
        return redirect("payment")

    order_number = request.POST.get("order_number")
    payment = Payment.objects.filter(order_id=order_number).first()

    if not payment:
        return redirect(f"/payment/payment_failed/?order_number={order_number}")

    try:

        rzp_order_id = request.POST.get("razorpay_order_id")
        rzp_payment_id = request.POST.get("razorpay_payment_id")
        rzp_signature = request.POST.get("razorpay_signature")

        PaymentHistory.objects.create(
            payment=payment,
            order_id=order_number,
            event_name="CALLBACK_RECEIVED",
            status="PROCESSING",
            rawdata_inp=json.dumps(dict(request.POST), default=str)
        )

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        client.utility.verify_payment_signature({
            "razorpay_order_id": rzp_order_id,
            "razorpay_payment_id": rzp_payment_id,
            "razorpay_signature": rzp_signature
        })

        payment_info = client.payment.fetch(rzp_payment_id)

        payment.status = "SUCCESS"
        payment.txn_id = rzp_order_id
        payment.txn_payment_id = rzp_payment_id
        payment.txn_signature = rzp_signature
        payment.txn_status = payment_info.get("status")
        payment.txn_amount_paid = str(payment_info.get("amount", 0) / 100)
        payment.save()

        PaymentHistory.objects.create(
            payment=payment,
            order_id=order_number,
            event_name="PAYMENT_VERIFIED",
            status="SUCCESS",
            rawdata_out=json.dumps(payment_info, default=str)
        )

        return redirect(f"/payment/payment_success/?order_number={order_number}")

    except Exception as e:

        if payment:
            payment.status = "FAILED"
            payment.txn_status = "FAILED"
            payment.save()

        PaymentHistory.objects.create(
            payment=payment,
            order_id=order_number,
            event_name="PAYMENT_FAILED",
            status="FAILED",
            rawdata_inp=json.dumps(dict(request.POST), default=str),
            remarks=str(e)
        )

        return redirect(f"/payment/payment_failed/?order_number={order_number}")

def payment_success(request):
    order_number = request.GET.get("order_number")
    order = Order.objects.filter(order_number=order_number).first()
    payment = Payment.objects.filter( order_id=order_number).first()
    
    message = render_to_string('payment/payment_success_email.html', {
        'order_number': order_number,
        'payment': payment,
    })
    mail_subject = 'Thank you for your order!'
    admin_email_str = settings.ADMIN_EMAILS
    admin_emails = [email.strip() for email in admin_email_str.split(',') if email.strip()]
    to_emails = [order.user.email] + admin_emails
    result = send_email(mail_subject, message, to_emails)
    email_result = bool(result)  # Ensure it's a boolean for consistent handling in the template
    if email_result is True:
        email_result = "Email sent successfully: " + ", ".join(to_emails)
    elif email_result is False:
        email_result = "Failed to send email: " + ", ".join(to_emails)
    else:
        email_result = None

    context = {
        "order_number": order_number,
        "payment": payment,
        "email_result": email_result,
    }
    return render( request, "payment/payment_success.html",context)


def payment_failed(request):
    order_number = request.GET.get("order_number")
    payment = Payment.objects.filter( order_id=order_number).first()
    context = {
        "order_number": order_number,
        "payment": payment
    }
    return render( request, "payment/payment_failed.html",context)
