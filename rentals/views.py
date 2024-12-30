from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Unit, Invoice, Tenant, Property
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import PropertyForm, TenantForm

def dashboard(request):
  # ملخص شامل للعقارات
    total_units = Unit.objects.count()
    available_units = Unit.objects.filter(status='available').count()
    rented_units = Unit.objects.filter(status='rented').count()
  # ملخص شامل للمستأجرون
    total_tenants = Tenant.objects.count()
  # الايجارات المستحقة
    total_invoices = Invoice.objects.count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    total_income = Invoice.objects.filter(status= 'paid').aggregate(total=Sum('amount'))['total'] or 0
    # chart.js البيانات لتكامل الرسوم البيانية مع
    unit_data = {
      'labels': ['متوفر', 'مؤجرة', 'تحت الصيانة'],
      'data': [
        Unit.objects.filter(status='available').count(),
        Unit.objects.filter(status='rented').count(),
        Unit.objects.filter(status='maintenance').count(),
      ]
    }

    overdue_data = {
      'labels': ['متأخرة', 'مدفوعة', 'معلق'],
      'data': [
        Invoice.objects.filter(status='overdue').count(),
        Invoice.objects.filter(status='paid').count(),
        Invoice.objects.filter(status='pending').count(),
      ]
    }

    context = {
        'total_units': total_units,
        'available_units': available_units,
        'rented_units': rented_units,
        'total_tenants': total_tenants,
        'total_invoices': total_invoices,
        'overdue_invoices': overdue_invoices,
        'total_income': total_income,
        'unit_data': unit_data,
        'overdue_data': overdue_data,
    }
    return render(request, 'dashboard.html', context)

# عرض قائمة العقارات
class PropertyListView(ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'

# إضافة عقار جديد
class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('property_list')

# تعديل عقار
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('property_list')

# حذف عقار
class PropertyDeleteView(DeleteView):
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('property_list')

# عرض قائمة المستأجرين
class TenantListView(ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'

# إضافة مستأجر جديد
class TenantCreateView(CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenant_list')

# تعديل مستأجر
class TenantUpdateView(UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenant_list')

# حذف مستأجر
class TenantDeleteView(DeleteView):
    model = Tenant
    template_name = 'tenants/tenant_confirm_delete.html'
    success_url = reverse_lazy('tenant_list')