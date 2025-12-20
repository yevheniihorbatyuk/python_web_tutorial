# Tutorial: Integrating Scrapy + Django + Celery

**Time**: 45 minutes hands-on
**Goal**: Build complete workflow: Django → Celery → Scrapy → Django ORM
**Difficulty**: Advanced

---

## Prerequisites

✅ Lesson 1 (Scrapy) complete
✅ Lesson 2 (Celery) complete
✅ Django installed and configured
✅ PostgreSQL running
✅ Redis running

---

## Step 1: Understand the Integration Flow

### Complete Workflow

```
1. User clicks "Start Scraping" in Django admin
   ↓
2. Django view submits Celery task
   ↓
3. Celery worker receives task
   ↓
4. Task starts Scrapy spider (CrawlerProcess)
   ↓
5. Spider extracts data from website
   ↓
6. Custom Django ORM pipeline processes items
   ├─ Validates data
   ├─ Checks for duplicates
   └─ Saves to database
   ↓
7. Task completes, results stored
   ↓
8. User sees results in Django admin
   ↓
9. Can query data via Django ORM
```

---

## Step 2: Review Models

### Check Models File

```bash
cat /root/goit/python_web/module_10/02_advanced_edition/code/django_integration/models.py | head -50
```

### Key Models

1. **ScrapeJob** - Tracks scraping execution
   - Status: PENDING, RUNNING, SUCCESS, FAILED
   - Stores error messages
   - Celery task_id for tracking

2. **Quote** - Scraped quotes
   - Unique constraint on (text, author)
   - Tracking: last_scraped, scraped_count
   - Indexes for performance

3. **ScrapingSchedule** - Configuration
   - Enable/disable scraping
   - Frequency settings
   - Last and next run times

---

## Step 3: Set Up Django Integration

### 3a. Add Models to Django App

```bash
# In your Django app
python manage.py makemigrations quotes
python manage.py migrate
```

### 3b. Register in Admin

```python
# quotes/admin.py
from django.contrib import admin
from .models import Quote, ScrapeJob, ScrapingSchedule

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'scraped_count', 'last_scraped')
    list_filter = ('last_scraped', 'scraped_count')
    search_fields = ('text', 'author')

@admin.register(ScrapeJob)
class ScrapeJobAdmin(admin.ModelAdmin):
    list_display = ('spider_name', 'status', 'items_count', 'started_at')
    list_filter = ('status', 'spider_name')
    readonly_fields = ('task_id', 'error_message')

@admin.register(ScrapingSchedule)
class ScrapingScheduleAdmin(admin.ModelAdmin):
    list_display = ('spider_name', 'is_enabled', 'frequency', 'last_run')
```

---

## Step 4: Create Scrapy Pipeline with Django ORM

### 4a. Create Custom Pipeline

```python
# code/scrapy_project/quotescrawler/pipelines.py
# Add this to existing file:

from django.utils import timezone
from django.core.exceptions import ValidationError
from code.django_integration.models import Quote

class DjangoORMPipeline:
    """Save items to Django ORM instead of JSON"""

    def __init__(self):
        self.items_created = 0
        self.items_updated = 0

    def open_spider(self, spider):
        self.items_created = 0
        self.items_updated = 0
        spider.logger.info('DjangoORMPipeline opened')

    def close_spider(self, spider):
        spider.logger.info(
            f'DjangoORMPipeline closed: '
            f'created={self.items_created}, updated={self.items_updated}'
        )

    def process_item(self, item, spider):
        try:
            # Get or create quote
            quote, created = Quote.objects.get_or_create(
                text=item['text'],
                author=item['author'],
                defaults={'source': item.get('source', spider.name)}
            )

            if created:
                self.items_created += 1
            else:
                self.items_updated += 1
                quote.scraped_count += 1

            quote.last_scraped = timezone.now()
            quote.save()

            return item

        except ValidationError as e:
            spider.logger.error(f'Validation error: {e}')
            raise


# Update settings to use new pipeline
ITEM_PIPELINES = {
    'quotescrawler.pipelines.ValidationPipeline': 100,
    'quotescrawler.pipelines.DjangoORMPipeline': 300,  # Add this
}
```

### 4b. Test Pipeline

```bash
# Run spider directly (outputs to Django)
cd code/scrapy_project
scrapy crawl quotes

# Check database
python manage.py shell
>>> from code.django_integration.models import Quote
>>> Quote.objects.count()
# Should see quotes in database!
```

---

## Step 5: Create Management Command

### 5a. Create Command Structure

```bash
# Create directories
mkdir -p code/django_integration/management/commands
touch code/django_integration/management/__init__.py
touch code/django_integration/management/commands/__init__.py
```

### 5b. Create Scraping Command

