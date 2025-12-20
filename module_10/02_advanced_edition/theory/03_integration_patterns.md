# Lesson 3: Scrapy + Django Integration Patterns

**Goal**: Combine Scrapy, Celery, and Django into unified system
**Time**: 25 minutes reading
**Prerequisites**: Lessons 1-2 complete

---

## The Integration Challenge

After Lessons 1 and 2, you have:
- **Lesson 1**: Scrapy spiders that extract data
- **Lesson 2**: Celery tasks that run async

But in production, you need them to work **together**:
- Run Scrapy from Django (not standalone)
- Store results in Django database
- Schedule with Celery Beat
- Monitor in Django admin
- Handle duplicates intelligently

---

## Integration Architecture

```
Django Admin Interface
  ↓ (User clicks: "Start Scraping")
Django View / Management Command
  ↓
Celery Task
  ↓
CrawlerProcess (Scrapy)
  ├─ Download HTML
  ├─ Parse with spiders
  └─ Yield items
       ↓
Custom Django ORM Pipeline
  ├─ Validate
  ├─ Check for duplicates
  └─ Save to database
       ↓
Django ORM
  └─ Quote, Book, Author models
       ↓
PostgreSQL Database

User queries through Django API
  ↓ (GET /api/quotes/)
Django REST API returns data from database
```

---

## Key Patterns

### Pattern 1: Django Management Command

Allows running Scrapy from Django context:

```python
# quotes/management/commands/scrape_quotes.py

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from quotescrawler.spiders import QuotesSpider

class Command(BaseCommand):
    help = 'Scrape quotes and store in database'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        # Access Django models, settings, database
        process = CrawlerProcess(settings)
        process.crawl(QuotesSpider, limit=options['limit'])
        process.start()

        self.stdout.write('Scraping complete')
```

**Advantages**:
- Access to Django ORM directly
- Settings and configuration
- Can be called from code or command line
- Fits Django's architecture

---

### Pattern 2: Custom Django ORM Pipeline

Instead of saving to JSON, save directly to Django models:

```python
# quotescrawler/pipelines.py

from django.core.exceptions import ValidationError
from quotes.models import Quote

class DjangoORMPipeline:
    """Save scraped items to Django database"""

    def process_item(self, item, spider):
        # Check for duplicates
        quote, created = Quote.objects.get_or_create(
            text=item['text'],
            author=item['author'],
        )

        # Update metadata
        if not created:
            quote.scraped_count += 1
        quote.last_scraped = timezone.now()
        quote.source = spider.name
        quote.save()

        return item
```

**Benefits**:
- Automatic duplicate detection
- Update statistics
- Track when items were last seen
- Query results immediately in Django

---

### Pattern 3: Duplicate Handling

Multiple approaches for detecting already-scraped items:

**Approach 1: get_or_create() (Simplest)**
```python
quote, created = Quote.objects.get_or_create(
    text=item['text'],
    author=item['author'],
)
if not created:
    quote.scraped_count += 1
    quote.save()
```

**Approach 2: update_or_create() (Updates)**
```python
quote, created = Quote.objects.update_or_create(
    text=item['text'],
    author=item['author'],
    defaults={'last_scraped': now()}
)
```

**Approach 3: Bulk operations (Efficient)**
```python
# Load existing IDs
existing_ids = set(Quote.objects.values_list('id', flat=True))

# Filter items
items_to_create = [q for q in items if q['id'] not in existing_ids]

# Bulk insert
Quote.objects.bulk_create(items_to_create)
```

---

### Pattern 4: Scheduled Scraping

Combine Celery Beat (scheduling) + Scrapy (scraping):

```python
# tasks.py
@shared_task
def scheduled_scrape_quotes():
    """Scrape quotes daily"""
    call_command('scrape_quotes')

# celery.py (configuration)
from celery.schedules import crontab

app.conf.beat_schedule = {
    'scrape-quotes-daily': {
        'task': 'tasks.scheduled_scrape_quotes',
        'schedule': crontab(hour=0, minute=0),  # Midnight
    },
}
```

**How it works**:
1. Celery Beat triggers task at scheduled time
2. Task calls Django management command
3. Command starts Scrapy spider
4. Spider extracts and saves to database
5. All happens automatically without user interaction

---

### Pattern 5: Job Tracking

Track scraping jobs for visibility:

