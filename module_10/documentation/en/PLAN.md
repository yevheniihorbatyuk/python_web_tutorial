# Module 10: Django, Web Scraping & Modern Web Development
## Комплексний план розробки

**Статус:** PLANNING
**Target:** Senior Data Scientists/Engineers
**Duration:** 6-8 hours (Beginner) + 4-6 hours (Advanced)
**Technologies:** Django 5.0, BeautifulSoup, Scrapy, PostgreSQL, Docker, Celery

---

## 🎯 Загальна мета

Побудувати **повнофункціональні веб-додатки** з:
- Веб-скрапінгом (news, products, data)
- Django CRUD операціями
- Реальною БД архітектурою
- Асинхронною обробкою даних
- Production-ready Docker контейнерами

---

## 📁 Структура Module 10

```
module_10/
│
├── PLAN.md (цей файл)
├── README.md (загальний огляд)
├── docker-compose.yml (DB + services)
├── requirements.txt (dependencies)
│
├── beginner_edition/
│   ├── README_beginner.md
│   ├── 01_beautifulsoup_basics.py
│   ├── 02_scrape_news_portal.py
│   ├── 03_django_setup.py
│   ├── 04_django_models.py
│   ├── 05_django_crud.py
│   ├── 06_django_forms.py
│   └── examples/
│       └── sample_scraped_data.json
│
├── advanced_edition/
│   ├── README_advanced.md
│   ├── 01_scrapy_project/
│   │   ├── scrapy.cfg
│   │   └── crawler/
│   │       ├── spiders/
│   │       │   ├── news_spider.py
│   │       │   └── product_spider.py
│   │       └── pipelines.py
│   │
│   ├── 02_django_async/
│   │   ├── celery_config.py
│   │   ├── tasks.py
│   │   └── models.py
│   │
│   ├── 03_scrapy_integration/
│   │   ├── django_with_scrapy.py
│   │   └── scheduled_crawler.py
│   │
│   └── 04_production_patterns/
│       ├── caching.py
│       ├── error_handling.py
│       └── monitoring.py
│
├── django_app/
│   ├── manage.py
│   ├── myapp/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   │       ├── base.html
│   │       ├── list.html
│   │       └── form.html
│   │
│   └── config/
│       ├── settings.py
│       └── urls.py
│
├── notebooks/
│   └── Module_10_Complete_Course.ipynb
│
└── tests/
    ├── test_scraping.py
    ├── test_django_models.py
    └── test_forms.py
```

---

## 📚 Beginner Edition (3-4 дня, 3-4 тиск часов)

### Lesson 1: Web Scraping з Beautiful Soup
**Час:** 45-60 хв

**Теорія:**
- HTML/CSS структура
- HTTP requests
- BeautifulSoup парсинг
- Data cleaning & validation

**Практика:**
- Скрапити новини з новинного порталу (укр.net)
- Парсити структуровані дані (заголовок, дата, текст)
- Зберігати в JSON

**Real-world:**
- LinkedIn job scraping
- News aggregation
- Price monitoring

**Exercises:**
1. Скрапити 10 новин
2. Парсити структуровані дані
3. Валідація та очистка

---

### Lesson 2: Web Scraping со Scrapy
**Час:** 60-90 хв

**Теорія:**
- Scrapy архітектура
- Spiders & Pipelines
- Обробка помилок
- Performance optimization

**Практика:**
- Створити Scrapy проект
- Написати spider для новин
- Встроити pipeline для збереження

**Real-world:**
- Large-scale scraping
- Distributed crawling
- Data validation pipelines

**Exercises:**
1. Налаштувати Scrapy проект
2. Написати spider
3. Додати pipeline

---

### Lesson 3: Django базис + ORM
**Час:** 90-120 хв

**Теорія:**
- Django MVT архітектура
- Models (ORM)
- Migrations
- QuerySet API

**Практика:**
- Налаштувати Django проект
- Створити моделі (User, Address, City, Country)
- Міграції на PostgreSQL

