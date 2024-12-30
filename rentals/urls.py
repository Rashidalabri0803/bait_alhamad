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
]