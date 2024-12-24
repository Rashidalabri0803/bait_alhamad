from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timezone

#نموذج المستخدم
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

class Unit(models.Model):
  UNIT_TYPE_CHOICES = [
    ('apartment', _('شقة')),
    ('office', _('مكتب')),
    ('shop', _('محل')),
  ]
  STATUS_CHOICES = [
    ('available', _('متوفر')),
    ('accupied', _('مؤجرة')),
  ]
  unit_type = models.CharField(
    max_length=20,
    choices=UNIT_TYPE_CHOICES,
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
  status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='available',
    verbose_name=_("الحالة")
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

class UnitImage(models.Model):
  unit = models.ForeignKey(
    Unit,
    on_delete=models.CASCADE,
    related_name='images',
    verbose_name=_("الوحدة")
  )
  image = models.ImageField(
    upload_to='unit_images/',
    verbose_name=_("صورة الوحدة")
  )
  uploaded_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name=_("تاريخ الرفع")
  )
  class Meta:
    verbose_name=_("صورة الوحدة")
    verbose_name_plural=_("صور الوحدات")
  def __str__(self):
    return f"{self.unit.unit_number}"

class Tenant(models.Model):
  user = models.OneToOneField(
    CustomUser,
    on_delete=models.CASCADE,
    verbose_name=_("المستخدم")
  )
  tenant_type = models.CharField(
    max_length=50,
    verbose_name=_("نوع المستأجر")
  )
  company_name = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name=_("اسم الشركة")
  )
  commercial_record_number = models.CharField(
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
    blank=True,
    null=True,
    verbose_name=_("رسوم البلدية")
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
  notes = models.TextField(
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
  @property
  def days_left(self):
    if self.end_date and not self.is_cancelled:
      return max((self.end_date - now().date()).days, 0)
    return 0
  @property
  def calculate_monthly_rent(self):
    if not self.monthly_rent and self.unit:
      return self.unit.rent_price
    return self.monthly_rent
  @property
  def calculate_municipality_fees(self):
    monthly_rent = self.calculate_monthly_rent
    if monthly_rent:
      return monthly_rent * 12 * 0.03
    return 0
  def clean(self):
    if self.end_date <= self.start_date:
      raise ValidationError(_("تاريخ النهاية يجب أن يكون بعد تاريخ البداية"))
    if self.unit.status == 'rented':
      raise ValidationError(_("هذه الوحدة مؤجرة بالفعل"))
  def save(self, *args, **kwargs):
    self.municipality_fees = self.calculate_municipality_fees
    if not self.is_cancelled:
      self.unit.status = 'rented'
      self.unit.save()
    else:
      self.unit.status = 'available'
      self.unit.save()
    super().save(*args, **kwargs)

  class Meta:
    verbose_name=_("عقد إيجار")
    verbose_name_plural=_("عقود الإيجار")

  def __str__(self):
    return f"عقد {self.unit} - {self.tenant}"

class Invoice(models.Model):
  STATUS_CHOICES = (
    ('pending', _('مستحقة')),
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
  is_paid = models.BooleanField(
    default=False,
    verbose_name=_("مدفوع")
  )
  @property
  def remaining_days(self):
    total_paid = self.payments.aggregate(total.Sum('amount_paid'))['total'] or 0
    return max(self.amount - total_paid, 0)
  def save(self, *args, **kwargs):
    if self.remaining_balance == 0:
      self.status = 'paid'
    elif self.due_date < now().date() and self.remaining_balance > 0:
      self.status = 'overdue'
    else:
      self.status = 'pending'
    super().save(*args, **kwargs)
  class Meta:
    verbose_name=_("فاتورة")
    verbose_name_plural=_("فواتير")
  def __str__(self):
    return f"فاتورة {self.contract} - {self.invoice_date}"

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
  transaction_id = models.CharField(
    max_length=50,
    blank=True,
    null=True,
    verbose_name=_("رقم المعاملة")
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
    return f"دفعة {self.amount_paid} - {self.invoice.id}"

class ContractAttachment(models.Model):
  contract = models.ForeignKey(
    RentalContract,
    on_delete=models.CASCADE,
    related_name='attachments',
    verbose_name=_("عقد الإيجار")
  )
  file = models.FileField(
    upload_to='attachments/',
    verbose_name=_("الملف")
  )
  uploaded_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name=_("تاريخ الرفع")
  )
  class Meta:
    verbose_name=_("مرفق")
    verbose_name_plural=_("مرفقات")
  def __str__(self):
    return f"مرفق {self.contract}"