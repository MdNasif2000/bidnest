from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, LandlordProfile, Review

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'profile_picture', 'is_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'email', 'phone_number')}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'course', 'year_of_study', 'document_verified')
    list_filter = ('document_verified', 'university', 'year_of_study')
    search_fields = ('user__username', 'user__email', 'university', 'student_id')
    readonly_fields = ('verification_date',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Academic Info', {'fields': ('university', 'course', 'year_of_study', 'student_id')}),
        ('Documents', {'fields': ('proof_of_study', 'id_document')}),
        ('Verification', {'fields': ('document_verified', 'verification_date')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone')}),
        ('Bio', {'fields': ('bio',)}),
    )


@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'city', 'document_verified', 'average_rating', 'total_reviews')
    list_filter = ('document_verified', 'city')
    search_fields = ('user__username', 'user__email', 'company_name', 'business_registration')
    readonly_fields = ('verification_date', 'average_rating', 'total_reviews')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Business Info', {'fields': ('company_name', 'business_registration')}),
        ('Address', {'fields': ('address', 'city', 'postcode')}),
        ('Documents', {'fields': ('id_document', 'proof_of_ownership')}),
        ('Verification', {'fields': ('document_verified', 'verification_date')}),
        ('Rating', {'fields': ('average_rating', 'total_reviews')}),
        ('Bio', {'fields': ('bio',)}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'landlord', 'rating', 'is_verified', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_featured', 'created_at')
    list_editable = ('is_featured',)
    search_fields = ('student__username', 'landlord__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_featured', 'unmark_as_featured', 'verify_reviews']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} review(s) marked as featured.')
    mark_as_featured.short_description = "Mark selected reviews as featured"
    
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} review(s) unmarked as featured.')
    unmark_as_featured.short_description = "Unmark selected reviews as featured"
    
    def verify_reviews(self, request, queryset):
        count = 0
        for review in queryset:
            if review.verify_review():
                count += 1
        self.message_user(request, f'{count} review(s) verified.')
    verify_reviews.short_description = "Verify selected reviews"
    
    fieldsets = (
        ('Review Info', {'fields': ('student', 'landlord', 'rating')}),
        ('Comment', {'fields': ('comment',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
