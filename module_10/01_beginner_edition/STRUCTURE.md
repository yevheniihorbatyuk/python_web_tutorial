# Course Structure & Organization

## Overview

This Beginner Edition is organized into **6 complete lessons** with three components for each:

1. **Theory** (Markdown) - Concepts and explanations
2. **Code** (Python) - Working implementations
3. **Tutorial** (Markdown) - Step-by-step guides

---

## File Organization

```
01_beginner_edition/
│
├── 📄 README.md                         # Main course guide
├── 📄 STRUCTURE.md                      # This file
├── 📄 GETTING_STARTED.md                # Quick start guide
│
├── 📁 theory/                           # Concept explanations
│   ├── 01_beautiful_soup_concepts.md        (1.1 KB - HTML & parsing)
│   ├── 02_real_world_scraping.md            (6.3 KB - Workflow & patterns)
│   ├── 03_django_fundamentals.md            (13 KB - Architecture & setup)
│   ├── 04_django_models_orm.md              (15 KB - Database design)
│   ├── 05_django_views_urls.md              (13 KB - Web views)
│   └── 06_django_forms_templates.md         (14 KB - Forms & UI)
│
├── 📁 code/                             # Production implementations
│   ├── 01_beautiful_soup_practice.py        (11 KB - Scraper class)
│   ├── 02_real_world_scraping.py            (14 KB - Complete workflow)
│   ├── 03_django_setup_guide.py             (16 KB - Setup reference)
│   ├── 04_django_models.py                  (15 KB - Model patterns)
│   ├── 05_django_crud_views.py              (16 KB - CRUD views)
│   └── 06_django_forms.py                   (22 KB - Forms & templates)
│
└── 📁 tutorials/                        # Step-by-step guides
    ├── 01_scraping_tutorial.md              (6.6 KB - 8 exercises)
    ├── 02_scraping_project_tutorial.md      (8.4 KB - Full project)
    ├── 03_django_setup_tutorial.md          (8.2 KB - Django creation)
    ├── 04_django_models_tutorial.md         (9.8 KB - 12 exercises)
    ├── 05_django_crud_tutorial.md           (19 KB - Full application)
    └── 06_django_forms_templates_tutorial.md (21 KB - Advanced UI)
```

---

## Lesson Breakdown

### Lesson 1: Beautiful Soup Web Scraping
**Duration**: 2-3 hours | **Difficulty**: Beginner

**What you'll learn:**
- HTTP requests with requests library
- HTML parsing with Beautiful Soup
- CSS selectors
- Data extraction and cleaning
- JSON export

**Files:**
- 📖 [theory/01_beautiful_soup_concepts.md](theory/01_beautiful_soup_concepts.md)
- 💻 [code/01_beautiful_soup_practice.py](code/01_beautiful_soup_practice.py)
- 📝 [tutorials/01_scraping_tutorial.md](tutorials/01_scraping_tutorial.md)

**Prerequisites:** Python 3.7+, pip

**Next:** Lesson 2

---

### Lesson 2: Real-World News Scraping Project
**Duration**: 3-4 hours | **Difficulty**: Beginner-Intermediate

**What you'll learn:**
- Complete scraping workflow
- Retry logic and exponential backoff
- Data validation and cleaning
- SQLite database persistence
- Error logging and handling
- Project organization

**Files:**
- 📖 [theory/02_real_world_scraping.md](theory/02_real_world_scraping.md)
- 💻 [code/02_real_world_scraping.py](code/02_real_world_scraping.py)
- 📝 [tutorials/02_scraping_project_tutorial.md](tutorials/02_scraping_project_tutorial.md)

**Prerequisites:** Lesson 1

**Key Concepts:**
- NewsArticle dataclass
- NewsPortalScraper with retries
- NewsDataValidator
- NewsDatabase
- Logging patterns

**Next:** Lesson 3

---

### Lesson 3: Django Project Setup
**Duration**: 2-3 hours | **Difficulty**: Beginner-Intermediate

**What you'll learn:**
- Django project structure
- App organization
- Settings configuration
- Database setup (PostgreSQL)
- Migrations system
- Django admin interface

**Files:**
- 📖 [theory/03_django_fundamentals.md](theory/03_django_fundamentals.md)
- 💻 [code/03_django_setup_guide.py](code/03_django_setup_guide.py)
- 📝 [tutorials/03_django_setup_tutorial.md](tutorials/03_django_setup_tutorial.md)

**Prerequisites:** Lesson 1-2 (recommended)

**Key Concepts:**
- MVT architecture
- Project vs App
- settings.py configuration
- manage.py commands
- Migration workflow
- Admin customization

**Next:** Lesson 4

---

### Lesson 4: Django Models & ORM
**Duration**: 3-4 hours | **Difficulty**: Intermediate

