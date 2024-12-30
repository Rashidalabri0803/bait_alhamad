from django.db import models
from django.utils.translation import gettext_lazy as _

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