from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_notification_read'),
    path('<int:notification_id>/go/', views.notification_redirect, name='notification_redirect'),
    path('read-all/', views.mark_all_as_read, name='mark_all_notifications_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('unread-count/', views.unread_count, name='unread_notification_count'),
]
