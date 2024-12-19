from django.urls import path
from .views import DashboardView, UserListView, UserCreateView, UserUpadateView, UserDeleteView, UnitListView, UnitDetialView, UnitCreateView, UnitUpdateView, UnitDeleteView, TenantListView, TenantDetialView, TenantCreateView, TenantUpdateView, TenantDeleteView, LeaseContractListView, LeaseContractDetialView, LeaseContractCreateView, LeaseContractUpdateView, LeaseContractDeleteView, ExportCSVView, OccupiedUnitsReportView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/edit/', UserUpadateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('units/', UnitListView.as_view(), name='unit-list'),
    path('units/<int:pk>/', UnitDetialView.as_view(), name='unit-detail'),
    path('units/create/', UnitCreateView.as_view(), name='unit-create'),
    path('units/<int:pk>/edit/', UnitUpdateView.as_view(), name='unit-update'),
    path('units/<int:pk>/delete/', UnitDeleteView.as_view(), name='unit-delete'),
    path('tenants/', TenantListView.as_view(), name='tenant-list'),
    path('tenants/<int:pk>/', TenantDetialView.as_view(), name='tenant-detail'),
    path('tenants/create/', TenantCreateView.as_view(), name='tenant-create'),
    path('tenants/<int:pk>/edit/', TenantUpdateView.as_view(), name='tenant-update'),
    path('tenants/<int:pk>/delete/', TenantDeleteView.as_view(), name='tenant-delete'),
    path('leases/', LeaseContractListView.as_view(), name='lease-list'),
    path('leases/<int:pk>/', LeaseContractDetialView.as_view(), name='lease-detail'),
    path('leases/create/', LeaseContractCreateView.as_view(), name='lease-create'),
    path('leases/<int:pk>/edit/', LeaseContractUpdateView.as_view(), name='lease-update'),
    path('leases/<int:pk>/delete/', LeaseContractDeleteView.as_view(), name='lease-delete'),
    path('export/csv/', ExportCSVView.as_view(), name='export-csv'),
]