from django.db import models
from django.contrib.auth.models import AbstractUser

#نموذج المستخدم
class CustomUser(AbstractUser):
  USER_TYPES = [
    ('admin', 'مشرف'),
    ('tenant', 'مستأجر'),
  ]
  user_type = models.CharField(
    max_length=10, 
    choices=USER_TYPES, 
    verbose_name="نوع المستخدم"
  )
  phone_number = models.CharField(
    max_length=15,
    blank=True,
    null=True,
    verbose_name="رقم الهاتف"
  )

  class Meta:
    verbose_name = "مستخدم"
    verbose_name_plural = "المستخدمون"

class Unit(models.Model):
  UNIT_TYPE = [
    ('apartment', 'شقة'),
    ('office', 'مكتب'),
    ('shop', 'محل'),
  ]
  unit_type = models.CharField(
    max_length=20,
    choices=UNIT_TYPE,
    verbose_name="نوع الوحدة"
  )
  unit_number = models.CharField(
    max_length=50,
    unique=True,
    verbose_name="رقم الوحدة"
  )
  rent_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name="سعر الإيجار"
  )
  electricity_account = models.CharField(
    max_length=50,
    verbose_name="رقم حساب الكهرباء"
  )
  water_account = models.CharField(
    max_length=50,
    verbose_name="رقم حساب المياه"
  )

  class Meta:
    verbose_name="وحدة"
    verbose_name_plural="الوحدات"

  def __str__(self):
    return f"{self.get_unit_type_display()} - {self.unit_number}"

class Tenant(models.Model):
  user = models.OneToOneField(
    CustomUser,
    on_delete=models.CASCADE,
    verbose_name="المستخدم"
  )
  tenant_type = models.CharField(
    max_length=20,
    choices=[
      ('individual', 'فرد'),
      ('company', 'شركة')
    ],
    verbose_name="نوع المستأجر"
  )
  company_name = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    verbose_name="اسم الشركة"
  )

  class Meta:
    verbose_name="مستأجر"
    verbose_name_plural="المستأجرون"

  def __str__(self):
    return self.user.username

class Lease(models.Model):
  unit = models.ForeignKey(
    Unit,
    on_delete=models.CASCADE,
    verbose_name="الوحدة"
  )
  tenant = models.ForeignKey(
    Tenant,
    on_delete=models.CASCADE,
    verbose_name="المستأجر"
  )
  start_date = models.DateField(verbose_name="تاريخ البداية")
  end_date = models.DateField(verbose_name="تاريخ النهاية")
  electricity_previous = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name="فاتورة الكهرباء السابق"
  )
  electricity_current = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name="فاتورة الكهرباء الحالي"
  )
  water_previous = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name="فاتورة المياه السابق"
  )
  water_current = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    blank=True,
    null=True,
    verbose_name="فاتورة المياه الحالي"
  )
  agreement_note = models.TextField(
    blank=True,
    null=True,
    verbose_name="ملاحظات العقد"
  )

  class Meta:
    verbose_name="عقد إيجار"
    verbose_name_plural="عقود الإيجار"

  def __str__(self):
    return f"عقد {self.unit} - {self.tenant}"