```python
# code/django_integration/management/commands/scrape_quotes.py

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from code.scrapy_project.quotescrawler.spiders import QuotesSpider
from code.django_integration.models import ScrapeJob
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape quotes and store in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of pages'
        )

    def handle(self, *args, **options):
        # Create job record
        job = ScrapeJob.objects.create(
            spider_name='quotes',
            status='RUNNING',
            started_at=timezone.now(),
        )

        try:
            # Configure Scrapy
            settings = {
                'USER_AGENT': 'Mozilla/5.0 ...',
                'ROBOTSTXT_OBEY': True,
                'CONCURRENT_REQUESTS': 8,
                'ITEM_PIPELINES': {
                    'quotescrawler.pipelines.ValidationPipeline': 100,
                    'quotescrawler.pipelines.DjangoORMPipeline': 300,
                },
            }

            # Run spider
            process = CrawlerProcess(settings)
            process.crawl(QuotesSpider)
            process.start()

            # Update job
            job.status = 'SUCCESS'
            job.completed_at = timezone.now()
            job.items_count = Quote.objects.filter(
                last_scraped__gte=job.started_at
            ).count()
            job.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully scraped {job.items_count} quotes'
                )
            )

        except Exception as exc:
            job.status = 'FAILED'
            job.error_message = str(exc)
            job.completed_at = timezone.now()
            job.save()
            logger.error(f'Scraping failed: {exc}')
            raise
```

### 5c. Test Command

```bash
# Run command
python manage.py scrape_quotes

# Check results
python manage.py shell
>>> from code.django_integration.models import Quote, ScrapeJob
>>> Quote.objects.count()
>>> ScrapeJob.objects.last()
```

---

## Step 6: Create Celery Task for Scraping

### 6a. Add Task

```python
# code/celery_tasks/tasks.py
# Add to existing file:

@shared_task(bind=True)
def scrape_quotes_task(self):
    """
    Scrape quotes using management command.
    This runs as a background task in Celery.
    """
    try:
        from django.core.management import call_command

        logger.info(f'Starting scrape task: {self.request.id}')

        # Run command
        call_command('scrape_quotes')

        # Get results
        from code.django_integration.models import ScrapeJob
        last_job = ScrapeJob.objects.last()

        logger.info(f'Scrape complete: {last_job.items_count} items')
        return {
            'status': 'success',
            'items_count': last_job.items_count,
        }

    except Exception as exc:
        logger.error(f'Scrape task failed: {exc}')
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=300)
```

### 6b. Test Task

```bash
# Terminal 1: Start Celery worker
celery -A code.celery_tasks worker --loglevel=info

# Terminal 2: Python shell
python3
>>> from code.celery_tasks.tasks import scrape_quotes_task
>>> task = scrape_quotes_task.delay()
>>> task.get(timeout=600)  # Wait up to 10 minutes
{'status': 'success', 'items_count': 50}

# Check database
>>> from code.django_integration.models import Quote
>>> Quote.objects.count()
```

---

## Step 7: Create Django View for Web Interface

### 7a. Create View

```python
# code/django_integration/views.py (update existing)

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from celery.result import AsyncResult
from code.celery_tasks.tasks import scrape_quotes_task

class TriggerScrapingView(View):
    @require_http_methods(['POST'])
    def post(self, request):
        """Trigger scraping task"""
        task = scrape_quotes_task.delay()

        return JsonResponse({
            'task_id': task.id,
            'status': 'submitted',
        }, status=202)

class ScrapingProgressView(View):
    @require_http_methods(['GET'])
    def get(self, request, task_id):
        """Check scraping progress"""
        task = AsyncResult(task_id)

        return JsonResponse({
            'task_id': task_id,
            'status': task.status,
            'result': task.result if task.ready() else None,
        })
```

### 7b. Add URLs

```python
# urls.py
from django.urls import path
from code.django_integration.views import TriggerScrapingView, ScrapingProgressView

urlpatterns = [
    path('api/scrape/', TriggerScrapingView.as_view(), name='trigger_scrape'),
    path('api/scrape/<str:task_id>/', ScrapingProgressView.as_view(), name='scrape_progress'),
]
```

### 7c. Test API

```bash
# Submit scraping task
curl -X POST http://localhost:8000/api/scrape/

# Response:
# {"task_id": "abc-123-def", "status": "submitted"}

# Check progress
curl http://localhost:8000/api/scrape/abc-123-def/

# Response:
# {"task_id": "abc-123-def", "status": "SUCCESS", "result": {...}}
```

---

## Step 8: Handle Duplicates

### 8a. Duplicate Detection

The `Quote` model has `unique_together` constraint:

```python
# In models.py:
class Meta:
    unique_together = ('text', 'author')
```

This ensures no duplicates are stored.

### 8b. Track Duplicate Attempts

When duplicate is found:

```python
# In pipeline:
quote, created = Quote.objects.get_or_create(
    text=item['text'],
    author=item['author'],
)

if not created:
    # This was a duplicate
    quote.scraped_count += 1  # Track how many times seen
    quote.last_scraped = timezone.now()
    quote.save()
```

### 8c. Query Duplicates

