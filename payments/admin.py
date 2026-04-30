from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'landlord', 'property', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('student__username', 'landlord__username', 'property__title', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'updated_at', 'held_in_escrow_at', 'released_at')
    
    fieldsets = (
        ('Parties', {
            'fields': ('student', 'landlord', 'property', 'bid')
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_type', 'status', 'description')
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Escrow', {
            'fields': ('held_in_escrow_at', 'released_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'amount', 'status', 'requested_by', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('payment__student__username', 'reason', 'stripe_refund_id')
    readonly_fields = ('requested_at', 'processed_at')
    
    fieldsets = (
        ('Refund Info', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_refund_id',)
        }),
        ('Request Details', {
            'fields': ('requested_by', 'requested_at', 'processed_at')
        }),
        ('Admin', {
            'fields': ('admin_notes',)
        }),
    )
