from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import date
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
  USER_TYPE_CHOICES = (
    ('owner', _('مالك')),
    ('tenant', _('مستأجر')),
  )
  user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name=_('نوع المستخدم'))
  phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('رقم الهاتف')),

  class Meta:
    verbose_name = _('مستخدم')
    verbose_name_plural = _('المستخدمون')

  def __str__(self):
    return self.username

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
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', verbose_name=_('المستخدم'))
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
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant', verbose_name=_('المستخدم'))
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

class RentalContract(models.Model):
  unit = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contracts', verbose_name=_('العقار'))
  tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='contracts', verbose_name=_('المستأجر'))
  start_date = models.DateField(verbose_name=_('تاريخ البدء'))
  end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
  monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('الايجار الشهري'))
  is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
  created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
  updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

  @property
  def days_left(self):
    """عدد الأيام المتبقية لانتهاء العقد"""
    if self.is_active and self.end_date:
      return max((self.end_date - date.today()).days, 0)
    return 0

  def save(self, *args, **kwargs):
    if self.end_date < date.today():
      self.is_active = False
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = _('عقد الايجار')
    verbose_name_plural = _('عقود الإيجار')

  def __str__(self):
    return f"عقد إيجار للوحدة {self.Property.Property_number} - {self.tenant.user.username}"

class Invoice(models.Model):
  STATUS_CHOICES = (
    ('pending', _('معلقة')),
    ('paid', _('مدفوعة')),
    ('overdue', _('متأخرة')),
  )
  contract = models.ForeignKey(RentalContract, on_delete=models.CASCADE, related_name='invoices', verbose_name=_('عقد الإيجار'))
  invoice_date = models.DateField(auto_now_add=True, verbose_name=_('تاريخ الفاتورة'))
  due_date = models.DateField(verbose_name=_('تاريخ الاستحقاق'))
  amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('المبلغ المستحق'))
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))

  class Meta:
    verbose_name = _('فاتورة')
    verbose_name_plural = _('الفواتير')

  def __str__(self):
    return f"فاتورة للعقد {self.contract} بمبلغ {self.amount}"

class Payment(models.Model):
  invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name=_('الفاتورة'))
  payment_date = models.DateField(auto_now_add=True, verbose_name=_('تاريخ الدفع'))
  amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('المبلغ المدفوع'))
  payment_method = models.CharField(max_length=50, choices=(('credit_card', _('بطاقة الائتمان')), ('bank_transfer', _('تحويل بنكي'))), verbose_name=_('طريقة الدفع'))

  class Meta:
    verbose_name = _('دفعة')
    verbose_name_plural = _('الدفعات')

  def __str__(self):
    return f"دفعة بقيمة {self.amount_paid} للفاتورة {self.invoice.id}"

class MaintenanceRequest(models.Model):
  STATUS_CHOICES = (
    ('pending', _('قيد الانتظار')),
    ('is_progres', _('قيد التنفيذ')),
    ('completed', _('مكتمل')),
  )
  unit = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests', verbose_name=_('الوحدة'))
  title = models.CharField(max_length=100, verbose_name=_('عنوان الطلب'))
  description = models.TextField(verbose_name=_('وصف المشكلة'))
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
  requested_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الطلب'))
  updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

  class Meta:
    verbose_name = _('طلب الصيانة')
    verbose_name_plural = _('طلبات الصيانة')

  def __str__(self):
    return f"طلب صيانة {self.title} - {self.get_status_display()}"

class Document(models.Model):
  title = models.CharField(max_length=255, verbose_name=_('عنوان المستند'))
  description = models.TextField(blank=True, null=True, verbose_name=_('وصف'))
  file = models.FileField(upload_to='documents/', verbose_name=_('ملف المستند'))
  updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ الرفع'))

  class Meta:
    verbose_name = _('مستند')
    verbose_name_plural = _('المستندات')

  def __str__(self):
    return self.title