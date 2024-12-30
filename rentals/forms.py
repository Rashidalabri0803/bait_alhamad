from django import forms
from .models import Property

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