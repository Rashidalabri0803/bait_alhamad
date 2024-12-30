from django.urls import path
from . import views
from views import (
    PropertyListView,
    PropertyCreateView,
    PropertyUpdateView,
    PropertyDeleteView,
    TenantListView,
    TenantCreateView,
    TenantUpdateView,
    TenantDeleteView,
    RentalContractListView,
    RentalContractCreateView,
    RentalContractUpdateView,
    RentalContractDeleteView,
    InvoiceListView,
    PaymentCreateView,
    generate_invoice_pdf,
)
app_name = 'rentals'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('properties/', PropertyListView.as_view(), name='property_list'),
    path('properties/create/', PropertyCreateView.as_view(), name='property_create'),
    path('properties/<int:pk>/update/', PropertyUpdateView.as_view(), name='property_update'),
    path('properties/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property_delete'),
    path('tenants/', TenantListView.as_view(), name='tenant_list'),
    path('tenants/create/', TenantCreateView.as_view(), name='tenant_create'),
    path('tenants/<int:pk>/update/', TenantUpdateView.as_view(), name='tenant_update'),
    path('tenants/<int:pk>/delete/', TenantDeleteView.as_view(), name='tenant_delete'),
    path('rental-contracts/', RentalContractListView.as_view(), name='rentalcontract_list'),
    path('rental-contracts/create/', RentalContractCreateView.as_view(), name='rentalcontract_create'),
    path('rental-contracts/<int:pk>/update/', RentalContractUpdateView.as_view(), name='rentalcontract_update'),
    path('rental-contracts/<int:pk>/delete/', RentalContractDeleteView.as_view(), name='rentalcontract_delete'),
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment_create'),
    path('invoices/pdf/<int:pk>/', generate_invoice_pdf, name='generate_invoice_pdf'),
]