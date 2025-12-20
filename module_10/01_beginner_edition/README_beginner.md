# Module 10 - Beginner Edition: Web Scraping & Django Fundamentals

**Target**: Beginners & Junior Developers
**Duration**: 6-8 hours
**Technologies**: Django 5.0, BeautifulSoup, PostgreSQL, Bootstrap

---

## 📚 Learning Path

This Beginner Edition takes you from "What is web scraping?" to building a complete Django CRUD application. Each lesson builds on the previous one.

### Lesson 1: BeautifulSoup Basics (45-60 min)
- **Goal**: Understand HTML parsing and web scraping fundamentals
- **Topics**:
  - HTTP requests and responses
  - HTML/CSS structure
  - BeautifulSoup parsing
  - Data extraction and validation
  - Error handling

- **Practical Skills**:
  - Parse HTML with CSS selectors
  - Extract structured data (title, date, content)
  - Handle network errors with retries
  - Validate and clean scraped data

- **Example**: Scrape quotes and books from `quotes.toscrape.com` and `books.toscrape.com`

- **File**: `code/01_beautiful_soup_practice.py`
- **Run**: `python code/01_beautiful_soup_practice.py quotes`

### Lesson 2: Complete News Scraping Project (60-90 min)
- **Goal**: Build a production-ready web scraper with error handling and data persistence
- **Topics**:
  - Complete scraping workflow (fetch → parse → validate → store)
  - Data validation and cleaning
  - Duplicate detection
  - Database persistence (SQLite)
  - Logging and error handling

- **Components**:
  - `NewsPortalScraper`: Fetches pages with retry logic and exponential backoff
  - `NewsDataValidator`: Validates article quality
  - `NewsDatabase`: Stores to SQLite with duplicate prevention
  - `run_complete_workflow()`: Demonstrates full pipeline

- **Key Concepts**:
  - Dataclasses for type-safe data models
  - Exception handling for network failures
  - SQL constraints for data integrity
  - Rate limiting for responsible scraping

- **File**: `code/02_real_world_scraping.py`
- **Run**: `python code/02_real_world_scraping.py`

### Lesson 3: Django Setup & Architecture (90-120 min)
- **Goal**: Understand Django's MVT architecture and set up a project
- **Topics**:
  - Django MVT (Model-View-Template) architecture
  - Project vs App structure
  - Settings configuration
  - Database setup (PostgreSQL)
  - Django management commands
  - Migrations explained

- **Key Concepts**:
  - `models.py`: Database schema (ORM)
  - `views.py`: Business logic
  - `urls.py`: URL routing
  - `templates/`: HTML with template language
  - `manage.py`: CLI tool for everything

- **Setup Steps**:
  ```bash
  django-admin startproject config .
  python manage.py startapp users
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  ```

- **File**: `code/03_django_setup_guide.py`
- **Run**: Use the working app in `../03_django_app/` for hands-on setup

### Lesson 4: Django Models & Relationships (90-120 min)
- **Goal**: Define database models with proper relationships
- **Topics**:
  - Model field types (CharField, IntegerField, DateTimeField, etc.)
  - Field options (null, blank, unique, default)
  - Relationships: ForeignKey, OneToOne, ManyToMany
  - Model methods and `__str__`
  - QuerySet operations (filter, get, count, order_by)
  - Migrations workflow

- **Data Model**:
  ```
  Country (1)
    ↓ (1:N)
  City (many)
    ↓ (N:1)
  User (many)
  ```

- **Key Queries**:
  ```python
  # Get all users
  User.objects.all()

  # Filter by city
  users = User.objects.filter(city__country__name="Ukraine")

  # Count users per city
  City.objects.annotate(Count('user'))
  ```

- **File**: `code/04_django_models.py`
- **Run**: Use the models in `../03_django_app/users/models.py`

### Lesson 5: Django CRUD Views (60-90 min)
- **Goal**: Build Create, Read, Update, Delete operations
- **Topics**:
  - Function-based views (FBV) vs Class-based views (CBV)
  - Generic views (ListView, DetailView, CreateView, UpdateView, DeleteView)
  - URL routing with path parameters
  - Filtering and searching
  - Pagination
  - Redirects

- **CRUD Operations**:
  ```
  List   → GET /users/
  Detail → GET /users/1/
  Create → GET /users/create/ + POST
  Update → GET /users/1/edit/ + POST
  Delete → GET /users/1/delete/ + POST
  ```

- **File**: `code/05_django_crud_views.py`
- **Run**: Use the views in `../03_django_app/users/views.py`

### Lesson 6: Django Forms & Templates (60-90 min)
- **Goal**: Build interactive forms and HTML templates
- **Topics**:
  - Django Forms and ModelForms
  - Form validation (clean methods)
  - Template tags (if, for, with, include, extends)
  - Template filters (lower, date, truncatewords)
  - Template inheritance (base.html)
  - Bootstrap integration
  - CSRF protection

