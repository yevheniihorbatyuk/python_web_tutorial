from django.contrib import admin
from .models import Payment, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'currency', 'status', 'method', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'reference_number')
    readonly_fields = ('transaction_id', 'created_at', 'processed_at', 'refunded_at')
    actions = ['complete_payments', 'refund_payments']

    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction_id', 'reference_number', 'booking', 'user')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'method', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at', 'refunded_at')
        }),
        ('Error Information', {
            'fields': ('error_message', 'metadata'),
            'classes': ('collapse',)
        }),
    )

    def complete_payments(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.complete()
        self.message_user(request, "Selected payments marked as completed.")

    def refund_payments(self, request, queryset):
        for payment in queryset.filter(status='completed'):
            payment.refund()
        self.message_user(request, "Selected payments refunded.")

    complete_payments.short_description = "Complete selected payments"
    refund_payments.short_description = "Refund completed payments"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'issued_at', 'is_sent', 'sent_at')
    list_filter = ('is_sent', 'issued_at')
    search_fields = ('invoice_number', 'payment__transaction_id')
    readonly_fields = ('invoice_number', 'issued_at', 'sent_at')
    actions = ['mark_invoices_as_sent']

    fieldsets = (
        ('Invoice Info', {
            'fields': ('invoice_number', 'payment', 'issued_at')
        }),
        ('Billing Details', {
            'fields': ('billing_address', 'notes')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at')
        }),
    )

    def mark_invoices_as_sent(self, request, queryset):
        for invoice in queryset.filter(is_sent=False):
            invoice.mark_as_sent()
        self.message_user(request, f"{queryset.count()} invoices marked as sent.")

    mark_invoices_as_sent.short_description = "Mark selected invoices as sent"
