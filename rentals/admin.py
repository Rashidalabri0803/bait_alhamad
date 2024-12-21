from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Q
from datetime import date
from django.utils.html import format_html
from django.http import HttpResponse
import csv
import openpyxl
from .models import CustomUser, Unit, Tenant, LeaseContract
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

class LeaseCotnractInline(admin.TabularInline):
    model = LeaseContract
    extra = 0
    readonly_fields = ('tenant', 'start_date', 'end_date', 'is_cancelled', 'notification_sent')
    can_delete = False

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'unit_type', 'status',  'rent_price', 'electricity_account', 'water_account')
    list_filter = ('unit_type', 'status')
    search_fields = ('unit_number', 'electricity_account', 'water_account')
    ordering = ('unit_number',)
    list_editable = ('status',)
    inlines = [LeaseCotnractInline]

class LeaseContractTenantInline(admin.TabularInline):
    model = LeaseContract
    extra = 0
    readonly_fields = ('unit', 'start_date', 'end_date', 'is_cancelled')

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant_type', 'company_name')
    list_filter = ('tenant_type',)
    search_fields = ('user__username', 'user__email', 'company_name')
    inlines = [LeaseContractTenantInline]

@admin.action(description="إلغاء العقود المحددة")
def cancel_contracts(modeladmin, request, queryset):
    updated_count = queryset.update(is_cancelled=True)
    modeladmin.message_user(request, f"تم إلغاء {updated_count} عقد بنجاح")

@admin.action(description="إرسال تنبيهات انتهاء العقد")
def send_notifications(modeladmin, request, queryset):
    updated_count = 0
    for contract in queryset:
        if not contract.notification_sent:
            contract.notification_sent = True
            contract.save()
            updated_count += 1
    modeladmin.message_user(request, f"تم إرسال التنبيهات ل{updated_count} عقد بنجاح")
            
@admin.action(description="تصدير العقود الى CSV")
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lease_contracts.csv"'

    writer = csv.writer(response)
    writer.writerow(['الوحدة', 'المستاجر', 'تاريخ البداية', 'تاريخ النهاية', 'ملغى', 'تم إرسال التنبيه'])

    for contract in queryset:
        writer.writerow([
            contract.unit.unit_number,
            contract.tenant.user.username, 
            contract.start_date, 
            contract.end_date, 
            "نعم" if contract.is_cancelled else "لا",
            "نعم" if contract.notification_sent else "لا",
        ])

    return response

@admin.action(description="تصدير العقود الى Excel")
def export_to_excel(modeladmin, request, queryset):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "عقود الإيجار"
    sheet.append(['الوحدة', 'المستاجر', 'تاريخ البداية', 'تاريخ النهاية', 'ملغى', 'تم إرسال التنبيه'])
    for contract in queryset:
        sheet.append([
            contract.unit.unit_number,
            contract.tenant.user.username, 
            contract.start_date, 
            contract.end_date, 
            "نعم" if contract.is_cancelled else "لا",
            "نعم" if contract.notification_sent else "لا",
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="lease_contracts.xlsx"'
    return response

class ExpiredContractFilter(admin.SimpleListFilter):
    title = 'حالة العقد'
    parameter_name = 'contract_status'
    def lookups(self, request, model_admin):
        return (
            ('active', 'نشط'),
            ('expired', 'منتهي'),
        )
    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'active':
            return queryset.filter(end_date__gte=today, is_cancelled=False)
        elif self.value() == 'expired':
            return queryset.filter(Q(end_date__lt=today) | Q(is_cancelled=True))
        return queryset
    
@admin.register(LeaseContract)
class LeaseContractAdmin(admin.ModelAdmin):
    list_display = ('unit', 'tenant', 'start_date', 'end_date', 'is_cancelled', 'notification_sent', 'created_at')
    list_filter = ('is_cancelled', 'notification_sent', 'start_date', 'end_date')
    search_fields = ('unit__unit_number', 'tenant__user__username', 'tenant__company_name')
    ordering = ('start_date',)
    date_hierarchy = 'start_date'
    list_editable = ('is_cancelled', 'notification_sent')
    readonly_fields = ('created_at', 'updated_at')
    def status_colored(self, obj):
        if obj.is_cancelled:
            color = "red"
            status = "ملغي"
        elif obj.end_date < date.today():
            color = "orange"
            status = "منتهي"
        else:
            color = "green"
            status = "نشط"
        return format_html('<span style="color: {}">{}</span>', color, status)
    status_colored.short_description ="حالة العقد"
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('unit', 'tenant__user').prefetch_related('tenant')
    fieldsets = (
        ('معلومات الوحدة', {
            'fields': ('unit', 'tenant')
        }),
        ('تفاصيل العقد', {
            'fields': ('start_date', 'end_date', 'is_cancelled', 'notification_sent')
        }),
        ('الفواتير', {
            'fields': ('electricity_previous', 'electricity_current', 'water_previous', 'water_current')
        }),
        ('ملاحظات وأوقات', {
            'fields': ('agreement_note', 'created_at', 'updated_at')
        }),
    )
    action = [cancel_contracts, send_notifications]