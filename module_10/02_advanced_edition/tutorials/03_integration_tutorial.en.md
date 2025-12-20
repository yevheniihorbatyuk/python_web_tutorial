# Tutorial: Integrating Scrapy + Django + Celery

**Goal**: Build a complete workflow where a Django view triggers a Celery task that runs a Scrapy spider, which in turn saves data to the Django database.

---

## Step 1: Create a Django Management Command for Scrapy

This command will be the bridge between Django and Scrapy.

1.  Create the necessary directory structure:
    ```bash
    mkdir -p 02_advanced_edition/code/django_integration/management/commands
    ```
2.  Create the command file `02_advanced_edition/code/django_integration/management/commands/run_spider.py`:
    ```python
    from django.core.management.base import BaseCommand
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from 02_advanced_edition.code.scrapy_project.quotescrawler.spiders.quotes_spider import QuotesSpider

    class Command(BaseCommand):
        help = "Runs the quotes spider"

        def handle(self, *args, **options):
            process = CrawlerProcess(get_project_settings())
            process.crawl(QuotesSpider)
            process.start()
            self.stdout.write(self.style.SUCCESS('Successfully ran spider'))
    ```

---

## Step 2: Create a Celery Task to Run the Command

This task will allow us to run the scraper asynchronously.

Open `02_advanced_edition/code/celery_tasks/tasks.py` and add:
```python
from django.core.management import call_command

@shared_task
def scrape_quotes_task():
    """
    A Celery task that runs the 'run_spider' management command.
    """
    print("Starting the scrape task...")
    call_command("run_spider")
    print("Scrape task finished.")
```

---

## Step 3: Create a Django Pipeline for Scrapy

This pipeline will receive items from the spider and save them using the Django ORM.

1.  Make sure your Django environment is configured for Scrapy. You might need to add this to your Scrapy `settings.py`:
    ```python
    import os
    import sys
    import django

    # Add the Django project to the Python path
    sys.path.append('/path/to/your/django_project') 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    ```

2.  Create the pipeline in `02_advanced_edition/code/scrapy_project/quotescrawler/pipelines.py`:
    ```python
    from 02_advanced_edition.code.django_integration.models import Quote, Author

    class DjangoPipeline:
        def process_item(self, item, spider):
            author, _ = Author.objects.get_or_create(name=item['author'])
            Quote.objects.get_or_create(
                text=item['text'],
                author=author
            )
            return item
    ```

3.  Enable the pipeline in your Scrapy `settings.py`:
    ```python
    ITEM_PIPELINES = {
       'quotescrawler.pipelines.DjangoPipeline': 300,
    }
    ```

---

## Step 4: Trigger the Task from a Django View

Finally, create a simple view to start the whole process.

1.  Add a view to `02_advanced_edition/code/django_integration/views.py`:
    ```python
    from django.http import HttpResponse
    from 02_advanced_edition.code.celery_tasks.tasks import scrape_quotes_task

    def trigger_scrape(request):
        scrape_quotes_task.delay()
        return HttpResponse("Scraping process has been started in the background.")
    ```

2.  Add a URL for it in your `urls.py`:
    ```python
    from django.urls import path
    from .views import trigger_scrape

    urlpatterns = [
        path('scrape/', trigger_scrape, name='trigger_scrape'),
    ]
    ```

---

## Step 5: Run and Test

1.  **Start your Django development server.**
2.  **Start your Celery worker** in a separate terminal.
3.  Navigate to `http://127.0.0.1:8000/scrape/` in your browser.

You should see the "Scraping process started" message. In your Celery worker's terminal, you will see the task being executed, which will then run the Scrapy spider. The spider's logs will appear, and the data will be saved to your Django database. You can verify this in the Django admin.