```bash
python manage.py shell
>>> from code.django_integration.models import Quote
>>> # Find quotes seen multiple times
>>> Quote.objects.filter(scraped_count__gt=1)
>>> # Find quotes not seen in 7 days
>>> from datetime import timedelta
>>> from django.utils import timezone
>>> cutoff = timezone.now() - timedelta(days=7)
>>> Quote.objects.filter(last_scraped__lt=cutoff)
```

---

## Step 9: Schedule Automatic Scraping

### 9a. Update Celery Beat Schedule

```python
# code/celery_tasks/config.py
from celery.schedules import crontab
from datetime import timedelta

app.conf.beat_schedule = {
    # Daily at midnight
    'scrape-quotes-daily': {
        'task': 'code.celery_tasks.tasks.scrape_quotes_task',
        'schedule': crontab(hour=0, minute=0),
    },

    # Every 6 hours
    'scrape-quotes-every-6h': {
        'task': 'code.celery_tasks.tasks.scrape_quotes_task',
        'schedule': timedelta(hours=6),
    },
}
```

### 9b. Start Celery Beat

```bash
# Terminal 3: Start Beat scheduler
celery -A code.celery_tasks beat --loglevel=info

# Output:
# [2024-01-15 00:00:00,000: INFO] Scheduler: Sending due task 'scrape-quotes-daily'
# [2024-01-15 06:00:00,000: INFO] Scheduler: Sending due task 'scrape-quotes-every-6h'
```

---

## Step 10: Monitor Everything

### 10a. Django Admin

```bash
# Access Django admin
python manage.py runserver

# Go to http://localhost:8000/admin
# View:
# - Quotes: All scraped quotes
# - Scrape Jobs: Execution history
# - Scheduling: Configure when to scrape
```

### 10b. Flower Dashboard

```bash
# Terminal 4: Flower monitoring
celery -A code.celery_tasks flower

# Access http://localhost:5555
# See:
# - Active tasks
# - Task history
# - Worker status
```

### 10c. Database Queries

```bash
python manage.py shell

# Total quotes scraped
>>> from code.django_integration.models import Quote
>>> Quote.objects.count()

# Quotes added today
>>> from datetime import timedelta
>>> from django.utils import timezone
>>> today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
>>> Quote.objects.filter(created_at__gte=today).count()

# Most seen quotes (duplicates)
>>> Quote.objects.order_by('-scraped_count')[:5]

# Scraping job history
>>> from code.django_integration.models import ScrapeJob
>>> ScrapeJob.objects.all()
>>> ScrapeJob.objects.filter(status='SUCCESS').count()
```

---

## Common Tasks

### Manually Trigger Scraping

**Option 1: Django Management Command**
```bash
python manage.py scrape_quotes --limit 10
```

**Option 2: Django Shell**
```python
from django.core.management import call_command
call_command('scrape_quotes')
```

**Option 3: Celery Task**
```python
from code.celery_tasks.tasks import scrape_quotes_task
task = scrape_quotes_task.delay()
result = task.get(timeout=600)
```

**Option 4: HTTP API**
```bash
curl -X POST http://localhost:8000/api/scrape/
```

### Clear Old Data

```python
# Delete quotes not seen in 30 days
from datetime import timedelta
from django.utils import timezone
from code.django_integration.models import Quote

cutoff = timezone.now() - timedelta(days=30)
deleted = Quote.objects.filter(last_scraped__lt=cutoff).delete()
print(f'Deleted {deleted[0]} quotes')
```

### Export Quotes

```bash
python manage.py dumpdata django_integration.Quote --format=json > quotes.json
```

---

## Troubleshooting

### Celery Not Finding Tasks

**Problem**: `Unregistered task`

**Solution**:
```bash
# Make sure Django is in path
export DJANGO_SETTINGS_MODULE=config.settings
celery -A code.celery_tasks worker --loglevel=info
```

### Scrapy Import Errors

**Problem**: `ModuleNotFoundError: No module named 'quotescrawler'`

**Solution**:
```bash
# Add to Python path
export PYTHONPATH=/root/goit/python_web/module_10/02_advanced_edition:$PYTHONPATH
```

### Database Migrations Failed

**Problem**: `django.db.utils.OperationalError`

**Solution**:
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

---

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Management Command** | Django way to run scripts |
| **CrawlerProcess** | Run Scrapy spider from code |
| **Django ORM Pipeline** | Save items to database |
| **Duplicate Detection** | Avoid storing same data twice |
| **Celery Task** | Async background job |
| **Celery Beat** | Scheduled task runner |
| **Monitoring** | Track execution via Flower |

---

## Next Steps

1. ✅ You've integrated all 3 systems
2. 📖 Read [Production Patterns](../theory/04_production_patterns.md)
3. 🔧 Follow [Production Tutorial](04_production_tutorial.md)
4. 📚 Review [example projects](../examples/)

Congratulations! You have a complete web scraping system. 🎉
