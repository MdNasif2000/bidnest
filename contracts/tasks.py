from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Contract

@shared_task
def check_contract_expiry():
    """Check for expiring contracts and send notifications"""
    today = timezone.now().date()
    
    # 30 days notice
    date_30_days = today + timedelta(days=30)
    contracts_30 = Contract.objects.filter(
        status='active',
        end_date=date_30_days,
        expiry_30_day_notice_sent=False
    )
    
    for contract in contracts_30:
        send_expiry_notification(contract, 30)
        contract.expiry_30_day_notice_sent = True
        contract.save()
    
    # 7 days notice
    date_7_days = today + timedelta(days=7)
    contracts_7 = Contract.objects.filter(
        status='active',
        end_date=date_7_days,
        expiry_7_day_notice_sent=False
    )
    
    for contract in contracts_7:
        send_expiry_notification(contract, 7)
        contract.expiry_7_day_notice_sent = True
        contract.save()
    
    # Expiry day
    contracts_today = Contract.objects.filter(
        status='active',
        end_date=today,
        expiry_day_notice_sent=False
    )
    
    for contract in contracts_today:
        send_expiry_notification(contract, 0)
        contract.expiry_day_notice_sent = True
        contract.status = 'expired'
        contract.save()


def send_expiry_notification(contract, days_remaining):
    """Send email notification about contract expiry"""
    if days_remaining == 0:
        subject = f'Contract Expired - {contract.property.title}'
        message = f'Your tenancy contract for {contract.property.title} has expired today.'
    else:
        subject = f'Contract Expiring in {days_remaining} Days - {contract.property.title}'
        message = f'Your tenancy contract for {contract.property.title} will expire in {days_remaining} days on {contract.end_date}.'
    
    # Send to student
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [contract.student.email],
        fail_silently=True,
    )
    
    # Send to landlord
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [contract.landlord.email],
        fail_silently=True,
    )


@shared_task
def send_contract_reminders():
    """Send reminders for pending contract signatures"""
    pending_contracts = Contract.objects.filter(status='pending_signatures')
    
    for contract in pending_contracts:
        if not contract.student_signed:
            send_mail(
                'Contract Awaiting Your Signature',
                f'Please sign the tenancy contract for {contract.property.title}.',
                settings.DEFAULT_FROM_EMAIL,
                [contract.student.email],
                fail_silently=True,
            )
        
        if not contract.landlord_signed:
            send_mail(
                'Contract Awaiting Your Signature',
                f'Please sign the tenancy contract for {contract.property.title}.',
                settings.DEFAULT_FROM_EMAIL,
                [contract.landlord.email],
                fail_silently=True,
            )
