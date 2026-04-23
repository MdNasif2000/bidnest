"""
Celery configuration for BidNest project.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bidnest.settings')

app = Celery('bidnest')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'check-contract-expiry-daily': {
        'task': 'contracts.tasks.check_contract_expiry',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    'send-contract-reminders': {
        'task': 'contracts.tasks.send_contract_reminders',
        'schedule': crontab(hour=10, minute=0),  # Run daily at 10 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
