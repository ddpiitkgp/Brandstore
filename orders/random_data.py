import random
from orders.models import Payment

def run():
    payments = Payment.objects.all()
    for payment in payments:
        payment.total_price = str(round(float(payment.amount_paid) * random.uniform(0.8, 0.95), 2))
        payment.save()