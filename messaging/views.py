from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from accounts.models import User
from .models import Conversation, Message

@login_required
def inbox(request):
    """View all conversations"""
    # Check if user has a user_type
    if not hasattr(request.user, 'user_type') or not request.user.user_type:
        django_messages.warning(request, 'Please log in as a student or landlord to access messages.')
        return redirect('home')
    
    # Get all conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(student=request.user) | Q(landlord=request.user)
    ).distinct()
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """View conversation and send messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check permissions
    if request.user != conversation.student and request.user != conversation.landlord:
        django_messages.error(request, 'Access denied.')
        return redirect('inbox')
    
    # Mark messages as read
    Message.objects.filter(
        conversation=conversation
    ).exclude(sender=request.user).update(is_read=True)
    
    chat_messages = conversation.messages.all().order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.save()  # Update updated_at
            
            # Create notification for the recipient
            from notifications.views import create_notification
            recipient = conversation.landlord if request.user == conversation.student else conversation.student
            create_notification(
                user=recipient,
                notification_type='message',
                title='New Message',
                message=f'{request.user.get_full_name() or request.user.username} sent you a message',
                link=f'/messages/{conversation.id}/'
            )
            
            # Redirect without adding any Django messages
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    context = {
        'conversation': conversation,
        'chat_messages': chat_messages,
    }
    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def start_conversation(request, user_id):
    """Start a new conversation"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Don't allow messaging yourself
    if request.user == other_user:
        django_messages.error(request, 'You cannot message yourself.')
        return redirect('inbox')
    
    # Determine student and landlord
    if request.user.user_type == 'student' and other_user.user_type == 'landlord':
        student = request.user
        landlord = other_user
    elif request.user.user_type == 'landlord' and other_user.user_type == 'student':
        student = other_user
        landlord = request.user
    elif request.user.user_type == 'student' and other_user.user_type == 'student':
        # For student-to-student messaging (e.g., from accommodation requests)
        # Use the first user as "student" and second as "landlord" for database purposes
        # This is just for the unique_together constraint
        if request.user.id < other_user.id:
            student = request.user
            landlord = other_user
        else:
            student = other_user
            landlord = request.user
    elif request.user.user_type == 'landlord' and other_user.user_type == 'landlord':
        # For landlord-to-landlord messaging
        if request.user.id < other_user.id:
            student = request.user
            landlord = other_user
        else:
            student = other_user
            landlord = request.user
    else:
        django_messages.error(request, 'Invalid conversation participants.')
        return redirect('home')
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        student=student,
        landlord=landlord
    )
    
    return redirect('conversation_detail', conversation_id=conversation.id)


@login_required
def unread_message_count(request):
    """Get unread message count (for AJAX)"""
    # Get conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(student=request.user) | Q(landlord=request.user)
    )
    
    # Count unread messages in those conversations (excluding messages sent by the user)
    count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'count': count})


@login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check permissions
    if request.user != conversation.student and request.user != conversation.landlord:
        django_messages.error(request, 'Access denied.')
        return redirect('inbox')
    
    if request.method == 'POST':
        conversation.delete()
        django_messages.success(request, 'Conversation deleted successfully.')
        return redirect('inbox')
    
    # If GET request, show confirmation
    return render(request, 'messaging/delete_conversation.html', {'conversation': conversation})
