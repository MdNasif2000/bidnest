from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/landlord/', views.register_landlord, name='register_landlord'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/student/', views.student_profile, name='student_profile'),
    path('profile/landlord/', views.landlord_profile, name='landlord_profile'),
    path('dashboard/landlord/', views.landlord_dashboard, name='landlord_dashboard'),
    path('landlord/<int:landlord_id>/', views.landlord_detail, name='landlord_detail'),
    path('review/add/<int:landlord_id>/', views.add_review, name='add_review'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('review/respond/<int:review_id>/', views.respond_to_review, name='respond_to_review'),
]
