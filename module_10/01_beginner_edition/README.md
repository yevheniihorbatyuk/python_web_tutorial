# Beginner Edition: Complete Course

**Learn Web Development with Python & Django**

Complete, production-quality educational material for learning:
- Web scraping with Beautiful Soup
- Real-world data processing
- Django web development
- Database modeling
- CRUD operations
- Forms and templates

---

## 📚 Course Structure

### Three Learning Methods

**Choose Your Path:**

1. **Theory-First Learner**: Read theory → Study code → Do tutorials
2. **Code-First Learner**: Study code → Read theory → Do tutorials
3. **Hands-On Learner**: Do tutorials → Reference theory & code as needed

---

## 🎓 6 Complete Lessons

### Lesson 1: Beautiful Soup Web Scraping
**Learn to extract data from websites**

- **Theory**: [theory/01_beautiful_soup_concepts.md](theory/01_beautiful_soup_concepts.md) (1.1 MB)
  - HTML structure fundamentals
  - CSS selectors
  - Parsing with Beautiful Soup
  - Data extraction patterns
  - Error handling

- **Code**: [code/01_beautiful_soup_practice.py](code/01_beautiful_soup_practice.py) (11 KB)
  - Working QuoteScraper class
  - Fetch, parse, extract workflow
  - Data validation functions
  - JSON export

- **Tutorial**: [tutorials/01_scraping_tutorial.md](tutorials/01_scraping_tutorial.md) (6.6 KB)
  - Step-by-step walkthrough
  - Expected outputs at each step
  - 8 progressive exercises
  - Testing and validation

**Topics**: HTTP requests, HTML parsing, CSS selectors, error handling, data storage

**Time**: 2-3 hours

---

### Lesson 2: Real-World News Scraping Project
**Build a complete scraping application**

- **Theory**: [theory/02_real_world_scraping.md](theory/02_real_world_scraping.md) (6.3 KB)
  - Complete workflow: Fetch → Parse → Extract → Validate → Store
  - Retry logic and exponential backoff
  - Data validation best practices
  - Production patterns

- **Code**: [code/02_real_world_scraping.py](code/02_real_world_scraping.py) (14 KB)
  - `NewsArticle` dataclass with validation
  - `NewsPortalScraper` with retry logic
  - `NewsDataValidator` for data cleaning
  - `NewsDatabase` for SQLite persistence
  - Complete end-to-end workflow

- **Tutorial**: [tutorials/02_scraping_project_tutorial.md](tutorials/02_scraping_project_tutorial.md) (8.4 KB)
  - Project setup
  - Running complete workflow
  - Understanding each component
  - Customization for real websites
  - Scheduling scraper runs

**Topics**: Retry logic, data validation, database persistence, logging, error handling

**Time**: 3-4 hours

---

### Lesson 3: Django Project Setup
**Create your first Django project**

- **Theory**: [theory/03_django_fundamentals.md](theory/03_django_fundamentals.md) (13 KB)
  - MVT (Model-View-Template) architecture
  - Project vs App structure
  - Settings configuration
  - Database and migrations
  - Admin interface

- **Code**: [code/03_django_setup_guide.py](code/03_django_setup_guide.py) (16 KB)
  - Django project structure reference
  - Settings template
  - Database setup instructions
  - Migrations workflow
  - Management commands reference

- **Tutorial**: [tutorials/03_django_setup_tutorial.md](tutorials/03_django_setup_tutorial.md) (8.2 KB)
  - Install Django step-by-step
  - Create project and app
  - Configure settings
  - Define models
  - Create migrations
  - Set up Django admin
  - Test with Django shell

**Topics**: Project structure, settings, models, migrations, admin interface

**Time**: 2-3 hours

---

### Lesson 4: Django Models & ORM
**Master database design and queries**

- **Theory**: [theory/04_django_models_orm.md](theory/04_django_models_orm.md) (15 KB)
  - Field types (CharField, IntegerField, DateTimeField, etc.)
  - Field options (null, blank, unique, default)
  - Relationships (ForeignKey, OneToOne, ManyToMany)
  - QuerySet operations
  - Field lookups and filters
  - Aggregation and annotation

- **Code**: [code/04_django_models.py](code/04_django_models.py) (15 KB)
  - Complete model definitions (Country, City, User)
  - QuerySet examples with all operations
  - Field types reference
  - Relationship patterns
  - Migrations workflow
  - Performance optimization (select_related)

- **Tutorial**: [tutorials/04_django_models_tutorial.md](tutorials/04_django_models_tutorial.md) (9.8 KB)
  - Field types in practice
  - One-to-many relationships
  - QuerySet operations
  - Field lookups and joins
  - Aggregation examples
  - CRUD operations
  - Pagination

**Topics**: Models, fields, relationships, QuerySets, migrations, performance

**Time**: 3-4 hours

---

### Lesson 5: Django CRUD Views
**Build complete web interfaces**

- **Theory**: [theory/05_django_views_urls.md](theory/05_django_views_urls.md) (13 KB)
  - Function-Based Views (FBV)
  - Class-Based Views (CBV)
  - Generic views for CRUD
  - URL routing and path converters
  - Request and response objects
  - Pagination and filtering

