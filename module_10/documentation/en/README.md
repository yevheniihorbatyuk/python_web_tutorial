# Module 10: Django & Web Scraping - Complete Web Development Course

**Status**: Complete Beginner Edition ✅ | Advanced Edition 🔄
**Target**: Beginner to Advanced Developers
**Duration**: 6-8 hours (Beginner) + 4-6 hours (Advanced)
**Technologies**: Django 5.0, BeautifulSoup, Scrapy, PostgreSQL, Redis, Celery, Docker

---

## 📖 Overview

Module 10 is a comprehensive course on modern web development with Python. You'll learn:

1. **Web Scraping**: From HTML parsing to production-ready crawlers
2. **Django Framework**: Build complete database-driven web applications
3. **Asynchronous Processing**: Background jobs with Celery & Redis
4. **Docker Deployment**: Containerize and deploy applications
5. **Best Practices**: Security, performance, monitoring, testing

This course bridges the gap between learning Python fundamentals and building real-world applications.

---

## 🎯 Two Learning Paths

### 👶 Beginner Edition (6-8 hours)
**Perfect for**: Beginners and Junior Developers

Practical, hands-on learning with real examples:
- Lesson 1: BeautifulSoup (HTML parsing)
- Lesson 2: Complete news scraper project
- Lesson 3: Django setup and architecture
- Lesson 4: Database models and relationships
- Lesson 5: CRUD views (Create, Read, Update, Delete)
- Lesson 6: Forms, validation, and Bootstrap templates

**Outcome**: Build a complete user management app with web scraping integration

**Start here**: [`beginner_edition/README_beginner.md`](beginner_edition/README_beginner.md)

### 🚀 Advanced Edition (4-6 hours)
**Perfect for**: Intermediate to Senior Developers

Production-ready patterns and scalability:
- Lesson 1: Scrapy framework for large-scale scraping
- Lesson 2: Celery + Redis for async tasks
- Lesson 3: Scrapy + Django integration
- Lesson 4: Production patterns (caching, monitoring, logging)

**Outcome**: Enterprise-ready web scraping and data pipeline architecture

**Start here**: `advanced_edition/README_advanced.md` (coming soon)

---

## 📁 Project Structure

```
module_10/
│
├── README.md                        # This file
├── PLAN.md                          # Complete implementation plan
├── requirements.txt                 # All dependencies
├── docker-compose.yml               # Full stack setup
├── .env.example                     # Environment template
├── Dockerfile                       # Container configuration
│
├── beginner_edition/                # ✅ COMPLETE
│   ├── README_beginner.md           # Beginner guide & learning path
│   ├── 01_beautifulsoup_basics.py   # Lesson 1: HTML parsing
│   ├── 02_scrape_news_portal.py     # Lesson 2: Complete scraper
│   ├── 03_django_setup.py           # Lesson 3: Django architecture
│   ├── 04_django_models.py          # Lesson 4: Database models
│   ├── 05_django_crud.py            # Lesson 5: CRUD operations
│   ├── 06_django_forms.py           # Lesson 6: Forms & templates
│   └── examples/
│       └── sample_data.json
│
├── advanced_edition/                # 🔄 IN PROGRESS
│   ├── README_advanced.md
│   ├── 01_scrapy_framework.py
│   ├── 02_celery_async.py
│   ├── 03_scrapy_django_integration.py
│   ├── 04_production_patterns.py
│   └── scrapy_project/
│       ├── spiders/
│       ├── pipelines.py
│       └── settings.py
│
├── django_app/                      # Complete Django application
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── users/
│   │   ├── models.py                # Country, City, User models
│   │   ├── views.py                 # CRUD views
│   │   ├── forms.py                 # ModelForms with validation
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templates/
│   │       ├── base.html            # Bootstrap base
│   │       ├── user_list.html
│   │       ├── user_detail.html
│   │       ├── user_form.html
│   │       └── user_confirm_delete.html
│   └── static/
│       ├── css/
│       └── js/
│
├── notebooks/                       # Interactive Jupyter notebooks
│   └── Module_10_Complete_Course.ipynb
│
├── tests/                           # Test suite
│   ├── test_scraping.py
│   ├── test_django_models.py
│   ├── test_forms.py
│   └── conftest.py
│
└── docs/                            # Additional documentation
    ├── DEPLOYMENT.md
    ├── PERFORMANCE.md
    └── TROUBLESHOOTING.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- PostgreSQL (or use Docker)

### 5-Minute Setup

```bash
# 1. Clone the module
cd module_10

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run first lesson
python beginner_edition/01_beautifulsoup_basics.py

