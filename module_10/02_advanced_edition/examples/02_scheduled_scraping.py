"""
Example 2: Scheduled Scraping with Celery Beat

This example demonstrates automated scraping on a schedule:
1. Configure Celery Beat for periodic tasks
2. Run scraping at specified times
3. Track scheduled execution
4. Handle missed schedules
5. Monitor job frequency

Time to complete: 20 minutes
Difficulty: Intermediate
"""

import os
import sys
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from celery import shared_task
from celery.schedules import crontab
from code.celery_tasks.config import app
from code.django_integration.models import ScrapeJob, ScrapingSchedule
from code.celery_tasks.tasks import long_task

logger = logging.getLogger(__name__)


# ============================================================================
# PART 1: Celery Beat Configuration
# ============================================================================
class CeleryBeatScheduleManager:
    """
    Manages Celery Beat periodic task schedules.

    This class provides utilities to configure and manage when Scrapy tasks
    run automatically without human intervention.
    """

    @staticmethod
    def configure_beat_schedule():
        """
        Configure Celery Beat schedule for periodic scraping tasks.

        This configuration runs in the Celery configuration, not here.
        See: code/celery_tasks/config.py for actual beat_schedule
        """
        schedule_config = {
            # Daily scraping at 2 AM
            'scrape-quotes-daily': {
                'task': 'code.celery_tasks.tasks.scrape_quotes_task',
                'schedule': crontab(hour=2, minute=0),
                'args': (),
                'kwargs': {},
                'options': {'queue': 'default'},
            },

            # Every 6 hours (0, 6, 12, 18)
            'scrape-quotes-6hourly': {
                'task': 'code.celery_tasks.tasks.scrape_quotes_task',
                'schedule': timedelta(hours=6),
            },

            # Twice daily at 6 AM and 6 PM
            'scrape-quotes-morning': {
                'task': 'code.celery_tasks.tasks.scrape_quotes_task',
                'schedule': crontab(hour=6, minute=0),
            },

            'scrape-quotes-evening': {
                'task': 'code.celery_tasks.tasks.scrape_quotes_task',
                'schedule': crontab(hour=18, minute=0),
            },

            # Weekly on Monday at midnight
            'scrape-books-weekly': {
                'task': 'code.celery_tasks.tasks.scrape_books_task',
                'schedule': crontab(day_of_week=0, hour=0, minute=0),
            },

            # Every 30 minutes during business hours (9-17)
            'scrape-quotes-frequent': {
                'task': 'code.celery_tasks.tasks.scrape_quotes_task',
                'schedule': crontab(minute='*/30', hour='9-17'),
            },

            # Cleanup old data daily at 3 AM
            'cleanup-old-data': {
                'task': 'code.celery_tasks.tasks.cleanup_old_quotes_task',
                'schedule': crontab(hour=3, minute=0),
            },
        }

        return schedule_config

    @staticmethod
    def get_schedule_display():
        """Get human-readable schedule descriptions"""
        schedules = {
            'crontab(hour=2, minute=0)': 'Daily at 2:00 AM',
            'timedelta(hours=6)': 'Every 6 hours (0:00, 6:00, 12:00, 18:00)',
            'crontab(hour=6, minute=0)': 'Every day at 6:00 AM',
            'crontab(hour=18, minute=0)': 'Every day at 6:00 PM',
            'crontab(day_of_week=0, hour=0, minute=0)': 'Every Monday at midnight',
            'crontab(minute="*/30", hour="9-17")': 'Every 30 min (9 AM - 5 PM, weekdays)',
        }
        return schedules


