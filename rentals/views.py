from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
from .models import Unit, RentalContract, Invoice, Payment, Tenant
from .forms import UnitForm, RentalContractForm, InvoiceForm, PaymentForm, ContractSearchForm

def unit_list(request):
    units = Unit.objects.all()
    return render(request, 'units/unit_list.html', {'units': units})

def unit_create_or_update(request, pk=None):
  if pk:
    unit = get_object_or_404(Unit, pk=pk)
  else:
    unit = None

  if request.method == 'POST':
    form = UnitForm(request.POST, instance=unit)
    if form.is_valid():
      form.save()
      messages.success(request, 'تم حفظ الوحدة بنجاح')
      return redirect('unit_list')
    else:
      form = UnitForm(instance=unit)
    return render(request, 'units/unit_form.html', {'form': form})

def unit_delete(request, pk):
  unit = get_object_or_404(Unit, pk=pk)
  unit.delete()
  messages.success(request, 'تم حذف الوحدة بنجاح')
  return redirect('unit_list')

def rental_contract_list(request):
  contracts = RentalContract.objects.all()
  return render(request, 'contracts/contract_list.html', {'contracts': contracts})

def rental_contract_create_or_update(request, pk=None):
  if pk:
    contract = get_object_or_404(RentalContract, pk=pk)
  else:
    contract = None

  if request.method == 'POST':
    form = RentalContractForm(request.POST, instance=contract)
    if form.is_valid():
      form.save()
      messages.success(request, 'تم حفظ العقد بنجاح')
      return redirect('rental_contract_list')
    else:
      form = RentalContractForm(instance=contract)
    return render(request, 'contracts/contract_form.html', {'form': form})

def rental_contract_delete(request, pk):
  contract = get_object_or_404(RentalContract, pk=pk)
  contract.delete()
  messages.success(request, 'تم حذف العقد بنجاح')
  return redirect('rental_contract_list')

def invoice_list(request):
  invoices = Invoice.objects.all()
  return render(request, 'invoices/invoice_list.html', {'invoices': invoices})

def invoice_create_or_update(request, pk=None):
  if pk:
    invoice = get_object_or_404(Invoice, pk=pk)
  else:
    invoice = None

  if request.method == 'POST':
    form = InvoiceForm(request.POST, instance=invoice)
    if form.is_valid():
      form.save()
      messages.success(request, 'تم حفظ الفاتورة بنجاح')
      return redirect('invoice_list')
    else:
      form = InvoiceForm(instance=invoice)
    return render(request, 'invoices/invoice_form.html', {'form': form})

def invoice_delete(request, pk):
  invoice = get_object_or_404(Invoice, pk=pk)
  invoice.delete()
  messages.success(request, 'تم حذف الفاتورة بنجاح')
  return redirect('invoice_list')

def payment_list(request):
  payments = Payment.objects.all()
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

def contract_search(request):
  form = ContractSearchForm(request.GET or None)
  contracts = RentalContract.objects.select_related('tenant', 'unit')
  if form.is_valid():
    contracts = form.filter_queryset(contracts)
  return render(request, 'contracts/contract_search.html', {'form': form, 'contracts': contracts})