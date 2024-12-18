from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import CustomUser, Unit, Tenant, LeaseContract
from .forms import CustomUserForm, UnitForm, TenantForm, LeaseContractForm

class UserListView(ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
  
class UserCreateView(CreateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')
  
    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء المستخدم بنجاح")
        return super().form_valid(form)

class UserUpadateView(UpdateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات المستخدم بنجاح")
        return super().form_valid(form)

class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "تم حذف المستخدم بنجاح")
        return super().delete(request, *args, **kwargs)

class UnitListView(ListView):
    model = Unit
    template_name = 'units/unit_list.html'
    context_object_name = 'units'
    paginate_by = 10

class UnitDetialView(DetailView):
    model = Unit
    template_name = 'units/unit_detail.html'
    context_object_name = 'unit'

class UnitCreateView(CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'units/unit_form.html'
    success_url = reverse_lazy('unit-list')

    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء الوحدة بنجاح")
        return super().form_valid(form)

class UnitUpdateView(UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'units/unit_form.html'
    success_url = reverse_lazy('unit-list')

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات الوحدة بنجاح")
        return super().form_valid(form)

class UnitDeleteView(DeleteView):
    model = Unit
    template_name = 'units/unit_confirm_delete.html'
    success_url = reverse_lazy('unit-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "تم حذف الوحدة بنجاح")
        return super().delete(request, *args, **kwargs)

class TenantListView(ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 10

class TenantDetialView(DetailView):
    model = Tenant
    template_name = 'tenants/tenant_detail.html'
    context_object_name = 'tenant'

class TenantCreateView(CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenant-list')

    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء المستأجر بنجاح")
        return super().form_valid(form)

class TenantUpdateView(UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenant-list')

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات المستأجر بنجاح")
        return super().form_valid(form)

class TenantDeleteView(DeleteView):
    model = Tenant
    template_name = 'tenants/tenant_confirm_delete.html'
    success_url = reverse_lazy('tenant-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "تم حذف المستأجر بنجاح")
        return super().delete(request, *args, **kwargs)

class LeaseContractListView(ListView):
    model = LeaseContract
    template_name = 'leases/lease_contract_list.html'
    context_object_name = 'lease-contracts'
    paginate_by = 10

class LeaseContractDetialView(DetailView):
    model = LeaseContract
    template_name = 'leases/lease_contract_detail.html'
    context_object_name = 'lease'

class LeaseContractCreateView(CreateView):
    model = LeaseContract
    form_class = LeaseContractForm
    template_name = 'leases/lease_contract_form.html'
    success_url = reverse_lazy('lease-list')

    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء عقد الايجار بنجاح")
        return super().form_valid(form)

class LeaseContractUpdateView(UpdateView):
    model = LeaseContract
    form_class = LeaseContractForm
    template_name = 'leases/lease_contract_form.html'
    success_url = reverse_lazy('lease-list')

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات العقد الايجار بنجاح")
        return super().form_valid(form)

class LeaseContractDeleteView(DeleteView):
    model = LeaseContract
    template_name = 'leases/lease_contract_confirm_delete.html'
    success_url = reverse_lazy('lease-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "تم حذف العقد الايجار بنجاح")
        return super().delete(request, *args, **kwargs)