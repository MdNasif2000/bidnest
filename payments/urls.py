from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.payment_history, name='payment_history'),
    path('initiate/<int:bid_id>/', views.initiate_payment, name='initiate_payment'),
    path('process/<int:payment_id>/', views.process_payment, name='process_payment'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/release/', views.release_payment, name='release_payment'),
    path('<int:payment_id>/refund/', views.request_refund, name='request_refund'),
]