**Real-world:**
- E-commerce platforms
- Social networks
- Content management

**Exercises:**
1. Створити Django проект
2. Визначити моделі
3. Запустити міграції

---

### Lesson 4: Django CRUD & Views
**Час:** 60-90 хв

**Теорія:**
- Views (Function-based & Class-based)
- URL routing
- Querysets & filtering
- Relationships

**Практика:**
- Написати CRUD views
- List, Detail, Create, Update, Delete
- Фільтрація і пошук

**Real-world:**
- Admin dashboards
- User management
- Content management

**Exercises:**
1. Написати CRUD views
2. Додати фільтрацію
3. Реалізувати пошук

---

### Lesson 5: Django Forms & Templates
**Час:** 60-90 хв

**Теорія:**
- Model Forms
- Form validation
- CSRF protection
- Template rendering

**Практика:**
- Створити форму для користувача
- HTML шаблони з Bootstrap
- Form processing і validation

**Real-world:**
- Registration forms
- Product filters
- Search interfaces

**Exercises:**
1. Створити ModelForm
2. Дизайнити шаблон
3. Реалізувати validation

---

### Lesson 6: Dockerization & Deployment
**Час:** 45-60 хв

**Теорія:**
- Dockerfile для Django
- Docker-compose setup
- Environment variables
- Volume management

**Практика:**
- Написати Dockerfile
- Налаштувати docker-compose
- Запустити локально

**Real-world:**
- Production deployments
- CI/CD pipelines
- Multi-environment setup

**Exercises:**
1. Написати Dockerfile
2. Налаштувати docker-compose
3. Запустити контейнер

---

## 🚀 Advanced Edition (3-4 дні, 4-6 годин)

### Lesson 1: Scrapy на Production
**Час:** 2-3 години

**Теорія:**
- Scrapy middleware
- Distributed crawling
- Caching & deduplication
- Error handling

**Практика:**
- Написати розширений spider
- Додати middleware для rate limiting
- Реалізувати retry logic

**Real-world:**
- E-commerce price monitoring
- SEO monitoring
- Competitive intelligence

**Advanced Topics:**
- Selenium для JavaScript-heavy sites
- Rotating proxies
- User-Agent rotation

---

### Lesson 2: Django + Celery (Async Tasks)
**Час:** 2-3 години

**Теорія:**
- Task queues
- Celery architecture
- Async/sync patterns
- Error handling & retries

**Практика:**
- Налаштувати Celery з Redis
- Запустити scraping task async
- Периодичні задачі (Celery Beat)

**Real-world:**
- Background jobs
- Email sending
- Data processing pipelines

**Advanced Topics:**
- Celery + Django signals
- Result backends
- Task priority queues

---

### Lesson 3: Scrapy + Django Integration
**Час:** 2-3 години

**Теорія:**
- Запуск Scrapy від Django
- Storing scraped data in Django ORM
- Handling duplicates
- Data enrichment

**Практика:**
- Інтегрувати Scrapy spider у Django
- Зберігати дані в БД
- Scheduling scraping tasks

**Real-world:**
- Data aggregation platforms
- Real estate portals
- Job boards

**Advanced Topics:**
- Change Data Capture (CDC)
- Data versioning
- Conflict resolution

---

### Lesson 4: Production Patterns
**Час:** 2-3 години

**Теорія:**
- Caching (Redis, Django cache)
- Rate limiting
- Monitoring & logging
- Error tracking (Sentry)

**Практика:**
- Додати Redis caching
- Структурований logging
- Error monitoring

**Real-world:**
- High-traffic applications
- Multi-tenant systems
- Microservices

**Advanced Topics:**
- Database optimization (indexes, partitioning)
- Query optimization
- Load balancing

---

## 🛠 Технологічний стак

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API
- **Celery** - Task queue
- **Scrapy** - Web scraping
- **Beautiful Soup** - HTML parsing

