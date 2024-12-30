from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Property(models.Model):
  PROPERTY_TYPE_CHOICES = (
    ('apartment', _('شقة')),
    ('office', _('مكتب')),
    ('shop', _('محل')),
  )
  STATUS_CHOICES = (
    ('available', _('متوفر')),
    ('rented', _('مؤجرة')),
    ( 'maintenance', _('تحت الصيانة')),
  )
  name = models.CharField(max_length=100, verbose_name=_('اسم العقار'))
  property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='available', verbose_name=_('الحالة'))
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_('الحالة'))
  address = models.TextField(verbose_name=_('عنوان العقار'))
  description = models.TextField(blank=True, null=True, verbose_name=_('وصف العقار'))
  created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
  updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

  class Meta:
    verbose_name = _('عقار')
    verbose_name_plural = _('العقارات')

  def __str__(self):
    return self.name

class Tenant(models.Model):
  TENANT_TYPE_CHOICES = (
    ('individual', _('فرد')),
    ('company', _('شركة')),
  )
  tenant_type = models.CharField(max_length=20, choices=TENANT_TYPE_CHOICES, verbose_name=_('نوع المستأجر'))
  company_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم الشركة'))
  commercial_registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('رقم التسجيل التجاري'))
  address = models.TextField(blank=True, null=True, verbose_name=_('عنوان'))
  phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('رقم الهاتف'))
  created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإضافة'))
  updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التعديل'))

  class Meta:
    verbose_name = _('مستأجر')
    verbose_name_plural = _('المستأجرون')

  def __str__(self):
    return self.user.username