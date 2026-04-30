from django.db import models
from accounts.models import User
from properties.models import Property
from bidding.models import Bid

class Payment(models.Model):
    """Payment transactions"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('held_in_escrow', 'Held in Escrow'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('rent', 'Rent'),
        ('full_payment', 'Full Payment'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    bid = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe details
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)
    
    # Escrow
    held_in_escrow_at = models.DateTimeField(blank=True, null=True)
    released_at = models.DateTimeField(blank=True, null=True)
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment of £{self.amount} from {self.student.username} to {self.landlord.username}"


class Refund(models.Model):
    """Refund requests and processing"""
    
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    )
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    stripe_refund_id = models.CharField(max_length=200, blank=True)
    
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refund_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Refund request for £{self.amount} - {self.status}"