# ============================================================================
# PART 2: Schedule Management Database Model
# ============================================================================
class ScheduleManager:
    """
    Manage scraping schedules stored in database.

    Provides an interface to enable/disable schedules and track execution.
    """

    @staticmethod
    def get_or_create_schedule(
        spider_name: str,
        frequency: str = 'DAILY',
        is_enabled: bool = True
    ) -> ScrapingSchedule:
        """
        Get or create a scraping schedule.

        Args:
            spider_name: Name of spider (quotes, books)
            frequency: How often to run (HOURLY, DAILY, WEEKLY, MONTHLY)
            is_enabled: Whether schedule is active

        Returns:
            ScrapingSchedule model instance
        """
        schedule, created = ScrapingSchedule.objects.get_or_create(
            spider_name=spider_name,
            defaults={
                'frequency': frequency,
                'is_enabled': is_enabled,
                'last_run': None,
                'next_run': None,
            }
        )

        if created:
            logger.info(f'Created schedule for {spider_name}: {frequency}')

        return schedule

    @staticmethod
    def enable_schedule(spider_name: str):
        """Enable a schedule"""
        try:
            schedule = ScrapingSchedule.objects.get(spider_name=spider_name)
            schedule.is_enabled = True
            schedule.save()
            logger.info(f'Enabled schedule: {spider_name}')
            return True
        except ScrapingSchedule.DoesNotExist:
            logger.warning(f'Schedule not found: {spider_name}')
            return False

    @staticmethod
    def disable_schedule(spider_name: str):
        """Disable a schedule"""
        try:
            schedule = ScrapingSchedule.objects.get(spider_name=spider_name)
            schedule.is_enabled = False
            schedule.save()
            logger.info(f'Disabled schedule: {spider_name}')
            return True
        except ScrapingSchedule.DoesNotExist:
            logger.warning(f'Schedule not found: {spider_name}')
            return False

    @staticmethod
    def update_last_run(spider_name: str, status: str = 'SUCCESS'):
        """Update last run time"""
        try:
            schedule = ScrapingSchedule.objects.get(spider_name=spider_name)
            schedule.last_run = timezone.now()

            # Calculate next run based on frequency
            if schedule.frequency == 'HOURLY':
                schedule.next_run = schedule.last_run + timedelta(hours=1)
            elif schedule.frequency == 'DAILY':
                schedule.next_run = schedule.last_run + timedelta(days=1)
            elif schedule.frequency == 'WEEKLY':
                schedule.next_run = schedule.last_run + timedelta(weeks=1)
            elif schedule.frequency == 'MONTHLY':
                schedule.next_run = schedule.last_run + timedelta(days=30)

            schedule.save()
            logger.info(f'Updated last run for {spider_name}, next run: {schedule.next_run}')

        except ScrapingSchedule.DoesNotExist:
            logger.warning(f'Schedule not found: {spider_name}')

    @staticmethod
    def get_all_schedules() -> List[Dict[str, Any]]:
        """Get all schedules with status"""
        schedules = ScrapingSchedule.objects.all()
        result = []

        for schedule in schedules:
            result.append({
                'spider': schedule.spider_name,
                'frequency': schedule.frequency,
                'enabled': schedule.is_enabled,
                'last_run': schedule.last_run,
                'next_run': schedule.next_run,
                'status': 'ACTIVE' if schedule.is_enabled else 'DISABLED',
            })

        return result


# ============================================================================
# PART 3: Celery Beat Tasks
# ============================================================================
@shared_task(bind=True)
def scrape_quotes_task(self):
    """Scheduled task to scrape quotes"""
    try:
        logger.info(f'Starting scheduled scrape task: {self.request.id}')

        from django.core.management import call_command

        # Run scraping command
        call_command('scrape_quotes')

        # Update schedule
        ScheduleManager.update_last_run('quotes', status='SUCCESS')

        logger.info('Scheduled scrape completed successfully')
        return {'status': 'success', 'message': 'Quotes scraped'}

    except Exception as exc:
        logger.error(f'Scheduled scrape failed: {exc}')
        ScheduleManager.update_last_run('quotes', status='FAILED')
        raise


