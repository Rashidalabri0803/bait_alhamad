from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
#نموذج المستخدم
class CustomUser(AbstractUser):
  USER_TYPES = [
    ('admin', _('مشرف')),
    ('tenant', _('مستأجر')),
  ]
  user_type = models.CharField(
    max_length=10, 
    choices=USER_TYPES, 
    verbose_name=_("نوع المستخدم")
  )
  phone_number = models.CharField(
    max_length=15,
    blank=True,
    null=True,
    verbose_name=_("رقم الهاتف")
  )

  class Meta:
    verbose_name = _("مستخدم")
    verbose_name_plural = _("المستخدمون")

  def __str__(self):
    return self.username

class Unit(models.Model):
  UNIT_TYPE = [
    ('apartment', _('شقة')),
    ('office', _('مكتب')),
    ('shop', _('محل')),
  ]
  STATUS_CHOICES = [
    ('available', _('متوفر')),
    ('accupied', _('مشغولة')),
  ]
  unit_type = models.CharField(
    max_length=20,
    choices=UNIT_TYPE,
    verbose_name=_("نوع الوحدة")
  )
  unit_number = models.CharField(
    max_length=50,
    unique=True,
    verbose_name=_("رقم الوحدة")
  )
  rent_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_("سعر الإيجار")
  )
  electricity_account = models.CharField(
    max_length=50,
    verbose_name=_("رقم حساب الكهرباء")
  )
  water_account = models.CharField(
    max_length=50,
    verbose_name=_("رقم حساب المياه")
  )
  status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='available',
    verbose_name=_("الحالة")
  )
  description = models.TextField(
    blank=True,
    verbose_name=_("وصف الوحدة")
  )

  class Meta:
    verbose_name=_("وحدة")
    verbose_name_plural=_("الوحدات")
    indexes = [
      models.Index(fields=['unit_number'], name='unit_number_idx'),
      models.Index(fields=['status'], name='status_idx'),
    ]

  def __str__(self):
    return f"{self.get_unit_type_display()} - {self.unit_number}"

class Tenant(models.Model):
  user = models.OneToOneField(
    CustomUser,
    on_delete=models.CASCADE,
    verbose_name=_("المستخدم")
  )
  tenant_type = models.CharField(
    max_length=20,
    choices=[
      ('individual', _('فرد')),
      ('company', _('شركة'))
    ],
    verbose_name=_("نوع المستأجر")
  )
  company_name = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name=_("اسم الشركة")
  )

  class Meta:
    verbose_name=_("مستأجر")
    verbose_name_plural=_("المستأجرون")

  def __str__(self):
    return self.user.username

class LeaseContract(models.Model):
  unit = models.ForeignKey(
    Unit,
    on_delete=models.CASCADE,
    verbose_name=_("الوحدة")
  )
  tenant = models.ForeignKey(
    Tenant,
    on_delete=models.CASCADE,
    verbose_name=_("المستأجر")
  )
  start_date = models.DateField(
    verbose_name=_("تاريخ البداية")
  )
  end_date = models.DateField(
    verbose_name=_("تاريخ النهاية")
  )
  electricity_previous = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=_("فاتورة الكهرباء السابق")
  )
  electricity_current = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=_("فاتورة الكهرباء الحالي")
  )
  water_previous = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=_("فاتورة المياه السابق")
  )
  water_current = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=("فاتورة المياه الحالي")
  )
  is_cancelled = models.BooleanField(
    default=False,
    verbose_name=_("ملغى")
  )
  agreement_note = models.TextField(
    blank=True,
    null=True,
    verbose_name=_("ملاحظات العقد")
  )
  notification_sent = models.BooleanField(
    default=False,
    verbose_name=_("تم ارسال التنبيه")
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name=_("تاريخ الإنشاء")
  )
  updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name=_("تاريخ التحديث")
  )

  class Meta:
    verbose_name=_("عقد إيجار")
    verbose_name_plural=_("عقود الإيجار")
    constraints = [
      models.CheckConstraint(
        check=models.Q(end_date__gte=models.F('start_date')),
        name='valid_contract_dates'
      ),
    ]

  def __str__(self):
    return f"عقد {self.unit} - {self.tenant}"

  @property
  def tax_amount(self):
    TAX_RATE = 0.05
    return self.unit.rent_price * TAX_RATE

  @property
  def total_electricity_dues(self):
    return (self.electricity_current or 0) - (self.electricity_previous or 0)

  @property
  def total_water_dues(self):
    return (self.water_current or 0) - (self.water_previous or 0)

@receiver(post_save, sender=LeaseContract)
@receiver(post_delete, sender=LeaseContract)
def update_unit_status(sender, instance, created, **kwargs):
  unit = instance.unit
  if LeaseContract.objects.filter(unit=unit).exists():
    unit.status = 'accupied'
  else:
    unit.status = 'available'
  unit.save()