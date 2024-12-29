from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Prefetch
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils.timezone import now
from django.core.paginator import Paginator
from datetime import timedelta
import csv
from .models import Unit, RentalContract, Invoice, Payment, Tenant
from .forms import(
    UnitForm, RentalContractForm, InvoiceForm, PaymentForm, 
    ContractSearchForm, UnitFilterForm, InvoiceSearchForm
) 

def dashboard(request):
    invoices = Invoice.objects.select_related('content__unit', 'content__tenant')
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
  
def unit_list(request):
    form = UnitFilterForm(request.GET or None)
    units = Unit.objects.all()
    if form.is_valid():
        if form.cleaned_data['unit_type']:
          units = units.filter(unit_type=form.cleaned_data['unit_type'])
        if form.cleaned_data['status']:
          units = units.filter(status=form.cleaned_data['status'])
    paginator = Paginator(units, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'units/unit_list.html', {'units': page_obj, 'form': form})

def unit_create_or_update(request, pk=None):
  if pk:
    unit = get_object_or_404(Unit, pk=pk)
  else:
    unit = None

  if request.method == 'POST':
    form = UnitForm(request.POST, instance=unit)
    if form.is_valid():
      unit = form.save(commit=False)
      unit.created_by = request.user
      unit.save()
      messages.success(request, 'تم حفظ الوحدة بنجاح')
      return redirect('rentals:unit_list')
  else:
    form = UnitForm(instance=unit)
  return render(request, 'units/unit_form.html', {'form': form})

def unit_delete(request, pk):
  unit = get_object_or_404(Unit, pk=pk)
  if request.method == 'POST':
    unit.delete()
    messages.success(request, 'تم حذف الوحدة بنجاح')
    return redirect('rentals:unit_list')
  return render(request, 'units/unit_confirm_delete.html', {'unit': unit})

def rental_contract_list(request):
  contracts = RentalContract.objects.select_related('unit', 'tenant').all()
  paginator = Paginator(contracts, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'contracts/contract_list.html', {'contracts': page_obj})

def rental_contract_create_or_update(request, pk=None):
  if pk:
    contract = get_object_or_404(RentalContract, pk=pk)
  else:
    contract = None

  if request.method == 'POST':
    form = RentalContractForm(request.POST, instance=contract, user=request.user)
    if form.is_valid():
      contracts = form.save()
      if not pk:
        start_date = contracts.start_date
        end_date = contracts.end_date
        monthly_rent = contracts.monthly_rent

        current_date = start_date
        while current_date <= end_date:
          Invoice.objects.create(
            contract=contracts,
            invoice_date=current_date,
            due_date=current_date + timedelta(days=30),
            amount=monthly_rent
          )
          current_date += timedelta(days=30)
      messages.success(request, 'تم حفظ العقد بنجاح')
      return redirect('rentals:rental_contract_list')
  else:
    form = RentalContractForm(instance=contract, user=request.user)
  return render(request, 'contracts/contract_form.html', {'form': form})

def rental_contract_detail(request, pk):
  contract = get_object_or_404(RentalContract.objects.select_related('unit', 'tenant'), pk=pk)
  invoices = contract.invoices.all()
  total_paid = invoices.aggregate(Sum('payments__amount_paid'))['payments__amount_paid__sum'] or 0
  return render(request, 'contracts/contract_detail.html', {
    'contract': contract,
    'invoices': invoices,
    'total_paid': total_paid,
  })

def rental_contract_delete(request, pk):
  contract = get_object_or_404(RentalContract, pk=pk)
  if request.method == 'POST':
    contract.delete()
    messages.success(request, 'تم حذف العقد بنجاح')
    return redirect('rentals:rental_contract_list')
  return render(request, 'contracts/contract_confirm_delete.html', {'contract': contract})

def invoice_list(request):
  form = InvoiceSearchForm(request.GET or None)
  invoices = Invoice.objects.select_related('contract__tenant', 'contract__unit')
  if form.is_valid():
    if form.cleaned_data['status']:
      invoices = invoices.filter(status=form.cleaned_data['status'])
    if form.cleaned_data['tenant']:
      invoices = invoices.filter(contract__tenant__user__username__icontains=form.cleaned_data['tenant'])
  paginator = Paginator(invoices, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'invoices/invoice_list.html', {'invoices': page_obj, 'form': form})
  
def invoice_create_or_update(request, pk=None):
  if pk:
    invoice = get_object_or_404(Invoice, pk=pk)
  else:
    invoice = None

  if request.method == 'POST':
    form = InvoiceForm(request.POST, instance=invoice)
    if form.is_valid():
      invoice = form.save()
      messages.success(request, 'تم حفظ الفاتورة بنجاح وإرسال إشعار')
      return redirect('rentals:invoice_list')
  else:
    form = InvoiceForm(instance=invoice)
  return render(request, 'invoices/invoice_form.html', {'form': form})

def invoice_delete(request, pk):
  invoice = get_object_or_404(Invoice, pk=pk)
  if request.method == 'POST':
    invoice.delete()
    messages.success(request, 'تم حذف الفاتورة بنجاح')
    return redirect('rentals:invoice_list')
  return render(request, 'invoices/invoice_confirm_delete.html', {'invoice': invoice})

def pay_full_invoice(request, pk):
  invoice = get_object_or_404(Invoice, pk=pk)
  if invoice.remaining_balance > 0:
    Payment.objecst.create(invoice=invoice, payment_date=now(), amount_paid=invoice.remaining_balance, payment_method='cash')
    invoice.status = 'paid'
    invoice.save()
    messages.success(request, 'تم دفع الفاتورة بالكامل')
  else:
    messages.error(request, 'لا توجد مبالغ مستحقة على هذه الفاتورة')
  return redirect('rentals:invoice_list')

def payment_list(request):
    payments = Payment.objects.select_related('invoice__contract').all()
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'payments/payment_list.html', {'payments': page_obj})

def payment_create(request):
    if request.method == 'POST':
      form = PaymentForm(request.POST)
      if form.is_valid():
        payment = form.save()
        messages.success(request, 'تم تسجيل الدفع بنجاح')
        return redirect('rentals:payment_list')
    else:
      form = PaymentForm()
    return render(request, 'payments/payment_form.html', {'form': form})

def monthly_report(request):
    month = request.GET.get('month', now().month)
    year = request.GET.get('year', now().year)
    invoices = Invoice.objects.filter(invoice_date__month=month, invoice_date__year=year, status='paid')
    total_income = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'reports/monthly_report.html', {'invoices': invoices, 'total_income': total_income, 'month': month, 'year': year})
      
def contract_search(request):
  form = ContractSearchForm(request.GET or None)
  contracts = RentalContract.objects.select_related('unit', 'tenant')
  if form.is_valid():
    contracts = form.filter_queryset(contracts)
  paginator = Paginator(contracts, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'contracts/contract_list.html', {'contracts': contracts})


def export_contracts_to_csv(request):
  contracts = RentalContract.objects.select_related('tenant', 'unit').all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="contracts.csv"'
  writer = csv.writer(response)
  writer.writerow(['ID', 'الوحدة', 'المستاجر', 'تاريخ البداية', 'تاريخ النهاية','الايجار الشهري'])
  for contract in contracts:
    writer.writerow([contract.id, contract.unit.unit_number, contract.tenant.user.username, contract.start_date, contract.end_date, contract.monthly_rent])
  return response