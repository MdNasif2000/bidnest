from django.contrib import admin
from .models import Property, PropertyImage, AccommodationRequest, SavedProperty, ContactMessage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_primary')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'city', 'property_type', 'rent_per_month', 
                    'current_bid', 'is_active', 'views_count', 'created_at')
    list_filter = ('property_type', 'furnishing', 'is_active', 'is_featured', 'city', 'academic_year')
    search_fields = ('title', 'description', 'address', 'city', 'postcode')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('landlord', 'title', 'description', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'postcode', 'campus', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'furnishing', 'square_feet')
        }),
        ('Pricing', {
            'fields': ('starting_bid', 'current_bid', 'rent_per_month', 'deposit')
        }),
        ('Availability', {
            'fields': ('available_from', 'available_until', 'academic_year')
        }),
        ('Amenities', {
            'fields': ('wifi', 'parking', 'garden', 'gym', 'laundry', 'dishwasher', 
                      'central_heating', 'bills_included')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('property__title', 'caption')


@admin.register(AccommodationRequest)
class AccommodationRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'preferred_location', 'accommodation_type', 
                    'move_in_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'accommodation_type', 'academic_year', 'created_at')
    search_fields = ('title', 'description', 'student__username', 'preferred_location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ('student', 'property', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('student__username', 'property__title')
    readonly_fields = ('saved_at',)



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual addition of contact messages
        return False
