from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, ProductVariation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from greatkart.utils import gst_breakup


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

@csrf_exempt
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    # If the user is authenticated
    if current_user.is_authenticated:
        if request.method == 'POST':
            color_value = request.POST.get('color')
            size_value = request.POST.get('size')
            if color_value and size_value:
                try:
                    product_variation_obj = ProductVariation.objects.get(product=product, color__iexact=color_value, size__iexact=size_value)
                except ProductVariation.DoesNotExist:
                    messages.error(request, "Selected variation combination does not exist.")
                    return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

                if product_variation_obj.stock < 1:
                    messages.error(request, "Out of stock.")
                    return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

                is_cart_item_exists = CartItem.objects.filter(product_variation=product_variation_obj, user=current_user).exists()
                if is_cart_item_exists:
                    item = CartItem.objects.get(product_variation=product_variation_obj, user=current_user)
                    if item.quantity + 1 > product_variation_obj.stock:
                        messages.error(request, "Not enough stock.")
                        return redirect('cart')
                    item.quantity += 1
                    item.save()
                else:
                    item = CartItem.objects.create(product_variation=product_variation_obj, quantity=1, user=current_user)
                    item.save()
            else:
                messages.error(request, "Please select both color and size.")
                return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
        return redirect('cart')
    # If the user is not authenticated
    else:
        if request.method == 'POST':
            color_value = request.POST.get('color')
            size_value = request.POST.get('size')
            if color_value and size_value:
                try:
                    product_variation_obj = ProductVariation.objects.get(product=product, color__iexact=color_value, size__iexact=size_value)
                except ProductVariation.DoesNotExist:
                    messages.error(request, "Selected variation combination does not exist.")
                    return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

                if product_variation_obj.stock < 1:
                    messages.error(request, "Out of stock.")
                    return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(
                        cart_id = _cart_id(request)
                    )
                cart.save()

                is_cart_item_exists = CartItem.objects.filter(product_variation=product_variation_obj, cart=cart).exists()
                if is_cart_item_exists:
                    item = CartItem.objects.get(product_variation=product_variation_obj, cart=cart)
                    if item.quantity + 1 > product_variation_obj.stock:
                        messages.error(request, "Not enough stock.")
                        return redirect('cart')
                    item.quantity += 1
                    item.save()
                else:
                    item = CartItem.objects.create(product_variation=product_variation_obj, quantity=1, cart=cart)
                    item.save()
            else:
                messages.error(request, "Please select both color and size.")
                return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product_variation__product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product_variation__product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product_variation__product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product_variation__product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        total_cgst = 0
        total_sgst = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += float(cart_item.product.price * cart_item.quantity)
            quantity += float(cart_item.quantity)

            cgst_rate = float(cart_item.product.category.cgst)
            sgst_rate = float(cart_item.product.category.sgst)
            total_gst = float(cgst_rate + sgst_rate)

            taxable_amount, item_cgst, item_sgst = gst_breakup(total, cgst_rate, sgst_rate)

            total_gst = total - taxable_amount

            total = round(taxable_amount, 2)
            total_cgst += item_cgst
            total_sgst += item_sgst
            
        tax = (total_cgst + total_sgst)
        grand_total = round((total + tax), 2)

    except ObjectDoesNotExist:
        total_cgst = 0
        total_sgst = 0
        tax = 0
        grand_total = 0
        cgst_rate = 0
        sgst_rate = 0
        pass #just ignore

    context = {
        'total': round(total, 2),
        'quantity': quantity,
        'cart_items': cart_items,
        'cgst': round(total_cgst, 2),
        'sgst': round(total_sgst, 2),
        'cgst_percentage': cgst_rate,
        'sgst_percentage': sgst_rate,
        'tax': round(tax, 2),
        'grand_total': round(grand_total, 0),
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total_price=0, quantity=0, cart_items=None):
    try:
        total_cgst = 0
        total_sgst = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
            cgst_rate = float(cart_item.product.category.cgst)
            sgst_rate = float(cart_item.product.category.sgst)
            total_gst = float(cgst_rate + sgst_rate)
            
            taxable_amount, item_cgst, item_sgst = gst_breakup(total_price, cgst_rate, sgst_rate)
            total_gst = total_price - taxable_amount
            
            total = round(taxable_amount, 2)
            total_cgst += item_cgst
            total_sgst += item_sgst
            
        tax = (total_cgst + total_sgst)
        grand_total = round((total + tax), 2)


    except ObjectDoesNotExist:
        total_cgst = 0
        total_sgst = 0
        tax = 0
        grand_total = 0
        cgst_percentage = 0
        sgst_percentage = 0
        pass #just ignore

    context = {
        'total': round(total,2),
        'quantity': quantity,
        'cart_items': cart_items,
        'cgst': round(total_cgst, 2),
        'sgst': round(total_sgst, 2),
        'cgst_percentage': round(cgst_rate, 2),
        'sgst_percentage': round(sgst_rate, 2),
        'tax': round(tax, 2),
        'grand_total': round(grand_total, 2),
    }
    return render(request, 'store/checkout.html', context)
