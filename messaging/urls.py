from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('unread-count/', views.unread_message_count, name='unread_message_count'),
]
