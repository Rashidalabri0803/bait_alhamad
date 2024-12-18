from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput, DateInput, Textarea, NumberInput, Select, CheckboxInput
from django.db.models import Q
from dal import autocomplete
from .models import CustomUser, Unit, Tenant, LeaseContract
from datetime import date

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
      label="كلمة المرور", 
      widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
      label="تأكيد كلمة المرور", 
      widget=forms.PasswordInput(attrs={'class': 'form-control'}))
  
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active']
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'user_type': 'نوع المستخدم',
            'phone_number': 'رقم الهاتف',
        }
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'user_type': Select(attrs={'class': 'form-control'}),
            'phone_number': TextInput(attrs={'class': 'form-control'}),
        }
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("كلمة المرور وتأكيد كلمة المرور غير متطابقين")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
      
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active']
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'user_type': 'نوع المستخدم',
            'phone_number': 'رقم الهاتف',
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'unit_type', 'rent_price', 'electricity_account', 'water_account', 'status', 'description']
        labels = {
            'unit_number': 'رقم الوحدة',
            'unit_type': 'نوع الوحدة',
            'rent_price': 'سعر الإيجار',
            'electricity_account': 'رقم حساب الكهرباء',
            'water_account': 'رقم حساب المياه',
            'status': 'الحالة',
            'description': 'الوصف',
        }
        widgets = {
            'unit_number': TextInput(attrs={'class': 'form-control'}),
            'unit_type': Select(attrs={'class': 'form-control'}),
            'rent_price': NumberInput(attrs={'class': 'form-control'}),
            'electricity_account': TextInput(attrs={'class': 'form-control'}),
            'water_account': TextInput(attrs={'class': 'form-control'}),
            'status': Select(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
        }

    def clean_unit_number(self):
        unit_number = self.cleaned_data.get("unit_number")
        if Unit.objects.filter(unit_number=unit_number).exists():
            raise forms.ValidationError("رقم الوحدة موجود بالفعل")
        return unit_number

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['user', 'tenant_type', 'company_name']
        labels = {
            'user': 'المستخدم',
            'tenant_type': 'نوع المستأجر',
            'company_name': 'اسم الشركة (إن وجد)',
        }
        widgets = {
            'tenant_type': forms.Select(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_company_name(self):
        tenant_type = self.cleaned_data.get("tenant_type")
        company_name = self.cleaned_data.get("company_name")
        if tenant_type == "company" and not company_name:
            raise forms.ValidationError("يجب إدخال اسم الشركة عند اختيار نوع المستأجر كشركة")
        return company_name

class LeaseContractForm(forms.ModelForm):
    admin_notes = forms.CharField(
        label="ملاحظات الإدارة",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows':2, 'placehoder': 'إضافة ملاحظات الإدارة' }),
        required=False
    )
    class Meta:
        model = LeaseContract
        fields = ['unit', 'tenant', 'start_date', 'end_date', 'electricity_previous', 'electricity_current', 'water_previous', 'water_current', 'agreement_note', 'is_cancelled']
        labels = {
            'unit': 'الوحدة',
            'tenant': 'المستأجر',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'electricity_previous': 'فاتورة الكهرباء السابقة',
            'electricity_current': 'فاتورة الكهرباء الحالية',
            'water_previous': 'فاتورة المياه السابقة',
            'water_current': 'فاتورة المياه الحالية',
            'agreement_note': 'ملاحظات العقد',
            'is_cancelled': 'ملغي؟',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'electricity_previous': forms.NumberInput(attrs={'class': 'form-control'}),
            'electricity_current': forms.NumberInput(attrs={'class': 'form-control'}),
            'water_previous': forms.NumberInput(attrs={'class': 'form-control'}),
            'water_current': forms.NumberInput(attrs={'class': 'form-control'}),
            'agreement_note': forms.Textarea(attrs={'class': 'form-control'}),
            'is_cancelled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get('unit')
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if end_date <= start_date:
            raise forms.ValidationError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")

        if LeaseContract.objects.filter(
            Q(unit=unit) & Q(is_cancelled=False) & Q(end_date__gte=start_date).exists():
            raise forms.ValidationError("هذه الوحدة تحتوي بالفعل على عقد نشط يغطي هذه الفترة")
        return cleaned_data
        
    def save(self, commit=True):
        contract = super().save(commit=False)
        if commit:
            contract.save()
            if not contract.is_cancelled or self.cleaned_data.get("unit_status_override"):
                contract.unit.status = "occupied"
            else:
                contract.unit.status = "available"
            contract.unit.save()
        return contract