from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta, date

# **نموذج المستخدم المخصص**
class CustomUser(AbstractUser):
  USER_TYPES_CHOICES = (
    ('admin', _('مشرف')),
    ('tenant', _('مستأجر')),
)
  phone_validator = RegexValidator(
    regex=r'^\+?[\d\s]{7,15}$',
    message=_("رقم الهاتف غير صالح")
  )
  user_type = models.CharField(
    max_length=10, 
    choices=USER_TYPES_CHOICES,
    verbose_name=_("نوع المستخدم")
  )
  phone_number = models.CharField(
    max_length=15,
    blank=True,
    null=True,
    validators=[phone_validator],
    verbose_name=_("رقم الهاتف")
  )

  class Meta:
    verbose_name = _("مستخدم")
    verbose_name_plural = _("المستخدمون")

  def __str__(self):
    return self.username

# **نموذج الوحدة**
class Unit(models.Model):
  UNIT_TYPE_CHOICES = [
    ('apartment', _('شقة')),
    ('office', _('مكتب')),
    ('shop', _('محل')),
  ]
  STATUS_CHOICES = [
    ('available', _('متوفر')),
    ('accupied', _('مؤجرة')),
    ('maintenance', _('تحت الصيانة')),
  ]
  unit_number = models.CharField(
    max_length=50,
    unique=True,
    verbose_name=_("رقم الوحدة")
  )
  unit_type = models.CharField(
    max_length=20,
    choices=UNIT_TYPE_CHOICES,
    verbose_name=_("نوع الوحدة")
  )
  status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='available',
    verbose_name=_("الحالة")
  )
  rent_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0.0,
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
  description = models.TextField(
    blank=True,
    null=True,
    verbose_name=_("وصف الوحدة")
  )

  class Meta:
    verbose_name=_("وحدة")
    verbose_name_plural=_("الوحدات")

  def __str__(self):
    return f"{self.get_unit_type_display()} - {self.unit_number}"

  def is_available(self):
    """التحقق إذا كانت الوحدة المتاحة"""
    return self.status == 'available'

# **نموذج المستأجر**
class Tenant(models.Model):
  user = models.OneToOneField(
    CustomUser,
    on_delete=models.CASCADE,
    relate_name='tenant',
    verbose_name=_("المستخدم")
  )
  company_name = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name=_("اسم الشركة")
  )
  commercial_registration_number = models.CharField(
    max_length=50,
    blank=True,
    null=True,
    verbose_name=_("رقم السجل التجاري")
  )

  class Meta:
    verbose_name=_("مستأجر")
    verbose_name_plural=_("المستأجرون")

  def __str__(self):
    return self.user.username

# **نموذج عقد الايجار**
class RentalContract(models.Model):
  unit = models.ForeignKey(
    Unit,
    on_delete=models.CASCADE,
    related_name='contracts',
    verbose_name=_("الوحدة")
  )
  tenant = models.ForeignKey(
    Tenant,
    on_delete=models.CASCADE,
    related_name='contracts',
    verbose_name=_("المستأجر")
  )
  start_date = models.DateField(
    verbose_name=_("تاريخ البداية")
  )
  end_date = models.DateField(
    verbose_name=_("تاريخ النهاية")
  )
  monthly_rent = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=_("الإيجار الشهري")
  )
  municipality_fees = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0,
    verbose_name=_("الرسوم البلدية")
  )
  is_cancelled = models.BooleanField(
    default=False,
    verbose_name=_("ملغى")
  )
  created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name=_("تاريخ الإنشاء")
  )
  updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name=_("تاريخ التحديث")
  )
  @property
  def days_left(self):
    """حساب عدد الايام المتبقية لانتهاء العقد"""
    if self.end_date and not self.is_cancelled:
      return max((self.end_date - date.today()).days, 0)
    return 0

  @property
  def calculate_municipality_fees(self):
    """حساب رسوم البلدية (الايجار الشهري * ١٢ * ٣٪)"""
    return self.monthly_rent * 12 * 0.03

  def clean(self):
    """التاكد من صحة تواريخ البداية والنهاية"""
    if self.end_date <= self.start_date:
      raise ValidationError(_("تاريخ النهاية يجب أن يكون أكبر من تاريخ البداية"))

  def save(self, *args, **kwargs):
    """تحديث رسوم البلدية وحالة الوحدة عند الحفظ"""
    self.calculate_municipality_fees = self.calculate_municipality_fees
    if not self.is_cancelled:
      self.unit.status = 'rented'
      self.save()
    else:
      self.unit.status = 'available'
      self.save()
    super().save(*args, **kwargs)

  class Meta:
    verbose_name=_("عقد إيجار")
    verbose_name_plural=_("عقود الإيجار")

  def __str__(self):
    return f"عقد للوحدة {self.unit} - {self.tenant}"

# **نموذج الفاتورة**
class Invoice(models.Model):
  STATUS_CHOICES = (
    ('pending', _('معلقة')),
    ('paid', _('مدفوعة')),
    ('overdue', _('متأخرة')),
  )
  contract = models.ForeignKey(
    RentalContract,
    on_delete=models.CASCADE,
    related_name='invoices',
    verbose_name=_("عقد الإيجار")
  )
  invoice_date = models.DateField(
    auto_now_add=True,
    verbose_name=_("تاريخ الفاتورة")
  )
  due_date = models.DateField(
    verbose_name=_("تاريخ الاستحقاق")
  )
  amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name=_("المبلغ المستحق")
  )
  status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='pending',
    verbose_name=_("حالة الفاتورة")
  )

  @property
  def remaining_balance(self):
    """حساب الرصيد المتبقي للفاتورة"""
    total_paid = self.payments.aggregate(total=models.Sum('amount_paid'))['total'] or 0
    return max(self.amount - total_paid, 0)

  def save(self, *args, **kwargs):
    """تحديث حالة الفاتورة بناء على الرصيد المتبقي"""
    if self.remaining_balance ==0:
      self.status = 'paid'
    elif self.due_date < date.today() and self.remaining_balance > 0:
      self.status = 'overdue'
    else:
      self.status = 'pending'
    super().save(*args, **kwargs)
    
  class Meta:
    verbose_name=_("فاتورة")
    verbose_name_plural=_("فواتير")
  def __str__(self):
    return f"فاتورة بمبلغ {self.amount} للعقد {self.contract}"

# ** نموذج الدفع **
class Payment(models.Model):
  invoice = models.ForeignKey(
    Invoice,
    on_delete=models.CASCADE,
    related_name='payments',
    verbose_name=_("الفاتورة")
  )
  payment_date = models.DateField(
    auto_now_add=True,
    verbose_name=_("تاريخ الدفع")
  )
  amount_paid = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name=_("المبلغ المدفوع")
  )
  payment_method = models.CharField(
    max_length=50,
    choices = (
      ('credit_card', _('بطاقة الائتمان')),
      ('bank_transfer', _('تحويل بنكي')),
    ),
    verbose_name=_("طريقة الدفع")
  )
  class Meta:
    verbose_name=_("دفعة")
    verbose_name_plural=_("دفعات")
  def __str__(self):
    return f"دفعة بمبلغ {self.amount_paid} للفاتورة {self.invoice.id}"