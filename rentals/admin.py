from django.contrib import admin
from .models import CustomeUser, Unit, Tenant, LeaseContract

@admin.register(CustomeUser)
class CustomeUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'unit_type', 'status',  'rent_price', 'electricity_account', 'water_account')
    list_filter = ('unit_type', 'status')
    search_fields = ('unit_number', 'electricity_account', 'water_account')
    ordering = ('unit_number',)
    list_editable = ('status',)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant_type', 'company_name')
    list_filter = ('tenant_type',)
    search_fields = ('user__username', 'user__email', 'company_name')

@admin.register(LeaseContract)
class LeaseContractAdmin(admin.ModelAdmin):
    list_display = ('unit', 'tenant', 'start_date', 'end_date', 'is_cancelled', 'notification_sent', 'created_at')
    list_filter = ('is_cancelled', 'notification_sent', 'start_date', 'end_date')
    search_fields = ('unit__unit_number', 'tenant__user__username', 'tenant__company_name')
    ordering = ('start_date',)
    date_hierarchy = 'start_date'
    list_editable = ('is_cancelled', 'notification_sent')
    readonly_fields = ('created_at', 'updated_at')
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