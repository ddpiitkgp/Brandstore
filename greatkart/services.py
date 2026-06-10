import razorpay
from django.conf import settings

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


def create_order(orderno, amount):
    """
    amount should be in paisa
    """

    data = {
        "amount": amount,
        "currency": "INR",
        "orderno": orderno,
        "payment_capture": 1
    }

    return client.order.create(data)