# Output: Web scraping guide and examples
```

### Using Docker (Recommended)

```bash
# 1. Start all services (PostgreSQL, Redis, pgAdmin)
docker-compose up -d

# 2. Enter app container
docker-compose exec app bash

# 3. Inside container
pip install -r requirements.txt
python beginner_edition/01_beautifulsoup_basics.py

# Access services:
# - pgAdmin: http://localhost:5050
# - Django: http://localhost:8000
```

---

## 📚 Learning Path

### Beginner Edition (Recommended Order)

1. **[Lesson 1: BeautifulSoup Basics](beginner_edition/01_beautifulsoup_basics.py)** (45 min)
   - What: HTML parsing with BeautifulSoup
   - Why: Foundation for web scraping
   - How: CSS selectors, data extraction, error handling
   - Example: Scrape quotes.toscrape.com

2. **[Lesson 2: News Portal Scraper](beginner_edition/02_scrape_news_portal.py)** (60 min)
   - What: Complete production scraper
   - Why: Real-world workflow integration
   - How: Fetch → Parse → Validate → Clean → Store
   - Example: Multi-page scraper with database persistence

3. **[Lesson 3: Django Setup](beginner_edition/03_django_setup.py)** (90 min)
   - What: Django project initialization
   - Why: Framework for web applications
   - How: MVT architecture, settings, management commands
   - Example: Create project, configure database

4. **[Lesson 4: Django Models](beginner_edition/04_django_models.py)** (90 min)
   - What: Database schema definition
   - Why: ORM for type-safe queries
   - How: Models, fields, relationships, QuerySets
   - Example: Country → City → User hierarchy

5. **[Lesson 5: CRUD Views](beginner_edition/05_django_crud.py)** (75 min)
   - What: Create, Read, Update, Delete operations
   - Why: Core web application functionality
   - How: FBV vs CBV, generic views, URL routing
   - Example: User management CRUD

6. **[Lesson 6: Forms & Templates](beginner_edition/06_django_forms.py)** (75 min)
   - What: User input & HTML generation
   - Why: Interactive web applications
   - How: ModelForms, validation, Bootstrap, inheritance
   - Example: User registration with validation

**Total Time**: 6-8 hours

---

## 💻 Technologies Used

### Backend
- **Django 5.0** - Web framework (MVT)
- **BeautifulSoup 4** - HTML parsing
- **Scrapy 2.11** - Large-scale web scraping
- **Celery 5.3** - Async task queue
- **Django REST Framework** - REST APIs (advanced)

### Database & Cache
- **PostgreSQL 16** - Primary database (relational)
- **Redis 7** - Cache & message broker
- **SQLite** - For beginner examples

### Development & Deployment
- **Docker & Docker Compose** - Containerization
- **Pytest** - Testing framework
- **Black** - Code formatting
- **Jupyter** - Interactive notebooks

---

## 🎯 Key Learning Outcomes

After completing **Beginner Edition**, you can:

✅ **Web Scraping**
- Fetch pages with HTTP requests
- Parse HTML with CSS selectors
- Extract and validate data
- Handle errors and retries
- Store data in databases
- Respect robots.txt and add rate limiting

✅ **Django Fundamentals**
- Explain MVT architecture
- Create projects and apps
- Define models with relationships
- Run migrations
- Build CRUD operations
- Create forms with validation
- Design templates with inheritance
- Understand security (CSRF, escaping)

✅ **Database Design**
- Model relationships (1:1, 1:N, N:M)
- Create indexes for performance
- Query with filters and joins
- Handle duplicates and constraints
- Migrate schema changes

✅ **Web Development Best Practices**
- Security (password hashing, CSRF protection)
- Validation (client & server side)
- Error handling and logging
- Testing fundamentals
- Docker basics

✅ **Ready For**
- Building real Django applications
- Scraping public data responsibly
- Creating REST APIs (with DRF)
- Deploying to production
- Advanced topics (caching, async tasks)

---

## 📖 Documentation

### For Beginners
Start with these resources:

1. **[Beginner README](beginner_edition/README_beginner.md)** - Complete learning guide
2. **Lessons 1-6** - Step-by-step tutorials with code
3. **Examples** - Real working code you can run
4. **Exercises** - Practice problems to reinforce learning

### For Advanced Learners
(Coming soon in Advanced Edition)

1. **Scrapy Framework** - Industrial-scale scraping
2. **Celery Async** - Background tasks and scheduling
3. **REST APIs** - Build APIs with Django REST Framework
4. **Production Patterns** - Caching, monitoring, logging
5. **Deployment** - Docker, servers, CI/CD

### For Everyone
- `PLAN.md` - High-level overview
- `docker-compose.yml` - Infrastructure setup
- `requirements.txt` - All dependencies
- `.env.example` - Configuration template

---

## 🔧 Common Tasks

### Run a Specific Lesson
```bash
python beginner_edition/01_beautifulsoup_basics.py
python beginner_edition/02_scrape_news_portal.py
python beginner_edition/03_django_setup.py
# etc.
```

### Start Django Development Server
```bash
cd django_app
python manage.py migrate
python manage.py runserver
# Visit http://localhost:8000
```

### Access Django Admin
```bash
python manage.py createsuperuser
# Visit http://localhost:8000/admin
```

### Query Database (Django Shell)
```bash
python manage.py shell

