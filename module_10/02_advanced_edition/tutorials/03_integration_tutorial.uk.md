# Туторіал: Інтеграція Scrapy + Django + Celery

**Мета**: Створити повний робочий процес, де представлення Django запускає завдання Celery, яке виконує павука Scrapy, що в свою чергу зберігає дані в базу даних Django.

---

## Крок 1: Створення команди керування Django для Scrapy

Ця команда буде мостом між Django та Scrapy.

1.  Створіть необхідну структуру каталогів:
    ```bash
    mkdir -p 02_advanced_edition/code/django_integration/management/commands
    ```
2.  Створіть файл команди `02_advanced_edition/code/django_integration/management/commands/run_spider.py`:
    ```python
    from django.core.management.base import BaseCommand
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from 02_advanced_edition.code.scrapy_project.quotescrawler.spiders.quotes_spider import QuotesSpider

    class Command(BaseCommand):
        help = "Запускає павука quotes"

        def handle(self, *args, **options):
            process = CrawlerProcess(get_project_settings())
            process.crawl(QuotesSpider)
            process.start()
            self.stdout.write(self.style.SUCCESS('Павука успішно запущено'))
    ```

---

## Крок 2: Створення завдання Celery для запуску команди

Це завдання дозволить нам запускати скрепер асинхронно.

Відкрийте `02_advanced_edition/code/celery_tasks/tasks.py` та додайте:
```python
from django.core.management import call_command

@shared_task
def scrape_quotes_task():
    """
    Завдання Celery, яке запускає команду керування 'run_spider'.
    """
    print("Запуск завдання скрапінгу...")
    call_command("run_spider")
    print("Завдання скрапінгу завершено.")
```

---

## Крок 3: Створення конвеєра Django для Scrapy

Цей конвеєр отримуватиме елементи від павука та зберігатиме їх за допомогою Django ORM.

1.  Переконайтеся, що ваше середовище Django налаштовано для Scrapy. Можливо, вам доведеться додати це до файлу `settings.py` вашого Scrapy:
    ```python
    import os
    import sys
    import django

    # Додайте проєкт Django до шляху Python
    sys.path.append('/шлях/до/вашого/django_project') 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    ```

2.  Створіть конвеєр у `02_advanced_edition/code/scrapy_project/quotescrawler/pipelines.py`:
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

3.  Увімкніть конвеєр у файлі `settings.py` вашого Scrapy:
    ```python
    ITEM_PIPELINES = {
       'quotescrawler.pipelines.DjangoPipeline': 300,
    }
    ```

---

## Крок 4: Запуск завдання з представлення Django

Нарешті, створіть просте представлення для запуску всього процесу.

1.  Додайте представлення до `02_advanced_edition/code/django_integration/views.py`:
    ```python
    from django.http import HttpResponse
    from 02_advanced_edition.code.celery_tasks.tasks import scrape_quotes_task

    def trigger_scrape(request):
        scrape_quotes_task.delay()
        return HttpResponse("Процес скрапінгу було запущено у фоновому режимі.")
    ```

2.  Додайте URL для нього у вашому `urls.py`:
    ```python
    from django.urls import path
    from .views import trigger_scrape

    urlpatterns = [
        path('scrape/', trigger_scrape, name='trigger_scrape'),
    ]
    ```

---

## Крок 5: Запуск та тестування

1.  **Запустіть ваш сервер розробки Django.**
2.  **Запустіть ваш воркер Celery** в окремому терміналі.
3.  Перейдіть за адресою `http://127.0.0.1:8000/scrape/` у вашому браузері.

Ви повинні побачити повідомлення "Процес скрапінгу було запущено". У терміналі вашого воркера Celery ви побачите, як виконується завдання, яке потім запустить павука Scrapy. З'являться логи павука, і дані будуть збережені у вашу базу даних Django. Ви можете перевірити це в адмін-панелі Django.
