"""
Celery configuration for Event Hub.

Handles async tasks and scheduled jobs.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventhub_config.settings')

app = Celery('eventhub_config')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule - Scheduled Tasks
app.conf.beat_schedule = {
    'send-event-reminders': {
        'task': 'notifications.tasks.send_event_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    'process-payment-timeouts': {
        'task': 'payments.tasks.process_payment_timeout',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'send-post-event-surveys': {
        'task': 'notifications.tasks.send_post_event_surveys',
        'schedule': crontab(hour=20, minute=0),  # 8 PM daily
    },
}

@app.task(bind=True)
def debug_task(self):
    """Test task for debugging."""
    print(f'Request: {self.request!r}')