- **Code**: [code/05_django_crud_views.py](code/05_django_crud_views.py) (16 KB)
  - Complete URLs configuration
  - 9 CRUD views for 3 models
  - Filtering and search implementation
  - Pagination setup
  - Custom success messages
  - FBV alternative examples

- **Tutorial**: [tutorials/05_django_crud_tutorial.md](tutorials/05_django_crud_tutorial.md) (19 KB)
  - Create forms
  - Implement CRUD views
  - Set up URL routing
  - Create base template
  - Build list, detail, form, delete templates
  - Add Bootstrap styling
  - Test full application

**Topics**: Views, URLs, CRUD operations, filtering, pagination, templates

**Time**: 4-5 hours

---

### Lesson 6: Django Forms & Templates
**Polish your user interface**

- **Theory**: [theory/06_django_forms_templates.md](theory/06_django_forms_templates.md) (14 KB)
  - Django Forms vs ModelForms
  - Form fields and validation
  - Template syntax (tags, filters, inheritance)
  - CSRF protection
  - Bootstrap integration
  - Static files management

- **Code**: [code/06_django_forms.py](code/06_django_forms.py) (22 KB)
  - ModelForm definitions with validation
  - Field-level and form-level validation
  - Bootstrap widget integration
  - Base template example
  - User list template with search/pagination
  - User form template with error display
  - Delete confirmation template
  - Template syntax reference

- **Tutorial**: [tutorials/06_django_forms_templates_tutorial.md](tutorials/06_django_forms_templates_tutorial.md) (21 KB)
  - Advanced form validation
  - Test form validation
  - Create advanced templates
  - Form template with error handling
  - List template with filters and pagination
  - Detail template
  - Delete confirmation
  - Add custom CSS
  - Success messages
  - Production checklist

**Topics**: Forms, validation, templates, Bootstrap, CSRF protection, static files

**Time**: 4-5 hours

---

## 📊 Complete Metrics

| Component | Count | Total Size |
|-----------|-------|-----------|
| **Theory Files** | 6 | 88 KB |
| **Code Files** | 6 | 94 KB |
| **Tutorials** | 6 | 88 KB |
| **Total** | 18 | **270 KB** |

---

## 🚀 Getting Started

### Option 1: Start Fresh

1. **Install Python 3.10+**
   ```bash
   python --version
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install requests beautifulsoup4 django psycopg2-binary python-dotenv
   ```

4. **Start with Lesson 1**
   - Read: [theory/01_beautiful_soup_concepts.md](theory/01_beautiful_soup_concepts.md)
   - Study: [code/01_beautiful_soup_practice.py](code/01_beautiful_soup_practice.py)
   - Practice: [tutorials/01_scraping_tutorial.md](tutorials/01_scraping_tutorial.md)

### Option 2: Use Existing Code

1. Copy code files to your project
   ```bash
   cp code/*.py your_project/
   ```

2. Run examples
   ```bash
   python code/01_beautiful_soup_practice.py quotes
   python code/02_real_world_scraping.py
   ```

3. Reference theory as needed
   ```bash
   cat theory/01_beautiful_soup_concepts.md
   ```

### Option 3: Jump to Django

Start at Lesson 3 if you already know web scraping:

1. Read: [theory/03_django_fundamentals.md](theory/03_django_fundamentals.md)
2. Follow: [tutorials/03_django_setup_tutorial.md](tutorials/03_django_setup_tutorial.md)

---

## 📖 How to Use This Course

### For Self-Study

1. **Read the theory file** to understand concepts
2. **Study the code file** to see implementations
3. **Follow the tutorial** to practice hands-on
4. **Modify and experiment** with the code
5. **Complete the exercises** in each tutorial
6. **Reference as needed** when building projects

### For Instructors

- Theory files: Clear, comprehensive explanations
- Code files: Production-ready examples
- Tutorials: Step-by-step with expected outputs
- All materials are self-contained and modular

### For Project Reference

- Copy code patterns directly to your projects
- Reference theory for concept clarification
- Use tutorials as troubleshooting guides

---

## ✨ Key Features

### Theory Files
- ✅ Comprehensive concept explanations
- ✅ Diagrams and visual aids
- ✅ Official documentation links
- ✅ Real-world use cases
- ✅ Best practices and patterns

### Code Files
- ✅ Production-ready implementations
- ✅ Full type hints
- ✅ Comprehensive docstrings
- ✅ Error handling
- ✅ Copy-paste ready examples

### Tutorials
- ✅ Step-by-step walkthrough
- ✅ Expected outputs at each step
- ✅ Hands-on exercises
- ✅ Testing examples
- ✅ Troubleshooting guides
- ✅ Next lesson progression

---

## 🎯 Learning Outcomes

After completing this course, you'll be able to:

### Lesson 1-2: Web Scraping
- ✅ Fetch websites with requests
- ✅ Parse HTML with Beautiful Soup
- ✅ Extract data with CSS selectors
- ✅ Validate and clean data
- ✅ Store data in databases
- ✅ Handle errors gracefully
- ✅ Implement retry logic

