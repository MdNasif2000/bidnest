from django.db import models
from accounts.models import User

class Notification(models.Model):
    """In-app notifications"""
    
    NOTIFICATION_TYPES = (
        ('bid_received', 'Bid Received'),
        ('bid_accepted', 'Bid Accepted'),
        ('bid_rejected', 'Bid Rejected'),
        ('bid_countered', 'Bid Countered'),
        ('message_received', 'Message Received'),
        ('payment_received', 'Payment Received'),
        ('payment_released', 'Payment Released'),
        ('contract_generated', 'Contract Generated'),
        ('contract_signed', 'Contract Signed'),
        ('contract_expiring', 'Contract Expiring'),
        ('contract_expired', 'Contract Expired'),
        ('renewal_requested', 'Renewal Requested'),
        ('property_saved', 'Property Saved'),
        ('review_received', 'Review Received'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
