from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create_or_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),

    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/create/', views.contract_create_or_update, name='contract_create'),
    path('contracts/update/<int:pk>/', views.contract_create_or_update, name='contract_update'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract_detail'),
    path('contracts/delete/<int:pk>/', views.contract_delete, name='contract_delete'),

    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create_or_update, name='invoice_create'),
    path('invoices/update/<int:pk>/', views.invoice_create_or_update, name='invoice_update'),
    path('invoices/delete/<int:pk>/', views.invoice_delete, name='invoice_delete'),
    path('invoices/pay/<int:pk>/', views.pay_full_invoice, name='pay_full_invoice'),

    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),

    path('contracts/search/', views.contract_search, name='contract_search'),
    path('contracts/export/', views.export_contracts_to_csv, name='export_contracts'),
]