**What you'll learn:**
- Django model definition
- Field types and options
- Relationships (ForeignKey, OneToOne, ManyToMany)
- QuerySet operations
- Field lookups and filtering
- Aggregation and annotation
- Query optimization

**Files:**
- 📖 [theory/04_django_models_orm.md](theory/04_django_models_orm.md)
- 💻 [code/04_django_models.py](code/04_django_models.py)
- 📝 [tutorials/04_django_models_tutorial.md](tutorials/04_django_models_tutorial.md)

**Prerequisites:** Lesson 3

**Models Used:**
- Country (top-level)
- City (many-to-one with Country)
- User (many-to-one with City)

**Key Concepts:**
- CharField, IntegerField, DateTimeField, etc.
- null, blank, unique, default, db_index
- ForeignKey relationships
- QuerySet: filter, exclude, get, count, etc.
- Field lookups: exact, contains, startswith, range, gt, lt, isnull
- Related queries with __
- Q objects for complex queries
- Aggregation with Count, Sum, Avg

**Next:** Lesson 5

---

### Lesson 5: Django CRUD Views
**Duration**: 4-5 hours | **Difficulty**: Intermediate

**What you'll learn:**
- Class-Based Views (ListView, DetailView, CreateView, UpdateView, DeleteView)
- URL routing and path converters
- Form processing
- Pagination
- Searching and filtering
- Request/response handling

**Files:**
- 📖 [theory/05_django_views_urls.md](theory/05_django_views_urls.md)
- 💻 [code/05_django_crud_views.py](code/05_django_crud_views.py)
- 📝 [tutorials/05_django_crud_tutorial.md](tutorials/05_django_crud_tutorial.md)

**Prerequisites:** Lesson 4

**Views Created:**
- UserListView (with search/filter/pagination)
- UserDetailView
- UserCreateView
- UserUpdateView
- UserDeleteView
- Same for Country and City

**Key Concepts:**
- CBV methods: get_queryset(), get_context_data()
- reverse_lazy for redirects
- Form processing: form_valid()
- select_related() for optimization
- Pagination with paginate_by
- URL naming with app_name

**Next:** Lesson 6

---

### Lesson 6: Django Forms & Templates
**Duration**: 4-5 hours | **Difficulty**: Intermediate-Advanced

**What you'll learn:**
- ModelForm creation
- Field-level validation (clean_<field>)
- Form-level validation (clean)
- Custom widgets
- Template syntax (variables, tags, filters)
- Template inheritance
- Bootstrap integration
- Static files management
- CSRF protection

**Files:**
- 📖 [theory/06_django_forms_templates.md](theory/06_django_forms_templates.md)
- 💻 [code/06_django_forms.py](code/06_django_forms.py)
- 📝 [tutorials/06_django_forms_templates_tutorial.md](tutorials/06_django_forms_templates_tutorial.md)

**Prerequisites:** Lesson 5

**Forms Created:**
- CountryForm with validation
- CityForm with validation
- UserForm with custom validation

**Templates Created:**
- base.html (inheritance base)
- user_list.html (list with search/filter/pagination)
- user_detail.html (single record)
- user_form.html (create/edit form)
- user_confirm_delete.html (delete confirmation)

**Key Concepts:**
- ModelForm Meta class
- Custom validation methods
- Widget customization with attrs
- Template tags: if, for, with, include, extends, block
- Template filters: date, default, truncatewords, lower, upper
- Bootstrap 5 classes
- {% csrf_token %} for security
- Messages framework for feedback

**Next:** Advanced Edition (optional)

---

## Learning Pathways

### Path 1: Theory → Code → Tutorial (Recommended)
Best for understanding concepts deeply

1. Read **theory file** (10-20 min)
2. Study **code file** (15-30 min)
3. Follow **tutorial** (1-2 hours)
4. Modify code examples
5. Complete exercises

### Path 2: Code → Tutorial → Theory
Best for hands-on learners

1. Study **code file** (15-30 min)
2. Follow **tutorial** (1-2 hours)
3. Read **theory file** to deepen understanding (10-20 min)
4. Experiment and modify

### Path 3: Tutorial → Code → Theory (Self-Paced)
Best for learn-by-doing people

1. Follow **tutorial** (1-2 hours)
2. Reference **code file** when needed (as-needed)
3. Read **theory file** for clarification (as-needed)
4. Build projects applying concepts

---

## Content Organization Within Files

### Theory Files Structure
Each theory file contains:
1. **Overview** - What you'll learn
2. **Key Concepts** - Fundamental ideas
3. **Detailed Explanations** - In-depth coverage
4. **Examples** - Code snippets showing usage
5. **Best Practices** - Production patterns
6. **Common Pitfalls** - What to avoid
7. **Official Links** - External resources
8. **Key Takeaways** - Summary points