- **Form Example**:
  ```python
  class UserForm(forms.ModelForm):
      class Meta:
          model = User
          fields = ['first_name', 'last_name', 'email', 'city']
  ```

- **Template Inheritance**:
  ```html
  {% extends 'base.html' %}
  {% block content %}
      <h1>{{ page_title }}</h1>
  {% endblock %}
  ```

- **File**: `code/06_django_forms.py`
- **Run**: Use the forms/templates in `../03_django_app/users/`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or use Docker)
- pip

### Installation

1. **Clone/download the module**:
   ```bash
   cd module_10
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Run lessons**:
   ```bash
   # Lesson 1: BeautifulSoup
   python 01_beginner_edition/code/01_beautiful_soup_practice.py quotes

   # Lesson 2: News Scraper
   python 01_beginner_edition/code/02_real_world_scraping.py

   # Lesson 3: Django Setup
   cd 03_django_app
   python manage.py migrate

   # Lesson 4: Models
   python manage.py shell

   # Lesson 5: CRUD Views
   python manage.py runserver

   # Lesson 6: Forms & Templates
   open http://localhost:8000/users/
   ```

### Using Docker

```bash
# Start services
docker-compose up -d

# Enter app container
docker-compose exec app bash

# Inside container
pip install -r requirements.txt
python 01_beginner_edition/code/01_beautiful_soup_practice.py quotes
```

---

## 📁 Project Structure

```
beginner_edition/
├── README_beginner.md                # This file
├── code/
│   ├── 01_beautiful_soup_practice.py # Lesson 1: Practical scraping
│   ├── 02_real_world_scraping.py     # Lesson 2: End-to-end pipeline
│   ├── 03_django_setup_guide.py      # Lesson 3: Setup references
│   ├── 04_django_models.py           # Lesson 4: Model patterns
│   ├── 05_django_crud_views.py       # Lesson 5: CRUD patterns
│   └── 06_django_forms.py            # Lesson 6: Forms/templates
├── theory/                           # Concept explanations
├── tutorials/                        # Step-by-step exercises
├── _old_files/                       # Archived print-heavy lesson scripts
└── examples/
    └── sample_scraped_data.json      # Example output
```

---

## 🎯 Key Concepts Summary

### Web Scraping
- **HTTP Requests**: GET/POST to fetch pages
- **HTML Parsing**: BeautifulSoup to extract data
- **CSS Selectors**: `.class`, `#id`, `tag > child`
- **Data Validation**: Check quality before storing
- **Error Handling**: Retry logic, proper exceptions
- **Ethics**: Respect robots.txt, add delays, use legal sources

### Django Basics
- **MVT Pattern**: Model (DB) → View (Logic) → Template (HTML)
- **ORM**: Python classes → SQL tables
- **Migrations**: Version control for database schema
- **Views**: Functions/classes that handle requests
- **URLs**: Map paths to views
- **Forms**: Validation and security
- **Templates**: HTML with Django template language

### Database Design
- **Primary Key**: Unique identifier (auto-increment)
- **Foreign Key**: Link to another table (1:N)
- **One-to-One**: Unique relation (1:1)
- **Many-to-Many**: Multiple relations (N:M)
- **Indexes**: Speed up queries
- **Constraints**: Data integrity

---

## 💡 Common Tasks

### Task 1: Run Lesson
```bash
python 01_beginner_edition/code/01_beautiful_soup_practice.py quotes
python 01_beginner_edition/code/02_real_world_scraping.py
```

### Task 2: Start Django Project
```bash
# Create project
django-admin startproject config .

# Create app
python manage.py startapp users

# Configure database in config/settings.py

# Create tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Task 3: Query Database (Django Shell)
```bash
python manage.py shell

# In shell:
from users.models import User, City

# Get all users
User.objects.all()

# Get specific user
user = User.objects.get(email="john@example.com")

# Filter users
users = User.objects.filter(city__name="Kyiv")

# Count
User.objects.count()

# Exit
exit()
```

### Task 4: Create Migration
```bash
# After modifying models.py
python manage.py makemigrations

# Review migration file
cat users/migrations/0001_initial.py

# Apply to database
python manage.py migrate
```

### Task 5: Scrape Data (from Lesson 2)
```bash
python 01_beginner_edition/code/02_real_world_scraping.py

