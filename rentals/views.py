from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from .models import Unit, Invoice, Tenant, Property,RentalContract, Payment
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import PropertyForm, TenantForm, RentalContractForm, PaymentForm
from django.http import HttpResponse
from weasyprint import HTML

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

# عرض قائمة العقود
class RentalContractListView(ListView):
    model = RentalContract
    template_name = 'contracts/rentalcontract_list.html'
    context_object_name = 'contracts'

# إضافة عقد إيجار جديد
class RentalContractCreateView(CreateView):
    model = RentalContract
    form_class = RentalContractForm
    template_name = 'contracts/rentalcontract_form.html'
    success_url = reverse_lazy('rentalcontract_list')

# تعديل عقد إيجار
class RentalContractUpdateView(UpdateView):
    model = RentalContract
    form_class = RentalContractForm
    template_name = 'contracts/rentalcontract_form.html'
    success_url = reverse_lazy('rentalcontract_list')

# حذف عقد إيجار
class RentalContractDeleteView(DeleteView):
    model = RentalContract
    template_name = 'contracts/rentalcontract_confirm_delete.html'
    success_url = reverse_lazy('rentalcontract_list')

# عرض قائمة الفواتير
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'

# إضافة دفعة جديدة
class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('invoice_list')

# توليد فاتورة PDF
def generate_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {'invoice': invoice}
    html = render(request, 'invoices/invoice_pdf.html', context)
    pdf = HTML(string=html).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{invoice.id}.pdf"'