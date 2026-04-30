from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    class Meta:
        ordering = ['-created_at']


class StudentProfile(models.Model):
    """Extended profile for students"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    university = models.CharField(max_length=200)
    course = models.CharField(max_length=200, blank=True)
    year_of_study = models.IntegerField(default=1)
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    proof_of_study = models.FileField(upload_to='documents/proof_of_study/', blank=True, null=True)
    id_document = models.FileField(upload_to='documents/ids/', blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    
    # Verification status
    document_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.university}"
    
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"


class LandlordProfile(models.Model):
    """Extended profile for landlords"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    company_name = models.CharField(max_length=200, blank=True)
    business_registration = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    
    # Verification documents
    id_document = models.FileField(upload_to='documents/landlord_ids/', blank=True, null=True)
    proof_of_ownership = models.FileField(upload_to='documents/ownership/', blank=True, null=True)
    
    # Verification status
    document_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    # Rating
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.company_name or 'Individual'}"
    
    class Meta:
        verbose_name = "Landlord Profile"
        verbose_name_plural = "Landlord Profiles"


class Review(models.Model):
    """Reviews for landlords by students"""
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    
    # New fields
    is_verified = models.BooleanField(default=False, help_text="Verified tenant who actually rented")
    is_featured = models.BooleanField(default=False, help_text="Show on home page")
    
    # Landlord response
    landlord_response = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'landlord')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['landlord', '-created_at']),
            models.Index(fields=['rating', '-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.student.username} for {self.landlord.username} - {self.rating}★"
    
    def can_edit(self, user):
        """Check if user can edit this review (within 30 days)"""
        from django.utils import timezone
        if user != self.student:
            return False
        days_since_creation = (timezone.now() - self.created_at).days
        return days_since_creation <= 30
    
    def verify_review(self):
        """Check if student actually rented from this landlord"""
        from contracts.models import Contract
        has_contract = Contract.objects.filter(
            student=self.student,
            property__landlord=self.landlord,
            status__in=['active', 'completed']  # Verify if contract is active or completed
        ).exists()
        self.is_verified = has_contract
        self.save()
        return has_contract