from users.models import User
User.objects.all()
User.objects.filter(city__name="Kyiv")
exit()
```

### Run Tests
```bash
pytest tests/
pytest tests/test_scraping.py -v
```

### Check Docker Services
```bash
docker-compose ps
docker-compose logs postgres
docker-compose exec postgres psql -U goit -d goit_module10
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
```bash
pip install -r requirements.txt
```

### "Connection refused" (PostgreSQL)
```bash
# Use Docker
docker-compose up -d postgres

# Or install locally and start:
# macOS: brew services start postgresql
# Ubuntu: sudo service postgresql start
```

### "CSRF token missing" or "403 Forbidden"
```django
{# Add to template #}
{% csrf_token %}
```

### "No such table" (Database error)
```bash
python manage.py migrate
```

### Port already in use (8000, 5432, etc.)
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

---

## 📊 Progress Tracking

### Beginner Edition Status
- [x] Lesson 1: BeautifulSoup Basics
- [x] Lesson 2: News Portal Scraper
- [x] Lesson 3: Django Setup
- [x] Lesson 4: Django Models
- [x] Lesson 5: CRUD Views
- [x] Lesson 6: Forms & Templates
- [x] README with learning path
- [ ] Complete Django app with templates
- [ ] Unit tests for all lessons
- [ ] Exercises (4 levels)

### Advanced Edition Status
- [ ] Lesson 1: Scrapy Framework
- [ ] Lesson 2: Celery Async
- [ ] Lesson 3: Integration
- [ ] Lesson 4: Production Patterns
- [ ] README with advanced topics
- [ ] Jupyter notebook

---

## 🎓 Next Steps

### After Completing Beginner Edition:

1. **Do the Exercises**
   - Practice with provided exercises
   - Build your own projects
   - Deploy locally with Docker

2. **Join Advanced Edition**
   - Learn Scrapy for industrial scraping
   - Master Celery async tasks
   - Build REST APIs with DRF

3. **Build Real Projects**
   - Job board scraper
   - Price monitoring system
   - Real estate listings aggregator
   - News feed aggregator

4. **Get Job-Ready**
   - Contribute to open source
   - Build portfolio projects
   - Learn deployment (AWS, Heroku, DigitalOcean)
   - Practice coding interviews

---

## 📚 External Resources

### Learning
- [Django Official Documentation](https://docs.djangoproject.com/)
- [BeautifulSoup 4 Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Real Python Django Tutorials](https://realpython.com/search?q=django)
- [MDN Django Tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)

### Practice Scraping (Legal)
- https://quotes.toscrape.com
- https://books.toscrape.com
- https://httpbin.org

### Tools
- [Postman](https://www.postman.com/) - API testing
- [VS Code](https://code.visualstudio.com/) - Code editor
- [DataGrip](https://www.jetbrains.com/datagrip/) - Database IDE
- [Robo 3T](https://robomongo.org/) - MongoDB GUI

---

## ⚖️ Legal & Ethics

### Web Scraping Guidelines
- ✅ **DO**:
  - Read robots.txt
  - Add delays between requests
  - Respect server resources
  - Use legal data sources
  - Identify yourself (User-Agent)
  - Cache data locally

- ❌ **DON'T**:
  - Ignore robots.txt
  - Hammer servers (no delays)
  - Bypass authentication
  - Steal copyrighted content
  - Use scraped data commercially without permission
  - Scrape personal data

### Recommended Data Sources
- Public APIs (preferred)
- Data marked CC0 or CC-BY
- Sites with `/robots.txt` allowing scraping
- Services providing data export
- Your own datasets

---

## 🤝 Contributing

Have improvements or found bugs? Let me know!

---

## 📝 License

These materials are provided for educational purposes.

---

## 🎉 You're Ready!

**Start with**: [`beginner_edition/README_beginner.md`](beginner_edition/README_beginner.md)

Follow the lessons in order, do the exercises, and you'll be building web applications in no time.

**Happy learning! 🚀**

---

**Last Updated**: December 2024
**Version**: 1.0 (Beginner Edition Complete)