### Database
- **PostgreSQL** - Primary DB
- **Redis** - Cache & task broker
- **MongoDB** (optional) - Document storage

### Tools
- **Docker & Docker Compose** - Containerization
- **Pytest** - Testing
- **Black** - Code formatting
- **Pre-commit** - Git hooks

---

## 📊 Практичні Проекти

### Beginner: News Aggregator
```
Вимоги:
- Скрапити новини з 3+ портальних
- Зберігати в БД
- Django CRUD для перегляду
- Фільтрація по категоріям та датам
- Docker контейнер
```

### Advanced: Real Estate Platform
```
Вимоги:
- Scrapy spider для real estate сайтів
- Django моделі для властивостей
- Celery tasks для періодичного обновлення
- Redis caching
- Price tracking з історією
- Email alerts при змінах цін
- Production logging & monitoring
```

---

## 📝 Jupyter Notebook Structure

```
Module_10_Complete_Course.ipynb
├── Introduction
├── Part 1: Web Scraping Basics
│   ├── Теорія HTML/CSS
│   ├── BeautifulSoup приклади
│   ├── Практика
│   └── Вправи
├── Part 2: Scrapy Framework
│   ├── Architecture overview
│   ├── Spider приклади
│   ├── Pipeline демонстрація
│   └── Advanced patterns
├── Part 3: Django Basics
│   ├── MVT架構
│   ├── ORM демонстрація
│   ├── Views & URLs
│   └── Templates
├── Part 4: Django + Scraping
│   ├── Integration patterns
│   ├── Celery tasks
│   ├── Scheduling
│   └── Monitoring
└── Project Walkthroughs
```

---

## 🧪 Testing Strategy

```
tests/
├── test_scraping.py
│   ├── Test BeautifulSoup parsing
│   ├── Test Scrapy spider
│   └── Test error handling
├── test_django_models.py
│   ├── Test model methods
│   ├── Test relationships
│   └── Test querysets
├── test_forms.py
│   ├── Test validation
│   ├── Test model forms
│   └── Test CSRF protection
└── integration_tests.py
    ├── Test scraping + Django
    ├── Test Celery tasks
    └── Test full workflow
```

---

## ✅ Success Criteria

### Beginner
- [ ] Скрапити новини с портального за 10 хвилин
- [ ] Створити Django проект з CRUD операціями
- [ ] Писати ModelForms та templates
- [ ] Dockerизувати Django застосунок
- [ ] Запустити з PostgreSQL в docker-compose

### Advanced
- [ ] Написати production-ready Scrapy spider
- [ ] Інтегрувати Scrapy з Django
- [ ] Запустити async tasks з Celery
- [ ] Додати Redis caching
- [ ] Структурований logging & monitoring

---

## 🎯 Learning Outcomes

**Після завершення модулю:**

✅ Розумієте HTTP запити та HTML парсинг
✅ Вмієте скрапити веб-сайти з BeautifulSoup
✅ Проектуєте scalable spiders з Scrapy
✅ Створюєте CRUD додатки на Django
✅ Обробляєте форми та валідацію
✅ Запускаєте асинхронні задачі з Celery
✅ Інтегруєте scraping з Django
✅ Монітеруєте та логуєте production код
✅ Dockerизуєте Python додатки
✅ Готові до real-world web development

---

## 📈 Time Allocation

| Activity | Time |
|----------|------|
| Beginner Lessons (6) | 6-8 hours |
| Beginner Exercises | 2-3 hours |
| Advanced Lessons (4) | 4-6 hours |
| Advanced Project | 2-3 hours |
| Jupyter Notebook Walkthrough | 1-2 hours |
| **Total** | **15-22 hours** |

---

## 🚀 Next Steps

1. **Створити docker-compose.yml** з PostgreSQL, Redis
2. **Написати Beginner Lesson 1-6**
3. **Написати Advanced Lesson 1-4**
4. **Практичні проекти**
5. **Jupyter notebook**
6. **Testing & documentation**

---

**Ready to build professional web applications! 🎉**
