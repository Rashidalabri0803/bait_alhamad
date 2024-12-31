from django.urls import path
from .views import dashboard,PropertyListView,PropertyCreateView,PropertyUpdateView,PropertyDeleteView,TenantListView,TenantCreateView,TenantUpdateView,TenantDeleteView,RentalContractListView,RentalContractCreateView,RentalContractUpdateView,RentalContractDeleteView,InvoiceListView,PaymentCreateView, MaintenanceRequestListView, MaintenanceRequestCreateView, MaintenanceRequestUpdateView, MaintenanceRequestDeleteView, generate_reports

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
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
    path('maintenance-requests/', MaintenanceRequestListView.as_view(), name='maintenance_request_list'),
    path('maintenance-requests/create/', MaintenanceRequestCreateView.as_view(), name='maintenance_request_create'),
    path('maintenance-requests/<int:pk>/update/', MaintenanceRequestUpdateView.as_view(), name='maintenance_request_update'),
    path('maintenance-requests/<int:pk>/delete/', MaintenanceRequestDeleteView.as_view(), name='maintenance_request_delete'),
    path('reports/', generate_reports, name='generate_reports'),
    #path('invoices/pdf/<int:pk>/', generate_invoice_pdf, name='generate_invoice_pdf'),
]