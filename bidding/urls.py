from django.urls import path
from . import views

urlpatterns = [
    path('place/<int:property_id>/', views.place_bid, name='place_bid'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('received/', views.received_bids, name='received_bids'),
    path('<int:bid_id>/', views.bid_detail, name='bid_detail'),
    path('<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
    path('<int:bid_id>/reject/', views.reject_bid, name='reject_bid'),
    path('<int:bid_id>/counter/', views.counter_offer, name='counter_offer'),
    path('<int:bid_id>/withdraw/', views.withdraw_bid, name='withdraw_bid'),
    path('<int:bid_id>/accept-counter/', views.accept_counter_offer, name='accept_counter_offer'),
]
