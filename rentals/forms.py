from django import forms
from .models import Property, Tenant

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