# Creates:
# - /tmp/news_demo.db (SQLite)
# - /tmp/news_export.json (JSON export)
```

---

## 🔍 Learning Resources

### Documentation
- [Django Official Docs](https://docs.djangoproject.com/)
- [BeautifulSoup 4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python Requests Library](https://requests.readthedocs.io/)

### Scraping Practice Sites (Legal & Safe)
- `https://quotes.toscrape.com` - Quotes (perfect for learning)
- `https://books.toscrape.com` - Books (with pagination)
- `https://httpbin.org` - Test requests
- `https://httpbin.org/delay/1` - Test timeout handling

### Django Tutorials
- [Django for Beginners](https://learndjango.com/)
- [Real Python Django Tutorials](https://realpython.com/search?q=django)
- [MDN Django Tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)

---

## ⚠️ Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'django'"
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

### Issue 2: "Connection refused" (PostgreSQL)
```bash
# Solution: Use Docker
docker-compose up -d postgres

# Or install locally:
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
```

### Issue 3: "CSRF token missing" (Form error)
```bash
# Solution: Add to template
{% csrf_token %}
```

### Issue 4: "No such table: users_user"
```bash
# Solution: Run migrations
python manage.py migrate
```

### Issue 5: "Allowed hosts" error
```bash
# Solution: Edit config/settings.py
ALLOWED_HOSTS = ['*']  # For development only!
```

---

## 📝 Exercises & Assignments

### Exercise 1: Extend BeautifulSoup Example
**Difficulty**: ⭐

Add to `code/01_beautiful_soup_practice.py`:
- Scrape `books.toscrape.com`
- Extract: title, price, availability
- Save to JSON
- Handle pagination (multiple pages)

### Exercise 2: Advanced News Scraper
**Difficulty**: ⭐⭐

Modify `code/02_real_world_scraping.py`:
- Add filtering by publication date
- Implement search functionality
- Calculate reading time (word count)
- Add export to CSV

### Exercise 3: Build Complete Django App
**Difficulty**: ⭐⭐⭐

Create a working Django project:
1. Define models (Country, City, User)
2. Create migrations
3. Build CRUD views
4. Create forms with validation
5. Design Bootstrap templates
6. Add search and filtering
7. Deploy with Docker

**Checklist**:
- [ ] Models defined with relationships
- [ ] Migrations applied to PostgreSQL
- [ ] All CRUD views working
- [ ] Forms with validation
- [ ] Beautiful Bootstrap templates
- [ ] Search/filter functionality
- [ ] Admin panel configured
- [ ] No console errors

### Exercise 4: Combine Scraping + Django
**Difficulty**: ⭐⭐⭐⭐

Create custom management command:
```bash
# Create command
python manage.py startapp news_scraper

# Create command file
touch news_scraper/management/commands/scrape_news.py
```

Command should:
- Scrape quotes.toscrape.com
- Parse data
- Save to Django models
- Handle duplicates
- Log progress

---

## 🎓 Next Steps

### After Completing Beginner Edition

1. **Do the Exercises** (1-4)
   - Start with Exercise 1 & 2 (scraping)
   - Progress to Exercise 3 (full Django app)
   - Challenge yourself with Exercise 4

2. **Build Your Own Project**
   - Choose a legal data source
   - Scrape real data
   - Store in Django
   - Create user interface

3. **Move to Advanced Edition**
   - Learn Scrapy framework (large-scale scraping)
   - Master Django REST Framework (APIs)
   - Add Celery async tasks
   - Production deployment

4. **Real-World Practice**
   - Job boards scraper
   - Product price monitor
   - News aggregator
   - Real estate listings

---

## 📞 Getting Help

1. **Read the code comments** - Every lesson has detailed explanations
2. **Check Django docs** - Official documentation is excellent
3. **Search errors** - Most errors have solutions on Stack Overflow
4. **Ask in communities** - Django Reddit, Stack Overflow, Discord

---

## ✅ Success Criteria

You've completed Beginner Edition when you can:

- [ ] **Web Scraping**:
  - Fetch pages with requests
  - Parse HTML with BeautifulSoup
  - Extract structured data
  - Handle errors gracefully
  - Save to database

- [ ] **Django Basics**:
  - Explain MVT architecture
  - Create Django project & apps
  - Define models with relationships
  - Run migrations
  - Use Django shell

- [ ] **CRUD Operations**:
  - Build ListView, DetailView
  - Create new records
  - Update existing records
  - Delete records
  - Add filtering & search

- [ ] **Forms & Templates**:
  - Create ModelForms
  - Render forms in templates
  - Validate user input
  - Use Bootstrap for styling
  - Understand template inheritance

- [ ] **Deployment**:
  - Run Django with PostgreSQL
  - Use Docker for services
  - Understand environment variables

---

## 🎉 You're Ready!

Once you've completed this Beginner Edition with all exercises, you're ready for:
- Advanced Edition (Scrapy, Celery, DRF)
- Real-world Django projects
- Web development career

**Happy coding! 🚀**