### Code Files Structure
Each code file contains:
1. **Module Docstring** - Purpose and contents
2. **Classes and Functions** - Working implementations
3. **Part 1-5** - Organized by topic
4. **Examples** - How to use the code
5. **Demonstration Function** - Run to see it work
6. **Next Steps** - What to learn next

### Tutorial Files Structure
Each tutorial file contains:
1. **Prerequisites** - What you need first
2. **Step 1-10** - Progressive exercises
3. **Expected Output** - What should happen
4. **Code Blocks** - Ready to copy-paste
5. **Verification** - How to check your work
6. **Common Issues** - Troubleshooting
7. **Key Takeaways** - What you learned
8. **Next Lesson** - Progression path

---

## Dependencies

### Lesson 1-2: Beautiful Soup
```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

### Lesson 3-6: Django
```
Django>=4.2.0
psycopg2-binary>=2.9.0  # PostgreSQL driver
python-dotenv>=0.20.0   # Environment variables
```

### Optional for Learning
```
ipython              # Better Python shell
pytest               # Testing
django-debug-toolbar # Development tool
```

---

## Recommended Study Schedule

### Full-Time (1 Week)
- Day 1: Lessons 1-2 (Scraping)
- Day 2-3: Lesson 3-4 (Django Setup & Models)
- Day 4-5: Lesson 5-6 (Views, Forms, Templates)
- Day 6-7: Review & Build project

### Part-Time (3-4 Weeks)
- Week 1: Lesson 1-2 (Scraping)
- Week 2: Lesson 3-4 (Django Setup & Models)
- Week 3: Lesson 5 (Views)
- Week 4: Lesson 6 (Forms & Templates)

### Self-Paced (Flexible)
- Study at your own pace
- Spend extra time on difficult concepts
- Build projects alongside lessons
- Review as needed

---

## Progression Map

```
START
  ↓
Lesson 1: Beautiful Soup Basics
  ├─ Theory: HTML & CSS Selectors
  ├─ Code: QuoteScraper class
  └─ Tutorial: 8 exercises
  ↓
Lesson 2: Real-World Scraping Project
  ├─ Theory: Complete workflow
  ├─ Code: News scraper with DB
  └─ Tutorial: Full project
  ↓
Lesson 3: Django Setup
  ├─ Theory: MVT & Architecture
  ├─ Code: Project structure
  └─ Tutorial: Create first project
  ↓
Lesson 4: Models & ORM
  ├─ Theory: Database design
  ├─ Code: Model patterns
  └─ Tutorial: 12 QuerySet exercises
  ↓
Lesson 5: CRUD Views
  ├─ Theory: Views & URLs
  ├─ Code: 9 CRUD views
  └─ Tutorial: Full web app
  ↓
Lesson 6: Forms & Templates
  ├─ Theory: Forms & Bootstrap
  ├─ Code: Forms & templates
  └─ Tutorial: Advanced UI
  ↓
Beginner Edition Complete!
  ↓
Optional: Advanced Edition
  ├─ Scrapy framework
  ├─ Celery task queue
  ├─ REST API with Django REST Framework
  └─ Production deployment
```

---

## File Size Summary

| Component | Files | Total |
|-----------|-------|-------|
| Theory | 6 files | 88 KB |
| Code | 6 files | 94 KB |
| Tutorials | 6 files | 88 KB |
| **Total** | **18 files** | **270 KB** |

---

## How to Navigate

### By Lesson Number
- Lesson 1: Start with theory/01_*
- Lesson 2: theory/02_*, code/02_*, tutorials/02_*
- etc.

### By File Type
- All theory: Look in `theory/` folder
- All code: Look in `code/` folder
- All tutorials: Look in `tutorials/` folder

### By Topic
- Web scraping: Lessons 1-2
- Django introduction: Lesson 3
- Database design: Lesson 4
- Web development: Lessons 5-6

---

## Linking Between Files

Within lesson files:
- Theory → Code: "See code/01_beautiful_soup_practice.py"
- Code → Tutorial: "Follow tutorials/01_scraping_tutorial.md"
- Tutorial → Theory: "Read theory/01_beautiful_soup_concepts.md"

Between lessons:
- End of Lesson 1 → Start of Lesson 2
- End of Lesson 2 → Start of Lesson 3
- etc.

---

## Quick Reference

**Need to find something?**

- **Web scraping**: theory/01_*, code/01_*
- **Django setup**: theory/03_*, tutorials/03_*
- **Database queries**: theory/04_*, code/04_*
- **Web views**: theory/05_*, code/05_*
- **Forms validation**: code/06_*, tutorials/06_*
- **Templates syntax**: theory/06_*, code/06_*

---

**[← Back to README](README.md)** | **[Next: Getting Started →](GETTING_STARTED.md)**
