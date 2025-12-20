# Module 10 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install & Setup

```bash
cd /root/goit/python_web/module_10

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Services (Optional - Docker)

```bash
docker-compose up -d
# Creates: PostgreSQL, Redis, pgAdmin
```

### Step 3: Run Beginner Lessons

```bash
# Lesson 1: BeautifulSoup
python beginner_edition/01_beautifulsoup_basics.py

# Lesson 2: News Scraper
python beginner_edition/02_scrape_news_portal.py

# Lesson 3-6: View guides
python beginner_edition/03_django_setup.py
python beginner_edition/04_django_models.py
python beginner_edition/05_django_crud.py
python beginner_edition/06_django_forms.py
```

### Step 4: Run Django App

```bash
cd django_app

# Create database
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter: username, email, password

# Start server
python manage.py runserver
```

### Step 5: Access Application

- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Users**: http://localhost:8000/users/
- **Cities**: http://localhost:8000/users/cities/
- **Countries**: http://localhost:8000/users/countries/

## 📚 Learning Path

1. **Lesson 1** (45 min): BeautifulSoup basics - Parse HTML
2. **Lesson 2** (60 min): Complete scraper - Full pipeline
3. **Lesson 3** (90 min): Django setup - Architecture
4. **Lesson 4** (90 min): Models - Database design
5. **Lesson 5** (75 min): CRUD views - Operations
6. **Lesson 6** (75 min): Forms & templates - UI

**Total**: 6-8 hours

## 🛠️ Common Tasks

### Create Users in Admin

```
1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Add Country (e.g., "Ukraine", code "UA")
4. Add City (e.g., "Kyiv", select country)
5. Add Users (select city)
```

### Query Database (Shell)

```bash
python django_app/manage.py shell

# In shell:
from users.models import User, City, Country

# Get all
User.objects.all()

# Filter
users = User.objects.filter(city__country__name="Ukraine")

# Count
User.objects.count()

# Exit
exit()
```

### Run Migrations

```bash
cd django_app

# After modifying models.py
python manage.py makemigrations

# Apply to database
python manage.py migrate
```

## 📖 File Structure

```
module_10/
├── beginner_edition/          # 6 lessons (2,200+ lines)
│   ├── 01_beautifulsoup_basics.py
│   ├── 02_scrape_news_portal.py
│   ├── 03_django_setup.py
│   ├── 04_django_models.py
│   ├── 05_django_crud.py
│   ├── 06_django_forms.py
│   └── README_beginner.md
│
├── django_app/                # Complete Django app
│   ├── manage.py
│   ├── config/               # Settings, URLs
│   ├── users/                # Models, views, forms
│   ├── templates/            # HTML files (16+)
│   └── static/               # CSS, JS
│
├── requirements.txt           # Dependencies
├── docker-compose.yml         # Services
├── .env.example              # Configuration
├── README.md                 # Main guide
├── PLAN.md                   # Implementation plan
└── QUICKSTART.md             # This file
```

## 🎯 What You'll Learn

### Web Scraping (Lessons 1-2)
- HTTP requests and HTML parsing
- CSS selectors
- Data extraction and validation
- Error handling and retries
- Database persistence

### Django (Lessons 3-6)
- MVT architecture
- Models with relationships
- CRUD operations
- Forms and validation
- Templates and inheritance
- Bootstrap integration

## 💡 Key Concepts

### Models
```python
Country (1) → City (N) → User (N)
```

### Views
```
UserListView → Filter, search, paginate
UserDetailView → Display single user
UserCreateView → Add with validation
UserUpdateView → Edit existing
UserDeleteView → Remove with confirmation
```

### Forms
```
UserForm(ModelForm) → Auto-created from model
UserSearchForm → Regular form for filtering
```

### Templates
```
base.html → Bootstrap base
user_list.html → List with pagination
user_detail.html → Profile
user_form.html → Create/edit
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError: django | `pip install -r requirements.txt` |
| Table doesn't exist | `python manage.py migrate` |
| Port 8000 in use | `python manage.py runserver 8001` |
| Static files not loading | `python manage.py collectstatic` |
| Can't connect to DB | Check .env, start PostgreSQL |

## 📚 Documentation

- **Beginner README**: Detailed learning guide with exercises
- **PLAN.md**: High-level implementation plan
- **Main README.md**: Overview and troubleshooting
- **Lesson files**: In-code documentation with examples

## 🚀 What's Next?

1. **Complete lessons 1-6**
2. **Do the exercises** (4 levels in Beginner README)
3. **Run Django app locally**
4. **Build your own project**
5. **Deploy with Docker**
6. **Start Advanced Edition** (Scrapy, Celery, APIs)

## 📞 Need Help?

1. Check lesson documentation (in-code comments)
2. Read Beginner README for explanations
3. Search official docs (Django, BeautifulSoup)
4. Review code examples in lesson files

---

**You're ready to start!** Open `beginner_edition/01_beautifulsoup_basics.py` and begin learning. 🎓

Estimated time to complete Beginner Edition: **6-8 hours**
