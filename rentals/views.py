from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils.timezone import now
from django.core.paginator import Paginator
import csv
from datetime import timedelta
from .models import Unit, RentalContract, Invoice, Payment, Tenant
from .forms import UnitForm, RentalContractForm, InvoiceForm, PaymentForm, ContractSearchForm

def unit_list(request):
    form = UnitFilter(request.GET or None)
    units = Unit.objects.all()
    if form.is_valid():
        if form.cleaned_data['unit_type']:
          units = units.filter(unit_type=form.cleaned_data['unit_type'])
        if form.cleaned_data['status']:
          units = units.filter(status=form.cleaned_data['status'])
    paginator = Paginator(units, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'units/unit_list.html', {'form': form, 'units': units})

def unit_create_or_update(request, pk=None):
  if pk:
    unit = get_object_or_404(Unit, pk=pk)
  else:
    unit = None

  if request.method == 'POST':
    form = UnitForm(request.POST, instance=unit)
    if form.is_valid():
      unit = form.save(commit=False)
      unit.save()
      messages.success(request, 'تم حفظ الوحدة بنجاح')
      return redirect('unit_list')
    else:
      form = UnitForm(instance=unit)
    return render(request, 'units/unit_form.html', {'form': form})

def unit_delete(request, pk):
  unit = get_object_or_404(Unit, pk=pk)
  if request.method == 'POST':
    unit.delete()
    messages.success(request, 'تم حذف الوحدة بنجاح')
    return redirect('unit_list')
  return render(request, 'units/unit_confirm_delete.html', {'unit': unit})

def rental_contract_list(request):
  contracts = RentalContract.objects.select_related('unit', 'tenant').all()
  paginator = Paginator(contracts, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'contracts/contract_list.html', {'contracts': contracts})

def rental_contract_create_or_update(request, pk=None):
  if pk:
    contract = get_object_or_404(RentalContract, pk=pk)
  else:
    contract = None

  if request.method == 'POST':
    form = RentalContractForm(request.POST, instance=contract)
    if form.is_valid():
      contracts = form.save()
      if not pk:
        start_date = contracts.start_date
        end_date = contracts.end_date
        monthly_rent = contracts.monthly_rent

        current_date = start_date
        while current_date <= end_date:
          invoice = Invoice.objects.create(
            contract=contracts,
            invoice_date=current_date,
            due_date=current_date + timedelta(days30),
            amount=monthly_rent
          )
          current_date += timedelta(days=30)
      messages.success(request, 'تم حفظ العقد بنجاح')
      return redirect('rental_contract_list')
  else:
    form = RentalContractForm(instance=contract, user=request.user)
  return render(request, 'contracts/contract_form.html', {'form': form})

def rental_contract_detail(request, pk):
  contract = get_object_or_404(RentalContract.objects.select_related('unit', 'tenant'), pk=pk)
  invoices = contract.invoices.all()
  total_paid = invoice.aggregate(Sum('payments__amount_paid'))['payments__amount_paid__sum'] or 0
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
    return redirect('rental_contract_list')
  return render(request, 'contracts/contract_confirm_delete.html', {'contract': contract})

def invoice_list(request):
  status = request.GET.get('status')
  invoices = Invoice.objects.select_related('contract__unit', 'contract__tenant')
  if status:
    invoices = invoices.filter(status=status)
  paginator = Paginator(invoices, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'invoices/invoice_list.html', {'invoices': invoices})

def invoice_create_or_update(request, pk=None):
  if pk:
    invoice = get_object_or_404(Invoice, pk=pk)
  else:
    invoice = None

  if request.method == 'POST':
    form = InvoiceForm(request.POST, instance=invoice)
    if form.is_valid():
      invoice = form.save()
      send_mail(
        'فاتورة جديدة',
        f'تم انشاء فاتورة جديدة بمبلغ {invoice.amount}',
         'tugrp@example.com',
         [invoices.contract.tenant.user.email]
      )
      messages.success(request, 'تم حفظ الفاتورة بنجاح وإرسال إشعار')
      return redirect('invoice_list')
    else:
      form = InvoiceForm(instance=invoice)
    return render(request, 'invoices/invoice_form.html', {'form': form})

def invoice_delete(request, pk):
  invoice = get_object_or_404(Invoice, pk=pk)
  if request.method == 'POST':
    invoice.delete()
    messages.success(request, 'تم حذف الفاتورة بنجاح')
    return redirect('invoice_list')
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
  return redirect('invoice_list')

def contract_search(request):
  form = ContractSearchForm(request.GET or None)
  contracts = RentalContract.objects.select_related('unit', 'tenant')
  if form.is_valid():
    contracts = form.filter_queryset(contracts)
  paginator = Paginator(contracts, 10)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  return render(request, 'contracts/contract_list.html', {'contracts': contracts})

def payment_list(request):
  payments = Payment.objects.select_related('invoice__').all()
  return render(request, 'payments/payment_list.html', {'payments': payments})

def payment_create(request):
  if request.method == 'POST':
    form = PaymentForm(request.POST)
    if form.is_valid():
      payment = form.save(commit=False)
      payment.amount_paid = form.cleaned_data['amount_paid']
      payment.save()
      messages.success(request, 'تم تسجيل الدفع بنجاح')
      return redirect('payment_list')
    else:
      form = PaymentForm()
    return render(request, 'payments/payment_form.html', {'form': form})

def export_contracts_to_csv(request):
  contracts = RentalContract.objects.select_related('tenant', 'unit').all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="contracts.csv"'
  writer = csv.writer(response)
  writer.writerow(['ID', 'الوحدة', 'المستاجر', 'تاريخ البداية', 'تاريخ النهاية','الايجار الشهري'])
  for contract in contracts:
    writer.writerow([contract.id, contract.unit.unit_number, contract.tenant.user.username, contract.start_date, contract.end_date, contract.monthly_rent])
  return response