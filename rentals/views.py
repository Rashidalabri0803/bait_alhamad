from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from .models import Property, Invoice, Tenant, RentalContract, Payment, MaintenanceRequest
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import PropertyForm, TenantForm, RentalContractForm, PaymentForm, MaintenanceRequestForm
import pandas as pd
import plotly.express as px
from plotly.offline import plot
#from django.http import HttpResponse
#from weasyprint import HTML

def dashboard(request):
  # ملخص شامل للعقارات
    total_units = Property.objects.count()
    available_units = Property.objects.filter(status='available').count()
    rented_units = Property.objects.filter(status='rented').count()
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
        Property.objects.filter(status='available').count(),
        Property.objects.filter(status='rented').count(),
        Property.objects.filter(status='maintenance').count(),
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

# عرض قائمة طلبات الصيانة
class MaintenanceRequestListView(ListView):
    model = MaintenanceRequest
    template_name = 'maintenance_requests/maintenance_request_list.html'
    context_object_name = 'requests'

# إضافة طلب صيانة جديد
class MaintenanceRequestCreateView(CreateView):
    model = MaintenanceRequest
    form_class = MaintenanceRequestForm
    template_name = 'maintenance_requests/maintenance_request_form.html'
    success_url = reverse_lazy('maintenance_request_list')

# تعديل طلب صيانة
class MaintenanceRequestUpdateView(UpdateView):
    model = MaintenanceRequest
    form_class = MaintenanceRequestForm
    template_name = 'maintenance_requests/maintenance_request_form.html'
    success_url = reverse_lazy('maintenance_request_list')

# حذف طلب صيانة
class MaintenanceRequestDeleteView(DeleteView):
    model = MaintenanceRequest
    template_name = 'maintenance_requests/maintenance_request_confirm_delete.html'
    success_url = reverse_lazy('maintenance_request_list')

def generate_reports(request):
    # 1. الايرادات
    total_revenue = Payment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0

    # 2. المصروفات (افتراض ان المصروفات تاتي من طلبات الصيانة)
    maintenance_expenses = Property.objects.annotate(total_expenses=Sum('maintenance_requests__expense_amount')).aggrgate(total=Sum('total_expenses'))['total'] or 0

    # 3. معدلات الإشغال
    total_unit = Property.objects.count()
    occupied_units = Property.objects.filter(status='rented').count()
    occupancy_rate = (occupied_units / total_unit) * 100 if total_unit > 0 else 0

    # بيانات إضافية: تحليل الايرادات عبر الاشهر
    invoices = Invoice.objects.values('invoice_date', 'amount')
    df = pd.DataFrame(invoices)
    if not df.empty:
        df['invoice_date'] = pd.to_datetime(df['invoice_date'])
        df['month'] = df['invoice_date'].dt.to_period('M')
        revenue_by_month = df.groupby('month')['amount'].sum().reset_index()
    else:
        revenue_by_month = pd.DataFrame(columns=['month', 'amount'])
    # إنشاء الرسم البياني باستخدام Plotly
    if not revenue_by_month.empty:
        fig = px.bar(revenue_by_month, x='month', y='amount', title="إيرادات الشهرية", labels={'month': 'الشهر', 'amount': 'الايرادات'},)
        revenue_chart = plot(fig, output_type='div')
    else:
        revenue_chart = "<p>لا يوجد بيانات للايرادات الشهرية.</p>"

    # تمرير البيانات إلى القالب
        context = {
            'total_revenue': total_revenue,
            'maintenance_expenses': maintenance_expenses,
            'occupancy_rate': occupancy_rate,
            'revenue_chart': revenue_chart,
        }
        return render(request, 'reports/reports.html', context)

# توليد فاتورة PDF
#def generate_invoice_pdf(request, pk):
    #invoice = get_object_or_404(Invoice, pk=pk)
    #context = {'invoice': invoice}
    #html = render(request, 'invoices/invoice_pdf.html', context)
    #pdf = HTML(string=html).write_pdf()

    #response = HttpResponse(pdf, content_type='application/pdf') if pdf else HttpResponse(status=404)
    #response['Content-Disposition'] = f'inline; filename="invoice_{invoice.id}.pdf"'