### Lesson 3: Django Setup
- ✅ Create Django projects and apps
- ✅ Configure Django settings
- ✅ Work with PostgreSQL databases
- ✅ Create and run migrations
- ✅ Use Django admin interface

### Lesson 4: Database Design
- ✅ Design database models
- ✅ Define relationships
- ✅ Write complex QuerySets
- ✅ Optimize database queries
- ✅ Aggregate and analyze data

### Lesson 5: Web Views
- ✅ Create CRUD views
- ✅ Handle URL routing
- ✅ Implement pagination
- ✅ Add searching and filtering
- ✅ Process GET/POST requests

### Lesson 6: Forms & Templates
- ✅ Create validation forms
- ✅ Render templates
- ✅ Implement inheritance
- ✅ Use template tags and filters
- ✅ Secure against CSRF
- ✅ Style with Bootstrap

---

## 📚 File Navigation

```
01_beginner_edition/
├── README.md                      ← You are here
├── theory/
│   ├── 01_beautiful_soup_concepts.md
│   ├── 02_real_world_scraping.md
│   ├── 03_django_fundamentals.md
│   ├── 04_django_models_orm.md
│   ├── 05_django_views_urls.md
│   └── 06_django_forms_templates.md
├── code/
│   ├── 01_beautiful_soup_practice.py
│   ├── 02_real_world_scraping.py
│   ├── 03_django_setup_guide.py
│   ├── 04_django_models.py
│   ├── 05_django_crud_views.py
│   └── 06_django_forms.py
├── tutorials/
│   ├── 01_scraping_tutorial.md
│   ├── 02_scraping_project_tutorial.md
│   ├── 03_django_setup_tutorial.md
│   ├── 04_django_models_tutorial.md
│   ├── 05_django_crud_tutorial.md
│   └── 06_django_forms_templates_tutorial.md
├── GETTING_STARTED.md
└── STRUCTURE.md
```

---

## 🔗 Quick Links

### Start Here
- 📖 [Getting Started Guide](GETTING_STARTED.md)
- 📋 [Course Structure](STRUCTURE.md)

### Lessons
| Lesson | Theory | Code | Tutorial |
|--------|--------|------|----------|
| 1 | [Theory](theory/01_beautiful_soup_concepts.md) | [Code](code/01_beautiful_soup_practice.py) | [Tutorial](tutorials/01_scraping_tutorial.md) |
| 2 | [Theory](theory/02_real_world_scraping.md) | [Code](code/02_real_world_scraping.py) | [Tutorial](tutorials/02_scraping_project_tutorial.md) |
| 3 | [Theory](theory/03_django_fundamentals.md) | [Code](code/03_django_setup_guide.py) | [Tutorial](tutorials/03_django_setup_tutorial.md) |
| 4 | [Theory](theory/04_django_models_orm.md) | [Code](code/04_django_models.py) | [Tutorial](tutorials/04_django_models_tutorial.md) |
| 5 | [Theory](theory/05_django_views_urls.md) | [Code](code/05_django_crud_views.py) | [Tutorial](tutorials/05_django_crud_tutorial.md) |
| 6 | [Theory](theory/06_django_forms_templates.md) | [Code](code/06_django_forms.py) | [Tutorial](tutorials/06_django_forms_templates_tutorial.md) |

---

## 💡 Tips for Success

1. **Don't skip the theory** - Understanding concepts prevents bugs later
2. **Type out the code** - Don't just copy-paste; typing helps learning
3. **Modify examples** - Change values, try different inputs
4. **Break it intentionally** - Understanding errors is part of learning
5. **Read error messages** - They tell you exactly what's wrong
6. **Take notes** - Write down patterns you want to remember
7. **Do the exercises** - Practice solidifies learning
8. **Build projects** - Apply what you've learned to real problems

---

## 🚀 After This Course

### Next Learning Paths

**Continue with Advanced Edition:**
- Web scraping at scale with Scrapy
- Async tasks with Celery
- REST APIs with Django REST Framework
- Production patterns and deployment

**Build Projects:**
- News aggregator
- Product price monitor
- Social media analyzer
- Data dashboard

**Advanced Topics:**
- Testing and TDD
- Performance optimization
- Security hardening
- Containerization with Docker

---

## 📝 License & Attribution

These materials were created for educational purposes.
Free to use, modify, and distribute for learning.

**Feedback Welcome:**
- Found a bug? Report it
- Unclear explanation? Let us know
- Have a suggestion? Share it

---

## ✅ Course Completion Checklist

- [ ] Completed Lesson 1: Beautiful Soup basics
- [ ] Completed Lesson 2: Real-world scraping
- [ ] Completed Lesson 3: Django setup
- [ ] Completed Lesson 4: Models & ORM
- [ ] Completed Lesson 5: CRUD views
- [ ] Completed Lesson 6: Forms & templates
- [ ] Built a small project
- [ ] Reviewed all code examples
- [ ] Ready for Advanced Edition

---

**Ready to start? → [Getting Started Guide](GETTING_STARTED.md)**
