from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from properties.models import Property
from bidding.models import Bid

class Contract(models.Model):
    """Tenancy contracts"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_signatures', 'Pending Signatures'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('renewed', 'Renewed'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts_as_tenant')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts_as_landlord')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='contracts')
    bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contract details
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Contract document
    contract_document = models.FileField(upload_to='contracts/', blank=True, null=True)
    docusign_envelope_id = models.CharField(max_length=200, blank=True)
    
    # Signatures
    student_signed = models.BooleanField(default=False)
    student_signed_at = models.DateTimeField(blank=True, null=True)
    landlord_signed = models.BooleanField(default=False)
    landlord_signed_at = models.DateTimeField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    
    # Notifications
    expiry_30_day_notice_sent = models.BooleanField(default=False)
    expiry_7_day_notice_sent = models.BooleanField(default=False)
    expiry_day_notice_sent = models.BooleanField(default=False)
    
    # Terms
    terms_and_conditions = models.TextField()
    special_conditions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Contract for {self.property.title} - {self.student.username}"
    
    def is_fully_signed(self):
        return self.student_signed and self.landlord_signed
    
    def days_until_expiry(self):
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return None
    
    def is_expiring_soon(self):
        days = self.days_until_expiry()
        return days is not None and 0 <= days <= 30


class ContractDocument(models.Model):
    """Additional documents related to contracts"""
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='additional_documents')
    document_type = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='contract_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_type} for {self.contract}"


class ContractRenewal(models.Model):
    """Contract renewal requests"""
    
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    original_contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='renewal_requests')
    new_contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='renewed_from')
    
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    new_start_date = models.DateField()
    new_end_date = models.DateField()
    new_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    response_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Renewal request for {self.original_contract} - {self.status}"


class ContractTermination(models.Model):
    """Early contract termination requests"""
    
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    REASON_CHOICES = (
        ('mutual_agreement', 'Mutual Agreement'),
        ('breach_of_contract', 'Breach of Contract'),
        ('property_issues', 'Property Issues'),
        ('personal_circumstances', 'Personal Circumstances'),
        ('relocation', 'Relocation'),
        ('financial_hardship', 'Financial Hardship'),
        ('other', 'Other'),
    )
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='termination_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='termination_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_details = models.TextField()
    proposed_termination_date = models.DateField()
    notice_period_days = models.IntegerField(default=30)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    # Response from other party
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='termination_responses')
    responded_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(blank=True)
    
    # Completion
    actual_termination_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Termination request for {self.contract} by {self.requested_by.username} - {self.status}"
    
    def get_other_party(self):
        """Get the other party who needs to approve"""
        if self.requested_by == self.contract.student:
            return self.contract.landlord
        return self.contract.student