@shared_task(bind=True)
def scrape_books_task(self):
    """Scheduled task to scrape books"""
    try:
        logger.info(f'Starting scheduled books scrape: {self.request.id}')

        from django.core.management import call_command

        # Run scraping command for books
        call_command('scrape_books')

        # Update schedule
        ScheduleManager.update_last_run('books', status='SUCCESS')

        logger.info('Scheduled books scrape completed')
        return {'status': 'success', 'message': 'Books scraped'}

    except Exception as exc:
        logger.error(f'Scheduled books scrape failed: {exc}')
        ScheduleManager.update_last_run('books', status='FAILED')
        raise


@shared_task(bind=True)
def cleanup_old_quotes_task(self):
    """Scheduled task to clean up old data"""
    try:
        logger.info('Starting cleanup task')

        from datetime import timedelta
        from django.utils import timezone
        from code.django_integration.models import Quote

        # Delete quotes not seen in 30 days
        cutoff = timezone.now() - timedelta(days=30)
        deleted_count, _ = Quote.objects.filter(last_scraped__lt=cutoff).delete()

        logger.info(f'Cleanup completed: deleted {deleted_count} old quotes')
        return {'status': 'success', 'deleted': deleted_count}

    except Exception as exc:
        logger.error(f'Cleanup failed: {exc}')
        raise


# ============================================================================
# PART 4: Schedule Status and Monitoring
# ============================================================================
class ScheduleMonitor:
    """Monitor scheduled task execution"""

    @staticmethod
    def get_schedule_status(spider_name: str) -> Dict[str, Any]:
        """Get current status of a schedule"""
        try:
            schedule = ScrapingSchedule.objects.get(spider_name=spider_name)

            # Get recent jobs
            recent_jobs = ScrapeJob.objects.filter(
                spider_name=spider_name
            ).order_by('-started_at')[:5]

            status = {
                'spider': spider_name,
                'enabled': schedule.is_enabled,
                'frequency': schedule.frequency,
                'last_run': schedule.last_run,
                'next_run': schedule.next_run,
                'recent_jobs': [
                    {
                        'status': job.status,
                        'items': job.items_count,
                        'started': job.started_at.isoformat(),
                        'duration': job.duration(),
                    }
                    for job in recent_jobs
                ],
            }

            return status

        except ScrapingSchedule.DoesNotExist:
            return None

    @staticmethod
    def get_overall_status() -> Dict[str, Any]:
        """Get status of all schedules"""
        print('\n' + '=' * 70)
        print('CELERY BEAT SCHEDULE STATUS')
        print('=' * 70)

        schedules = ScheduleManager.get_all_schedules()

        print(f'\nConfigured Schedules: {len(schedules)}\n')

        for schedule in schedules:
            status_icon = '✓' if schedule['enabled'] else '✗'
            last_run = schedule['last_run'].strftime('%Y-%m-%d %H:%M') if schedule['last_run'] else 'Never'
            next_run = schedule['next_run'].strftime('%Y-%m-%d %H:%M') if schedule['next_run'] else 'Not calculated'

            print(f'{status_icon} {schedule["spider"]:10} ({schedule["frequency"]:10})')
            print(f'  Last run: {last_run}')
            print(f'  Next run: {next_run}')
            print()

    @staticmethod
    def get_upcoming_runs() -> List[Dict[str, Any]]:
        """Get upcoming scheduled runs sorted by time"""
        schedules = ScrapingSchedule.objects.filter(
            is_enabled=True,
            next_run__isnull=False
        ).order_by('next_run')

        upcoming = []

        for schedule in schedules[:10]:
            time_until = schedule.next_run - timezone.now()
            upcoming.append({
                'spider': schedule.spider_name,
                'scheduled_for': schedule.next_run,
                'time_until': str(time_until).split('.')[0],  # Remove microseconds
                'frequency': schedule.frequency,
            })

        return upcoming

    @staticmethod
    def print_upcoming_runs():
        """Print upcoming runs in readable format"""
        print('\n' + '=' * 70)
        print('UPCOMING SCHEDULED RUNS')
        print('=' * 70 + '\n')

        upcoming = ScheduleMonitor.get_upcoming_runs()

        if not upcoming:
            print('No scheduled runs configured\n')
            return

        print(f'{"Spider":<15} {"Scheduled For":<20} {"In":<15}')
        print('─' * 70)

        for run in upcoming:
            scheduled = run['scheduled_for'].strftime('%Y-%m-%d %H:%M:%S')
            print(f'{run["spider"]:<15} {scheduled:<20} {run["time_until"]:<15}')

        print()