```python
# models.py
class ScrapeJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    spider_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    items_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

# In management command
job = ScrapeJob.objects.create(
    spider_name='quotes',
    status='RUNNING',
    started_at=timezone.now(),
)

try:
    # ... scraping ...
    job.status = 'SUCCESS'
    job.items_count = Quote.objects.filter(
        last_scraped__gte=job.started_at
    ).count()
except Exception as e:
    job.status = 'FAILED'
    job.error_message = str(e)
finally:
    job.completed_at = timezone.now()
    job.save()
```

**Benefits**:
- See when scraping ran
- Track success/failure
- Count items scraped
- See errors for debugging
- Available in Django admin

---

### Pattern 6: Data Enrichment

Combine scraped data with other sources:

```python
@shared_task
def enrich_quotes():
    """Add author details to quotes"""
    for quote in Quote.objects.filter(author_bio=''):
        # Fetch bio from Wikipedia
        bio = fetch_author_bio(quote.author)
        quote.author_bio = bio
        quote.save()

# Schedule weekly
app.conf.beat_schedule = {
    'enrich-quotes-weekly': {
        'task': 'tasks.enrich_quotes',
        'schedule': crontab(day_of_week=0, hour=2),  # Sunday 2am
    },
}
```

---

## Complete Integration Example

```
1. User clicks "Scrape Quotes" in Django admin
   ↓
2. Django view submits Celery task
   task = scrape_quotes_task.delay()
   ↓
3. Celery worker picks up task
   ↓
4. Task calls: python manage.py scrape_quotes
   ↓
5. Management command creates Scrapy CrawlerProcess
   ↓
6. Spider downloads pages and extracts quotes
   ↓
7. Custom Django ORM pipeline processes each item
   - Validates data
   - Checks for duplicates
   - Saves to PostgreSQL database
   ↓
8. Job tracking record updated with results
   ↓
9. User sees results in Django admin immediately
   Quote.objects.all() returns fresh data from database
```

---

## CrawlerProcess vs CrawlerRunner

When running Scrapy from Django:

| Method | Blocking | Use Case |
|--------|----------|----------|
| **CrawlerProcess** | Yes | Management commands, Celery tasks |
| **CrawlerRunner** | No | Embedded spiders, real-time handling |

For integration: Use **CrawlerProcess** (simpler, blocking is fine in background tasks)

```python
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess(settings)
process.crawl(QuotesSpider)
process.start()  # Blocks until spider finishes
# Then continue to save results
```

---

## Error Handling in Integration

```python
# Task with error handling
@shared_task(bind=True, autoretry_for=(Exception,))
def scrape_with_retry(self):
    try:
        call_command('scrape_quotes')
        return 'Success'
    except ScrapyError as e:
        # Retry on spider errors
        raise self.retry(exc=e, countdown=300)
    except DatabaseError as e:
        # Log database errors, don't retry
        logger.error(f'DB error: {e}')
        return 'Failed: Database error'
```

---

## Monitoring Integration

### In Django Admin
- See ScrapeJob history
- View errors
- Manually trigger scraping
- See statistics

### With Flower
```bash
celery -A config flower
# See task execution time
# See if retrying
# Monitor worker health
```

### Logs
```bash
# Check if spider ran
tail -f logs/spider.log

# Check task execution
tail -f logs/celery.log
```

---

## Common Issues & Solutions

### Issue: Spider runs twice
**Problem**: Task submitted twice, both run
**Solution**: Add task lock with Redis

### Issue: Spider hangs
**Problem**: Network issue, stuck on page
**Solution**: Set CONCURRENT_REQUESTS_PER_DOMAIN = 1

### Issue: Database locked
**Problem**: Multiple spiders writing simultaneously
**Solution**: Use db_for_read/db_for_write

### Issue: Out of memory
**Problem**: Too many items in pipeline
**Solution**: Use bulk_create with batch_size

---

## Best Practices

1. **Always use management commands** - Cleaner integration
2. **Track jobs** - See what ran when
3. **Handle duplicates** - Don't store same data twice
4. **Log everything** - Debug production issues
5. **Set timeouts** - Prevent hanging tasks
6. **Test offline** - Run spider locally first
7. **Monitor** - Watch with Flower or logs
8. **Validate** - Check data before saving

---

## Official Resources

- **Django Management Commands**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- **Scrapy with Django**: https://docs.scrapy.org/en/latest/topics/django.html
- **Celery Django**: https://docs.celeryproject.io/en/stable/django/

---

## Next Steps

1. **Read this document** (you're reading it) ✓
2. **Follow**: [03_integration_tutorial.md](../tutorials/03_integration_tutorial.md)
3. **Code**: Create management command and pipeline in `code/`
4. **Test**: Run spider through Django

Then move to **Lesson 4: Production Patterns**
