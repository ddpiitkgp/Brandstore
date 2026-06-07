from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product, ProductVariation
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

import smtplib
from email.message import EmailMessage as RawEmailMessage

def send_email(subject, body, to_emails):
    from django.conf import settings
    # Configuration
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD

    msg = RawEmailMessage()
    msg.set_content(body)
    msg.add_alternative(body, subtype='html')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_emails

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # comment the below 2 in Production server
            #server.starttls()
            #server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@require_POST
@login_required(login_url='login')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, order_number=body['orderID'])

    # 1. Store transaction details
    payment = Payment(
        user_id = request.user,
        order_id = order.order_number,  
        txn_payment_id = body['transID'],
        total_price = order.order_total,
        txn_amount_paid = order.order_total,  # Assuming the amount paid is the same as order total
        txn_order = order.order_number,
        status = body['status'],
    )
    payment.save()

    if body['status'] == 'COMPLETED':
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_variation_id = item.product_variation_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product_variation.product.price
            
            # --- TAX CALCULATION LOGIC ---
            # Calculate CGST and SGST amounts based on the Category rates
            # Amount = (Price * Quantity) * (Percentage / 100)
            price_for_tax = float(item.product_variation.product.price) * item.quantity
            orderproduct.cgst = round(price_for_tax * (float(item.product_variation.product.category.cgst) / 100), 2)
            orderproduct.sgst = round(price_for_tax * (float(item.product_variation.product.category.sgst) / 100), 2)
            # -----------------------------

            orderproduct.ordered = True
            orderproduct.save()

            # Reduce the quantity of the sold products
            item.product_variation.stock -= item.quantity
            item.product_variation.save()

        # 2. Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # 3. Send email
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = sum(i.product_price * i.quantity for i in ordered_products)
        
        # Calculate total tax breakdown for the email template
        total_cgst = round(sum(i.cgst for i in ordered_products), 2)
        total_sgst = round(sum(i.sgst for i in ordered_products), 2)
        
        # Calculate total tax properly
        total_tax = round(total_cgst + total_sgst, 2)
        
        # Calculate effective tax percentages
        cgst_percentage = round((total_cgst / subtotal * 100) if subtotal > 0 else 0, 2)
        sgst_percentage = round((total_sgst / subtotal * 100) if subtotal > 0 else 0, 2)

        message = render_to_string('orders/email_template.html', {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.txn_payment_id,
            'payment': payment,

            'subtotal': subtotal,
            'cgst': total_cgst,
            'sgst': total_sgst,
            'cgst_percentage': cgst_percentage,
            'sgst_percentage': sgst_percentage,
            'tax': total_tax,
        })
        mail_subject = 'Thank you for your order!'

        admin_email_str = settings.ADMIN_EMAILS
        admin_emails = [email.strip() for email in admin_email_str.split(',') if email.strip()]
        to_emails = [request.user.email] + admin_emails
        result = send_email(mail_subject, message, to_emails)
        
        try:
            request.session[f'email_sent_{order.order_number}'] = bool(result)
        except Exception:
            pass
        
        data = {
            'order_number': order.order_number,
            'transID': payment.txn_payment_id,            
        }
        return JsonResponse(data)
    
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Payment was not successful'}, status=400)
@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        messages.error(request, "Your cart is empty")
        return redirect('store')

    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product_variation.stock:
            messages.error(request, f"Currently this variation {cart_item.product_variation} is out of stock.")
            return redirect('cart')

    total_cgst = 0
    total_sgst = 0
    grand_total = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        
        # Calculate Category-based Tax
        # Calculation: (Price * Quantity) * (Tax_Rate / 100)
        item_cgst = round((cart_item.product.price * cart_item.quantity) * (float(cart_item.product.category.cgst) / 100), 2)
        item_sgst = round((cart_item.product.price * cart_item.quantity) * (float(cart_item.product.category.sgst) / 100), 2)
        total_cgst += item_cgst
        total_sgst += item_sgst

    total_tax = round(total_cgst + total_sgst, 2)
    grand_total = round(total + total_tax, 2)
    
    # Calculate effective tax percentages
    cgst_percentage = round((total_cgst / total * 100) if total > 0 else 0, 2)
    sgst_percentage = round((total_sgst / total * 100) if total > 0 else 0, 2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                data = Order()
                # ... (Your existing field assignments: first_name, last_name, etc.) ...
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                
                data.order_total = grand_total
                data.tax = total_tax # Stores total GST
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

        # Generate Order Number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d") #20210305
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'cgst': total_cgst,
                    'sgst': total_sgst,
                    'cgst_percentage': cgst_percentage,
                    'sgst_percentage': sgst_percentage,
                    'tax': total_tax,
                    'grand_total': grand_total,
                }
                return render(request, 'orders/payments.html', context)
            except Exception as e:
                messages.error(request, f"Error processing order: {e}")
                return redirect('checkout')
        else:
            messages.error(request, f"Form validation failed: {form.errors}")
            return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('txn_payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(txn_payment_id=transID)
        total_cgst = 0
        total_sgst = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            total_cgst += i.cgst
            total_sgst += i.sgst

        # Round the total tax values to 2 decimal places
        total_cgst = round(total_cgst, 2)
        total_sgst = round(total_sgst, 2)
        
        # Calculate total tax properly
        total_tax = round(total_cgst + total_sgst, 2)
        
        # Calculate effective tax percentages
        cgst_percentage = round((total_cgst / subtotal * 100) if subtotal > 0 else 0, 2)
        sgst_percentage = round((total_sgst / subtotal * 100) if subtotal > 0 else 0, 2)
        
        # Read the email send result from session (set by payments()).
        # Map boolean -> friendly message; if missing, leave as None.
        email_result = request.session.pop(f'email_sent_{order_number}', None)
        if email_result is True:
            email_result = "Email sent successfully"
        elif email_result is False:
            email_result = "Failed to send email"
        else:
            email_result = None

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.txn_payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'cgst': total_cgst,
            'sgst': total_sgst,
            'cgst_percentage': cgst_percentage,
            'sgst_percentage': sgst_percentage,
            'tax': total_tax,
            'email_result': email_result,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def blank_page(request):
    # Get data from the URL parameters
    order_number = request.GET.get('order_number')
    amount = request.GET.get('amount')
    
    context = {
        'order_number': order_number,
        'amount': amount,
    }

    return render(request, 'orders/blank_page.html', context)

def email_template(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        payment = Payment.objects.get(txn_payment_id=transID)
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        total_cgst = 0
        total_sgst = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            total_cgst += i.cgst
            total_sgst += i.sgst

        # Calculate effective tax percentages
        cgst_percentage = (total_cgst / subtotal * 100) if subtotal > 0 else 0
        sgst_percentage = (total_sgst / subtotal * 100) if subtotal > 0 else 0

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.txn_payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'cgst': total_cgst,
            'sgst': total_sgst,
            'cgst_percentage': cgst_percentage,
            'sgst_percentage': sgst_percentage,
        }
        
        html_string = render_to_string('orders/email_template.html', context)
        
        return HttpResponse(html_string)

    except Exception as e:
        return HttpResponse(str(e), status=400)

