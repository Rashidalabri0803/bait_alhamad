from django import forms
from .models import Property, Tenant, RentalContract, Payment, MaintenanceRequest, Document, CustomUser
from django.contrib.auth.forms import PasswordChangeForm

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'الاسم الأخير',
            'email': 'البريد الإلكتروني',
            'phone_number': 'رقم الهاتف',
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        labels = {
            'old_password': 'كلمة المرور القديمة',
            'new_password1': 'كلمة المرور الجديدة',
            'new_password2': 'تأكيد كلمة المرور الجديدة'
        }

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'property_type', 'status', 'address', 'description']
        labels = {
            'name': 'اسم العقار',
            'property_type': 'نوع العقار',
            'status': 'الحالة',
            'address': 'عنوان العقار',
            'description': 'وصف العقار'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['user', 'tenant_type', 'company_name', 'commercial_registration_number', 'address', 'phone_number']
        labels = {
            'user': 'المستخدم',
            'tenant_type': 'نوع المستأجر',
            'company_name': 'اسم الشركة',
            'commercial_registration_number': 'رقم التسجيل التجاري',
            'address': 'عنوان',
            'phone_number': 'رقم الهاتف'
        }

class RentalContractForm(forms.ModelForm):
    class Meta:
        model = RentalContract
        fields = ['unit', 'tenant', 'start_date', 'end_date', 'monthly_rent']
        labels = {
            'unit': 'الوحدة',
            'tenant': 'المستأجر',
            'start_date': 'تاريخ البدء',
            'end_date': 'تاريخ النهاية',
            'monthly_rent': 'الايجار الشهري',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'amount_paid', 'payment_method']
        labels = {
            'invoice': 'الفاتورة',
            'amount_paid': 'المبلغ المدفوع',
            'payment_method': 'طريقة الدفع',
        }

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['unit', 'title', 'description', 'status']
        labels = {
            'unit': 'الوحدة',
            'title': 'عنوان الطلب',
            'description': 'وصف المشكلة',
            'status': 'الحالة',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file']
        labels = {
            'title': 'عنوان المستند',
            'description': 'وصف',
            'file': 'الملف',
        }