# ============================================================================
# PART 5: Examples and Usage
# ============================================================================
def example_setup_schedules():
    """Example: Set up initial schedules"""
    print('\n' + '=' * 70)
    print('EXAMPLE: Setting Up Scraping Schedules')
    print('=' * 70)

    # Create schedules for both spiders
    print('\n[1/3] Creating schedules...')

    quotes_schedule = ScheduleManager.get_or_create_schedule(
        spider_name='quotes',
        frequency='DAILY',
        is_enabled=True
    )
    print(f'✓ Created quotes schedule: DAILY')

    books_schedule = ScheduleManager.get_or_create_schedule(
        spider_name='books',
        frequency='WEEKLY',
        is_enabled=True
    )
    print(f'✓ Created books schedule: WEEKLY')

    # Show current status
    print('\n[2/3] Current schedule status...')
    ScheduleMonitor.get_overall_status()

    # Show upcoming runs
    print('[3/3] Upcoming scheduled runs...')
    ScheduleMonitor.print_upcoming_runs()


def example_manage_schedules():
    """Example: Manage existing schedules"""
    print('\n' + '=' * 70)
    print('EXAMPLE: Managing Schedules')
    print('=' * 70)

    # List all
    print('\n[1/4] All schedules:')
    for schedule in ScheduleManager.get_all_schedules():
        status = '✓ ENABLED' if schedule['enabled'] else '✗ DISABLED'
        print(f'  {schedule["spider"]:15} {schedule["frequency"]:10} {status}')

    # Disable one
    print('\n[2/4] Disabling quotes schedule...')
    ScheduleManager.disable_schedule('quotes')
    print('✓ Quotes scraping disabled')

    # Check status after disable
    print('\n[3/4] Schedule status after disable:')
    status = ScheduleMonitor.get_schedule_status('quotes')
    if status:
        print(f'  Enabled: {status["enabled"]}')
        print(f'  Next run: {status["next_run"]}')

    # Re-enable
    print('\n[4/4] Re-enabling quotes schedule...')
    ScheduleManager.enable_schedule('quotes')
    print('✓ Quotes scraping re-enabled')


def example_beat_configuration():
    """Example: Show Celery Beat configuration"""
    print('\n' + '=' * 70)
    print('EXAMPLE: Celery Beat Schedule Configuration')
    print('=' * 70)

    config = CeleryBeatScheduleManager.configure_beat_schedule()

    print(f'\nConfigured {len(config)} periodic tasks:\n')

    for task_name, task_config in config.items():
        schedule = task_config['schedule']
        task = task_config['task'].split('.')[-1]

        print(f'Task: {task_name}')
        print(f'  Function: {task}')
        print(f'  Schedule: {schedule}')
        print()


def example_monitor_execution():
    """Example: Monitor schedule execution"""
    print('\n' + '=' * 70)
    print('EXAMPLE: Monitoring Schedule Execution')
    print('=' * 70)

    # Get status for all spiders
    for spider in ['quotes', 'books']:
        status = ScheduleMonitor.get_schedule_status(spider)

        if status:
            print(f'\n{spider.upper()} Schedule:')
            print(f'  Enabled: {status["enabled"]}')
            print(f'  Frequency: {status["frequency"]}')
            print(f'  Last run: {status["last_run"]}')
            print(f'  Next run: {status["next_run"]}')

            if status['recent_jobs']:
                print(f'  Recent executions:')
                for job in status['recent_jobs'][:3]:
                    duration = f'{job["duration"]:.1f}s' if job['duration'] else 'N/A'
                    print(
                        f'    - {job["status"]:10} {job["items"]:5} items '
                        f'({duration})'
                    )


