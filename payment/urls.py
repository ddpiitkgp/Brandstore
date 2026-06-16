from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment, name='payment'),
    path('payment_summary/', views.payment_summary, name='payment_summary'),
    path('payment_response/', views.payment_response, name='payment_response'),
    path('payment_callback/', views.payment_callback, name='payment_callback'), 
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
]
