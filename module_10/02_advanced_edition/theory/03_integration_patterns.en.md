# Lesson 3: Scrapy + Django Integration Patterns

**Goal**: Combine Scrapy, Celery, and Django into a unified system.

---

## The Integration Challenge

We have three powerful but separate components:
- **Django**: For web interface and database models.
- **Scrapy**: For efficient, large-scale scraping.
- **Celery**: For running background tasks.

The challenge is to make them work together seamlessly.

---

## Integration Architecture

A common and effective architecture looks like this:

```
  User Action (e.g., button click in Django Admin)
         │
         ▼
    Django View
         │
         ▼ (Dispatches a task)
    Celery Task
         │
         ▼ (Executes the scraper)
   Scrapy Spider
         │
         ▼ (Processes and saves data)
  Scrapy Pipeline
         │
         ▼ (Uses Django's ORM)
   Django Models
         │
         ▼
     Database
```

---

## Key Integration Patterns

### Pattern 1: Run Scrapy from Django

Instead of running `scrapy crawl` from the command line, we can run it from within our Django application. The best way to do this is via a **custom management command**.

```python
# my_app/management/commands/scrape.py
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from my_scraper.spiders.my_spider import MySpider

class Command(BaseCommand):
    help = "Runs the Scrapy spider"

    def handle(self, *args, **options):
        process = CrawlerProcess(get_project_settings())
        process.crawl(MySpider)
        process.start() # The script will block here until the crawling is finished
```
Now you can run your spider with `python manage.py scrape`.

### Pattern 2: Save Data with a Django Item Pipeline

A Scrapy pipeline can be used to save scraped items directly into the Django database.

```python
# my_scraper/pipelines.py
from my_app.models import MyModel

class DjangoPipeline:
    def process_item(self, item, spider):
        # Use get_or_create to avoid duplicates
        obj, created = MyModel.objects.get_or_create(
            field1=item['field1'],
            defaults={'field2': item['field2']}
        )
        if created:
            spider.log(f"Created new object: {obj.field1}")
        else:
            spider.log(f"Found existing object: {obj.field1}")
        return item
```
To use this pipeline, you must enable it in your Scrapy `settings.py`.

### Pattern 3: Asynchronous Scraping with Celery

To prevent the web process from blocking while the scraper runs, we dispatch the scraping job as a Celery task.

```python
# my_app/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def run_scrape_task():
    """A Celery task to run the scrape management command."""
    call_command("scrape")
```
Now, from a Django view, you can start the scraper in the background:
```python
# my_app/views.py
from .tasks import run_scrape_task

def start_scrape_view(request):
    run_scrape_task.delay()
    return HttpResponse("Scraping has been started in the background!")
```

---
## Additional Resources

- **Django Management Commands**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- **Running Scrapy from a script**: https://docs.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
- **Using Django Items in Scrapy**: https://pypi.org/project/scrapy-djangoitem/
