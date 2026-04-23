from django.db import models
from accounts.models import User
from properties.models import Property

class Bid(models.Model):
    """Bids placed by students on properties"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('countered', 'Countered'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bids')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids_placed')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, help_text="Optional message to landlord")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Counter offer from landlord
    counter_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    counter_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Allow multiple bids per student per property (one per status type)
        # unique_together = ('property', 'student', 'status')
    
    def __str__(self):
        return f"Bid by {self.student.username} on {self.property.title} - £{self.amount}"
    
    def accept(self):
        """Accept the bid"""
        self.status = 'accepted'
        self.save()
        
        # Update property current bid
        self.property.current_bid = self.amount
        self.property.save()
        
        # Reject all other pending bids for this property
        Bid.objects.filter(property=self.property, status='pending').exclude(id=self.id).update(status='rejected')
    
    def reject(self):
        """Reject the bid"""
        self.status = 'rejected'
        self.save()
        
        # If this was the current highest bid, update to next highest
        if self.amount == self.property.current_bid:
            next_highest = Bid.objects.filter(
                property=self.property,
                status__in=['pending', 'countered']
            ).order_by('-amount').first()
            
            if next_highest:
                self.property.current_bid = next_highest.amount
            else:
                self.property.current_bid = self.property.starting_bid
            self.property.save()
    
    def counter_offer(self, amount, message=''):
        """Make a counter offer"""
        self.counter_amount = amount
        self.counter_message = message
        self.status = 'countered'
        self.save()
        # Note: Counter offers do NOT update property.current_bid
        # Only actual student bids update current_bid
    
    def withdraw(self):
        """Student withdraws the bid"""
        self.status = 'withdrawn'
        self.save()
        
        # If this was the current highest bid, update to next highest
        if self.amount == self.property.current_bid:
            next_highest = Bid.objects.filter(
                property=self.property,
                status__in=['pending', 'countered']
            ).order_by('-amount').first()
            
            if next_highest:
                self.property.current_bid = next_highest.amount
            else:
                self.property.current_bid = self.property.starting_bid
            self.property.save()


class BidHistory(models.Model):
    """Track all bid changes and negotiations"""
    
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)  # e.g., 'created', 'accepted', 'countered'
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bid Histories"
    
    def __str__(self):
        return f"{self.action} - £{self.amount} on {self.bid}"
