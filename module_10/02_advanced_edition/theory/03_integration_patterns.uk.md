# Урок 3: Патерни інтеграції Scrapy + Django

**Мета**: об'єднати Scrapy, Celery та Django в єдину систему.

---

## Проблема інтеграції

У нас є три потужні, але окремі компоненти:
- **Django**: для веб-інтерфейсу та моделей бази даних.
- **Scrapy**: для ефективного, великомасштабного скрапінгу.
- **Celery**: для виконання фонових завдань.

Завдання полягає в тому, щоб змусити їх працювати разом безперебійно.

---

## Архітектура інтеграції

Поширена та ефективна архітектура виглядає так:

```
  Дія користувача (наприклад, клік кнопки в адмін-панелі Django)
         │
         ▼
    Django View
         │
         ▼ (Відправляє завдання)
    Celery Task
         │
         ▼ (Виконує скрепер)
   Scrapy Spider
         │
         ▼ (Обробляє та зберігає дані)
  Scrapy Pipeline
         │
         ▼ (Використовує Django ORM)
   Django Models
         │
         ▼
     База даних
```

---

## Ключові патерни інтеграції

### Патерн 1: Запуск Scrapy з Django

Замість того, щоб запускати `scrapy crawl` з командного рядка, ми можемо запускати його з нашого додатку Django. Найкращий спосіб зробити це — через **власну команду керування**.

```python
# my_app/management/commands/scrape.py
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from my_scraper.spiders.my_spider import MySpider

class Command(BaseCommand):
    help = "Запускає павука Scrapy"

    def handle(self, *args, **options):
        process = CrawlerProcess(get_project_settings())
        process.crawl(MySpider)
        process.start() # Скрипт буде блокуватися тут до завершення кроулінгу
```
Тепер ви можете запустити свого павука за допомогою `python manage.py scrape`.

### Патерн 2: Збереження даних за допомогою Django Item Pipeline

Конвеєр Scrapy можна використовувати для збереження зібраних елементів безпосередньо в базу даних Django.

```python
# my_scraper/pipelines.py
from my_app.models import MyModel

class DjangoPipeline:
    def process_item(self, item, spider):
        # Використовуйте get_or_create, щоб уникнути дублікатів
        obj, created = MyModel.objects.get_or_create(
            field1=item['field1'],
            defaults={'field2': item['field2']}
        )
        if created:
            spider.log(f"Створено новий об'єкт: {obj.field1}")
        else:
            spider.log(f"Знайдено існуючий об'єкт: {obj.field1}")
        return item
```
Щоб використовувати цей конвеєр, ви повинні увімкнути його у файлі `settings.py` вашого Scrapy.

### Патерн 3: Асинхронний скрапінг з Celery

Щоб запобігти блокуванню веб-процесу під час роботи скрепера, ми відправляємо завдання скрапінгу як завдання Celery.

```python
# my_app/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def run_scrape_task():
    """Завдання Celery для запуску команди керування скрапінгом."""
    call_command("scrape")
```
Тепер з представлення Django ви можете запустити скрепер у фоновому режимі:
```python
# my_app/views.py
from .tasks import run_scrape_task

def start_scrape_view(request):
    run_scrape_task.delay()
    return HttpResponse("Скрапінг було запущено у фоновому режимі!")
```

---
## Додаткові ресурси

- **Команди керування Django**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
- **Запуск Scrapy зі скрипта**: https://docs.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
- **Використання Django Items у Scrapy**: https://pypi.org/project/scrapy-djangoitem/
