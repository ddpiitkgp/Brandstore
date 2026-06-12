from django.db import models
from django.contrib.auth.models import User # Assuming you are using the default User model
from accounts.models import Account
from store.models import ProductVariation, Product

class Payment(models.Model):
    order_id = models.CharField(max_length=100, db_index=True)
    total_price = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="INITIATED")
    txn_id = models.CharField(max_length=512, null=True, blank=True)  # Razorpay Order ID
    txn_order = models.CharField(max_length=512, null=True, blank=True)  # Razorpay Payment ID
    txn_payment_id = models.CharField(max_length=512, null=True, blank=True)
    txn_signature = models.CharField(max_length=512, null=True, blank=True)
    txn_status = models.CharField(max_length=512, null=True, blank=True)
    txn_amount_paid = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product_variation = models.ForeignKey('store.ProductVariation', on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    cgst = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
 
    @property
    def product(self):
        return self.product_variation.product

    def __str__(self):
        return self.product.product_name

class PaymentHistory(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="history", null=True, blank=True)
    order_id = models.CharField(max_length=100, db_index=True)
    event_name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    rawdata_inp = models.TextField(null=True, blank=True)
    rawdata_out = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_payment_history"

    def __str__(self):
        return f"{self.order_id} - {self.event_name}"
