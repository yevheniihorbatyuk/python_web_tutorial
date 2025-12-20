"""Celery configuration for task queue"""

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import logging
import os

# Create Celery app
app = Celery('goit_module10')
logger = logging.getLogger(__name__)

# Configure from Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Load configuration from object
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Broker (message queue)
    broker_url='redis://localhost:6379/0',

    # Result backend (result storage)
    result_backend='redis://localhost:6379/1',

    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes warning
    task_acks_late=True,  # Acknowledge after completion

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Periodic tasks (Celery Beat)
    beat_schedule={
        'example-task-every-10-seconds': {
            'task': 'celery_tasks.tasks.example_task',
            'schedule': timedelta(seconds=10),
        },
        'example-task-daily': {
            'task': 'celery_tasks.tasks.example_task_daily',
            'schedule': crontab(hour=0, minute=0),  # Midnight daily
        },
    },
)


@app.task(bind=True)
def debug_task(self):
    """Test task to verify Celery is working"""
    logger.info("Request: %r", self.request)