# ============================================================================
# PART 6: How to Run Celery Beat
# ============================================================================
def show_beat_instructions():
    """Show instructions for running Celery Beat"""
    print('\n' + '=' * 70)
    print('HOW TO RUN CELERY BEAT')
    print('=' * 70)

    instructions = """
TERMINAL 1: Start Celery Worker
─────────────────────────────────────────────────────────────
$ celery -A code.celery_tasks worker --loglevel=info

Output shows:
  [2024-01-15 10:00:00,123: INFO] Connected to redis://localhost:6379/0
  [2024-01-15 10:00:01,456: INFO] Ready to accept tasks

TERMINAL 2: Start Celery Beat Scheduler
─────────────────────────────────────────────────────────────
$ celery -A code.celery_tasks beat --loglevel=info

Output shows:
  [2024-01-15 10:00:00,789: INFO] Scheduler: Sending due task 'scrape-quotes-daily'
  [2024-01-15 10:00:01,012: INFO] Task 'code.celery_tasks.tasks.scrape_quotes_task' ...

TERMINAL 3: Monitor with Flower (Optional)
─────────────────────────────────────────────────────────────
$ celery -A code.celery_tasks flower --port=5555

Open browser: http://localhost:5555
  - Tasks tab: See all executed tasks
  - Workers tab: Monitor worker status
  - Monitor tab: Real-time graph

TERMINAL 4: View Logs
─────────────────────────────────────────────────────────────
$ tail -f logs/scraping.log | python -m json.tool

Shows JSON logs in human-readable format:
  {
    "timestamp": "2024-01-15T10:00:00",
    "spider": "quotes",
    "items": 50,
    "status": "SUCCESS"
  }

What Happens:
─────────────────────────────────────────────────────────────
1. Beat scheduler waits for scheduled time
2. When time arrives, scheduler submits task to queue
3. Worker picks up task from queue
4. Task executes scraping command
5. Results stored in database
6. Schedule updated with next run time
7. Process repeats

To Manually Trigger a Scheduled Task:
─────────────────────────────────────────────────────────────
$ python manage.py shell
>>> from code.celery_tasks.tasks import scrape_quotes_task
>>> task = scrape_quotes_task.delay()
>>> print(task.id)  # Watch in Flower or logs
"""

    print(instructions)


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print('\n')
    print('╔' + '=' * 68 + '╗')
    print('║' + ' ' * 68 + '║')
    print('║' + '  Example 2: Scheduled Scraping with Celery Beat'.center(68) + '║')
    print('║' + ' ' * 68 + '║')
    print('╚' + '=' * 68 + '╝')

    import argparse

    parser = argparse.ArgumentParser(description='Celery Beat scheduling examples')
    parser.add_argument(
        'action',
        nargs='?',
        default='setup',
        choices=['setup', 'manage', 'config', 'monitor', 'upcoming', 'status', 'instructions'],
        help='Action to perform'
    )

    args = parser.parse_args()

    try:
        if args.action == 'setup':
            example_setup_schedules()

        elif args.action == 'manage':
            example_manage_schedules()

        elif args.action == 'config':
            example_beat_configuration()

        elif args.action == 'monitor':
            example_monitor_execution()

        elif args.action == 'upcoming':
            ScheduleMonitor.print_upcoming_runs()

        elif args.action == 'status':
            ScheduleMonitor.get_overall_status()

        elif args.action == 'instructions':
            show_beat_instructions()

    except Exception as e:
        print(f'\n✗ Error: {e}')
        logger.exception('Unexpected error')
        sys.exit(1)
