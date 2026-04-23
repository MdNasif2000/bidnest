from django.contrib import admin
from .models import Contract, ContractDocument, ContractRenewal, ContractTermination

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('property', 'student', 'landlord', 'monthly_rent', 'start_date', 
                    'end_date', 'status', 'student_signed', 'landlord_signed')
    list_filter = ('status', 'student_signed', 'landlord_signed', 'start_date', 'end_date')
    search_fields = ('property__title', 'student__username', 'landlord__username')
    readonly_fields = ('created_at', 'updated_at', 'student_signed_at', 'landlord_signed_at')
    
    fieldsets = (
        ('Parties', {
            'fields': ('student', 'landlord', 'property', 'bid')
        }),
        ('Financial', {
            'fields': ('monthly_rent', 'deposit')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date')
        }),
        ('Document', {
            'fields': ('contract_document', 'docusign_envelope_id')
        }),
        ('Signatures', {
            'fields': ('student_signed', 'student_signed_at', 'landlord_signed', 'landlord_signed_at')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Notifications', {
            'fields': ('expiry_30_day_notice_sent', 'expiry_7_day_notice_sent', 'expiry_day_notice_sent')
        }),
        ('Terms', {
            'fields': ('terms_and_conditions', 'special_conditions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ContractDocument)
class ContractDocumentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('contract__property__title', 'document_type', 'description')
    readonly_fields = ('uploaded_at',)


@admin.register(ContractRenewal)
class ContractRenewalAdmin(admin.ModelAdmin):
    list_display = ('original_contract', 'requested_by', 'new_start_date', 'new_end_date', 
                    'new_monthly_rent', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('original_contract__property__title', 'requested_by__username')
    readonly_fields = ('requested_at',)



@admin.register(ContractTermination)
class ContractTerminationAdmin(admin.ModelAdmin):
    list_display = ('contract', 'requested_by', 'reason', 'proposed_termination_date', 
                    'status', 'requested_at')
    list_filter = ('status', 'reason', 'requested_at')
    search_fields = ('contract__property__title', 'requested_by__username', 'reason_details')
    readonly_fields = ('requested_at', 'responded_at')
    
    fieldsets = (
        ('Request', {
            'fields': ('contract', 'requested_by', 'requested_at')
        }),
        ('Details', {
            'fields': ('reason', 'reason_details', 'proposed_termination_date', 'notice_period_days')
        }),
        ('Response', {
            'fields': ('status', 'responded_by', 'responded_at', 'response_message')
        }),
        ('Completion', {
            'fields': ('actual_termination_date',)
        }),
    )
