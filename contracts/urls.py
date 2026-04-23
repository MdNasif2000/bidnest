from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_contracts, name='my_contracts'),
    path('<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('generate/<int:bid_id>/', views.generate_contract, name='generate_contract'),
    path('<int:contract_id>/sign/', views.sign_contract, name='sign_contract'),
    path('<int:contract_id>/renew/', views.request_renewal, name='request_renewal'),
    path('<int:contract_id>/upload/', views.upload_document, name='upload_contract_document'),
    path('<int:contract_id>/terminate/', views.request_termination, name='request_termination'),
    path('<int:contract_id>/termination/<int:termination_id>/', views.termination_detail, name='termination_detail'),
]
