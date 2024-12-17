from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Unit, Tenant, LeaseContract
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="تأكيد كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
  
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
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
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
      
class CustomUserChangeForm(UserChangeForm):
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
            'unit_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

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
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
        return cleaned_data
    def save(self, commit=True):
        contract = super().save(commit=False)
        if commit:
            contract.save()
            unit = contract.unit
            unit.status = "occupied" if not contract.is_cancelled else "available"
            unit.save()
        return contract
      