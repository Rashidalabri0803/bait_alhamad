from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse
import csv
from django.db.models import Sum
from .models import CustomUser, Unit, UnitImage, Tenant, RentalContract, Invoice, Payment, ContractAttachment

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

class UnitImageInline(admin.TabularInline):
    model = UnitImage
    extra = 1
    fields = ('image_preview', 'image',)
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;"/>', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة الصورة"

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'unit_type', 'status', 'rent_price', 'electricity_account', 'water_account')
    list_filter = ('unit_type', 'status')
    search_fields = ('unit_number', 'description', 'electricity_account', 'water_account')
    inlines = [UnitImageInline]
    ordering = ('unit_number',)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant_type', 'company_name', 'commercial_record_number')
    list_filter = ('tenant_type',)
    search_fields = ('user__username', 'company_name', 'commercial_record_number')

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1
    fields = ('invoice_date', 'due_date', 'amount', 'status')

class ContractAttachmentInline(admin.TabularInline):
    model = ContractAttachment
    extra = 1
    fields = ('file',)

@admin.register(RentalContract)
class RentalContractAdmin(admin.ModelAdmin):
    list_display = ('unit', 'tenant', 'start_date', 'end_date', 'days_left', 'is_cancelled')
    list_filter = ('is_cancelled', 'unit__status')
    search_fields = ('unit__unit_number', 'tenant__user__username')
    inlines = [InvoiceInline, ContractAttachmentInline]
    ordering = ('start_date',)
    actions = ['cancel_contracts']
    
    def unit_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:app_unit_change', args=[obj.unit.id]), obj.unit.unit_number)
    unit_link.short_description = "الوحدة"
    
    def tenant_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:app_tenant_change', args=[obj.tenant.id]), obj.tenant.user.username)
    tenant_link.short_description = "المستأجر"
    
    @admin.action(description="إلغاء العقود المحددة")
    def cancel_contracts(self, request, queryset):
        updated = queryset.update(is_cancelled=True)
        self.messaage_user(request, f"تم إلغاء {updated} عقد ")
        
    @admin.action(description="إعادة تنشيط العقود الملغاة")
    def reactivate_contracts(self, request, queryset):
        updated = queryset.update(is_cancelled=False)
        self.messaage_user(request, f"تم إعادة تنشيط {updated} عقد ")
    change_list_template = "admin/rental_contract_changelist.html"
    
    def get_url(self):
        urls = super().get_urls()
        custom_urls = [
            path('active-contracts-report/', self.export_active_contracts, name='active_contracts_report'),
    ]
        return custom_urls + urls
        
    def export_active_contracts(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="active_contracts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Contract Id', 'Unit', 'Tenant', 'Start Date', 'End Date'])
        contracts = RentalContract.objects.filter(is_cancelled=False)
        for contract in contracts:
            writer.writerow([contract.id, contract.unit.unit_number, contract.tenant.user.username, contract.start_date, contract.end_date])
        return response
    
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ('payment_date', 'amount_paid', 'transaction_id', 'payment_method')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('contract', 'invoice_date', 'due_date', 'amount', 'remainig_balance', 'status')
    list_filter = ('status',)
    search_fields = ('contract__unit__unit_number', 'contract__tenant__user__username')
    inlines = [PaymentInline]
    ordering = ('due_date',)
    actions = ['mark_as_paid']

    def total_payments(self, obj):
        return obj.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_payments.short_description = "إجمالي المدفوعات"

    @admin.action(description="تحديد الفواتير المدفوعة")
    def mark_as_paid(self, request, queryset)::
        updated = queryset.update(status='Paid')
        self.messaage_user(request, f"تم تحديث {updated} فاتورة الى مدفوعة")
        
    def get_url(self):
        urls = super().get_urls()
        custom_urls = [
            path('overdue-report/', self.export_active_invoices, name='overdue_invoices_report'),
    ]
        return custom_urls + urls
        
    def export_active_invoices(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="active_invoices.csv"'
        writer = csv.writer(response)
        writer.writerow(['Invoice Id', 'Contract', 'Unit', 'Tenant', 'Amount', 'Due Date', 'Status'])
        overdue_invoices = Invoice.objects.filter(status='overdue')
        for invoice in overdue_invoices:
            writer.writerow([invoice.id, invoice.contract.unit.unit_number, invoice.contract.tenant.user.username, invoice.amount, invoice.due_date, invoice.get_status_display()])
        return response

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'payment_date', 'amount_paid', 'transaction_id', 'payment_method')
    list_filter = ('payment_method',)
    search_fields = ('invoice__contract__unit__unit_number', 'transaction_id')
    ordering = ('payment_date',)

@admin.register(ContractAttachment)
class ContractAttachmentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'file', 'uploaded_at')
    search_fields = ('contract__unit__unit_number',)
    ordering = ('uploaded_at',)