from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('<int:property_id>/', views.property_detail, name='property_detail'),
    path('add/', views.add_property, name='add_property'),
    path('<int:property_id>/images/', views.add_property_images, name='add_property_images'),
    path('<int:property_id>/edit/', views.edit_property, name='edit_property'),
    path('<int:property_id>/delete/', views.delete_property, name='delete_property'),
    path('images/<int:image_id>/delete/', views.delete_property_image, name='delete_property_image'),
    path('<int:property_id>/save/', views.save_property, name='save_property'),
    path('<int:property_id>/unsave/', views.unsave_property, name='unsave_property'),
    path('saved/', views.saved_properties, name='saved_properties'),
    path('requests/', views.accommodation_requests, name='accommodation_requests'),
    path('requests/add/', views.add_accommodation_request, name='add_accommodation_request'),
    path('requests/<int:request_id>/', views.accommodation_request_detail, name='accommodation_request_detail'),
    path('requests/<int:request_id>/delete/', views.delete_accommodation_request, name='delete_accommodation_request'),
]
