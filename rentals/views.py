from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Q, Count, Sum
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView, View
from .models import CustomUser, Unit, Tenant, LeaseContract
from .forms import CustomUserCreationForm, UnitForm, TenantForm, LeaseContractForm

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_units'] = Unit.objects.count()
        context['occupied_units'] = Unit.objects.filter(status='occupied').count()
        context['available_units'] = Unit.objects.filter(status='available').count()
        context['total_contracts'] = LeaseContract.objects.count()
        context['active_contracts'] = LeaseContract.objects.filter(end_date__gte=now(), is_cancelled=False).count()
        context['expired_contracts'] = LeaseContract.objects.filter(Q(end_date__lt=now()) | Q(is_cancelled=False)).count()
        context['total_income'] = LeaseContract.objects.filter(is_cancelled=False).aggregate(total_rent=Sum('unit_rent_price'))['total_rent'] or 0
        return context
        
class UserListView(ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
  
class UserCreateView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')
  
    def form_valid(self, form):
        messages.success(self.request, "تم إنشاء المستخدم بنجاح")
        return super().form_valid(form)

class UserUpadateView(UpdateView):
    model = CustomUser
    form_class = CustomUserCreationForm
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

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_parm = self.request.GET.get('filter', 'all')
        if filter_parm == 'active':
            queryset = queryset.filter(Q(end_date__gte=now()) & Q(is_cancelled=False))
        elif filter_parm == 'expired':
            queryset = queryset.filter(Q(end_date__lt=now()) & Q(is_cancelled=True))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context

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

class ExportCSVView(View):
    def get(self, request, *args, **kwargs):
        queryset = LeaseContract.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leases_contracts.csv"'

        writer = csv.writer(response)
        writer.writerow(['الوحدة', 'المستأجر', 'تاريخ البداية', 'تاريخ النهاية', 'سعر الإيجار', 'ملغي'])
        for contract in queryset:
            writer.writerow([contract.unit.unit_number, contract.user.username, contract.start_date, contract.end_date, contract.unit.rent_price,  "لا" if contract.is_cancelled else "نعم"])
            return response

class OccupiedUnitsReportView(ListView):
    model = Unit
    template_name = 'reports/occupied_units.html'
    context_object_name = 'units'

    def get_queryset(self):
        return Unit.objects.filter(status='occupied')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_units'] = Unit.objects.count()
        context['occupied_units'] = Unit.objects.filter(status='occupied').count()
        return context

def check_unit_availability(request):
    unit_id = request.GET.get('unit_id')
    is_available = not LeaseContract.objects.filter(unit_id=unit_id, end_date__gte=now(), is_cancelled=False).exists()
    return JsonResponse({'is_available': is_available})