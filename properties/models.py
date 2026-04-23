from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User

class Property(models.Model):
    """Property listings by landlords"""
    
    PROPERTY_TYPE_CHOICES = (
        ('whole', 'Whole Property'),
        ('room', 'Room'),
    )
    
    ROOM_TYPE_CHOICES = (
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('ensuite', 'Ensuite Room'),
        ('semi_double', 'Semi-Double Room'),
    )
    
    FURNISHING_CHOICES = (
        ('furnished', 'Furnished'),
        ('unfurnished', 'Unfurnished'),
        ('part_furnished', 'Part Furnished'),
    )
    
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, blank=True, null=True)
    
    # Location
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    campus = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Property details
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(validators=[MinValueValidator(0)])
    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES)
    square_feet = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    
    # Pricing
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    deposit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Availability
    available_from = models.DateField()
    available_until = models.DateField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True)  # e.g., "2025/2026"
    
    # Amenities
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    dishwasher = models.BooleanField(default=False)
    central_heating = models.BooleanField(default=False)
    
    # Bills
    bills_included = models.BooleanField(default=False)
    
    # Additional features
    pets_allowed = models.BooleanField(default=False)
    disabled_access = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Properties"
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class PropertyImage(models.Model):
    """Images for properties"""
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.title}"


class AccommodationRequest(models.Model):
    """Users can post their accommodation requirements"""
    
    SEARCHING_FOR_CHOICES = (
        ('just_me', 'Just me'),
        ('me_and_partner', 'Me and a partner'),
        ('me_and_friend', 'Me and a friend'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accommodation_requests')  # Field name kept for compatibility, but can be any user type
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Who's searching
    searching_for = models.CharField(max_length=20, choices=SEARCHING_FOR_CHOICES, default='just_me')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    
    # Accommodation type (property type)
    accommodation_type = models.CharField(max_length=20, choices=Property.PROPERTY_TYPE_CHOICES, blank=True)
    room_type = models.CharField(max_length=20, choices=Property.ROOM_TYPE_CHOICES, blank=True, null=True)
    
    # Preferences
    preferred_location = models.CharField(max_length=200)
    campus = models.CharField(max_length=100, blank=True)
    min_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    bedrooms_needed = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    move_in_date = models.DateField(blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True)
    
    # Requirements
    furnishing_preference = models.CharField(max_length=100, blank=True)  # Store comma-separated values
    bills_included_preferred = models.BooleanField(default=False)
    wifi_required = models.BooleanField(default=False)
    parking_required = models.BooleanField(default=False)
    garden_required = models.BooleanField(default=False)
    pets_allowed_required = models.BooleanField(default=False)
    disabled_access_required = models.BooleanField(default=False)
    
    # Buddy up feature
    interested_in_buddy_up = models.BooleanField(default=False, help_text="Interested in finding roommates to share accommodation")
    additional_requirements = models.TextField(blank=True, help_text="Any additional requirements or preferences")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.student.username}"


class SavedProperty(models.Model):
    """Students can save properties for later"""
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'property')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.student.username} saved {self.property.title}"


class ContactMessage(models.Model):
    """Store contact form submissions"""
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
