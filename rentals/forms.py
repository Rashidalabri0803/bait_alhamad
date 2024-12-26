from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import CustomUser, Tenant, Unit, RentalContract, Invoice, Payment

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'phone_number', 'is_active']
        labels = {
            'username': _('اسم المستخدم'),
            'email': _('البريد الإلكتروني'),
            'user_type': _('نوع المستخدم'),
            'phone_number': _('رقم الهاتف'),
            'is_active': _('نشط'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _('أدخل اسم المستخدم')}),
            'email': forms.EmailInput(attrs={'placeholder': _('أدخل البريد الإلكتروني')}),
            'user_type': forms.Select(attrs={'placeholder': _('أدخل نوع المستخدم')}),
            'phone_number': forms.TextInput(attrs={'placeholder': _('أدخل رقم الهاتف مع رمز الدولة')}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number and not phone_number.startswith('+'):
            raise forms.ValidationError(_("رقم الهاتف يجب بدء بـ +"))
        return phone_number

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'unit_type', 'status', 'rent_price', 'electricity_account', 'water_account', 'description']
        labels = {
            'unit_number': _('رقم الوحدة'),
            'unit_type': _('نوع الوحدة'),
            'status': _('الحالة'),
            'rent_price': _('سعر الإيجار'),
            'electricity_account': _('حساب الكهرباء'),
            'water_account': _('حساب المياه'),
            'description': _('الوصف'),
        }
        widgets = {
            'unit_number': forms.TextInput(attrs={'placeholder': _('أدخل رقم الوحدة')}),
            'description': forms.Textarea(attrs={'placeholder': _('أدخل الوصف')}),
        }

class RentalContractForm(forms.ModelForm):
    municipality_fees = forms.DecimalField(label=_('رسوم البلدية'), required=False, disabled=True)
    class Meta:
        model = RentalContract
        fields = ['unit', 'tenant', 'start_date', 'end_date', 'monthly_rent', 'municipality_fees',  'is_cancelled']
        labels = {
            'unit': _('الوحدة'),
            'tenant': _('المستأجر'),
            'start_date': _('تاريخ البدء'),
            'end_date': _('تاريخ النهاية'),
            'monthly_rent': _('الإيجار الشهري'),
            'municipality_fees': _('رسوم البلدية'),
            'is_cancelled': _('ملغي'),
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date'}),
            'end_date': forms.DateInput(attrs={'typr':'date'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.filter(status='available')
        if self.instance.pk:
            self.fields['municipality_fees'].initial = self.instance.monthly_rent * 12 * 0.03
        if user and not user.is_superuser:
            self.fields.pop('is_cancelled')
            
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(_("تاريخ النهاية يجب أن يكون أكبر من تاريخ البداية"))
        unit = cleaned_data.get('unit')
        if unit and start_date and end_date:
            overlapping_contracts = RentalContract.objects.filter(
                unit=unit,
                end_date__gte=start_date,
                start_date__lte=end_date,
                is_cancelled=False
            ).exclude(pk=self.instance.pk)
            if overlapping_contracts.exists():
               raise forms.ValidationError(_("الوحدة لديها عقود أخرى متداخلة في هذه الفترة"))
        return cleaned_data

class InvoiceForm(forms.ModelForm):
    remaining_balance = forms.DecimalField(label=_('الرصيد المتبقي'), required=False, disabled=True)
    class Meta:
        model = Invoice
        fields = ['contract', 'invoice_date', 'due_date', 'amount', 'status', 'remaining_balance']
        labels = {
            'contract': _('عقد الايجار'),
            'invoice_date': _('تاريخ الفاتورة'),
            'due_date': _('تاريخ الاستحقاق'),
            'amount': _('المبلغ'),
            'status': _('الحالة'),
            'remaining_balance': _('الرصيد المتبقي'),
        }
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type':'date'}),
            'due_date': forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['remaining_balance'].initial = self.instance.remaining_balance

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date and due_date < self.cleaned_data.get('invoice_date'):
            raise forms.ValidationError(_("تاريخ الاستحقاق يجب أن يكون بعد  تاريخ الفاتورة"))
        return due_date

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'payment_date', 'amount_paid', 'transaction_id', 'payment_method']
        labels = {
            'invoice': _('عقد الايجار'),
            'payment_date': _('تاريخ الدفع'),
            'amount_paid': _('المبلغ المدفوع'),
            'transaction_id': _('رقم المعاملة'),
            'payment_method': _('طريقة الدفع'),
        }
        widgets = {
            'payment_date': forms.DateInput(attrs={'type':'date'}),
            'transaction_id': forms.TextInput(attrs={'placeholder': _('أدخل رقم المعاملة')})
        }

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get('amount_paid')
        invoice = self.cleaned_data.get('invoice')
        if amount_paid and amount_paid <= 0:
            raise forms.ValidationError(_("المبلغ المدفوع يجب أن يكون أكبر من صفر"))
        if amount_paid and invoice and amount_paid > invoice.remaining_balance:
            raise forms.ValidationError(_("تاريخ الدفع لا يمكن أن يكون قبل تاريخ الفاتورة"))
        return amount_paid
        
    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')
        invoice = self.cleaned_data.get('invoice')
        if payment_date and invoice and payment_date < invoice.invoice_date:
            raise forms.ValidationError(_("تاريخ الدفع لا يمكن أن يكون قبل تاريخ الفاتورة"))
        return payment_date

class ContractSearchForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False, label=_("المستأجر"))
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=False, label=_("الوحدة"))
    start_date = forms.DateField(required=False, label=_("تاريخ البدء"))
    end_date = forms.DateField(required=False, label=_("تاريخ النهاية"))

    def filter_queryset(self, queryset):
        tenant = self.cleaned_data.get('tenant')
        unit = self.cleaned_data.get('unit')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if tenant:
            queryset = queryset.filter(tenant=tenant)
        if unit:
            queryset = queryset.filter(unit=unit)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        return queryset
        
class ContractFilterForm(forms.Form):
    start_date = forms.DateField(label=_('تاريخ البدء'), required=False)
    end_date = forms.DateField(label=_('تاريخ النهاية'), required=False)
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_("تاريخ البداية يجب أن يكون قبل  تاريخ النهاية"))