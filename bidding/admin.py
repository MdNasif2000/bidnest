from django.contrib import admin
from .models import Bid, BidHistory

class BidHistoryInline(admin.TabularInline):
    model = BidHistory
    extra = 0
    readonly_fields = ('action', 'amount', 'note', 'created_by', 'created_at')
    can_delete = False

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('property', 'student', 'amount', 'status', 'counter_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'student__username', 'message')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BidHistoryInline]
    
    fieldsets = (
        ('Bid Info', {
            'fields': ('property', 'student', 'amount', 'message', 'status')
        }),
        ('Counter Offer', {
            'fields': ('counter_amount', 'counter_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BidHistory)
class BidHistoryAdmin(admin.ModelAdmin):
    list_display = ('bid', 'action', 'amount', 'created_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('bid__property__title', 'bid__student__username', 'note')
    readonly_fields = ('created_at',)
