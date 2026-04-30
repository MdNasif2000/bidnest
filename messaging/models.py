from django.db import models
from accounts.models import User

class Conversation(models.Model):
    """Conversation between student and landlord"""
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_conversations')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'landlord')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation between {self.student.username} and {self.landlord.username}"
    
    def get_last_message(self):
        return self.messages.first()


class Message(models.Model):
    """Messages within a conversation"""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
