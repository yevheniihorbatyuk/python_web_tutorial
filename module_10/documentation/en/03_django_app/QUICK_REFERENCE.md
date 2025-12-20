# Quick Reference Guide

## 📍 Location
```
/root/goit/python_web/module_10/03_django_app
```

## 🚀 Start Development (30 seconds)

```bash
cd /root/goit/python_web/module_10/03_django_app
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

**Then visit**: http://localhost:8000

## 🐳 Start with Docker (1 minute)

```bash
cd /root/goit/python_web/module_10
docker-compose up -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
```

**Then visit**: http://localhost:8000

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| [README.md](03_django_app/README.md) | Overview & quick start |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Complete setup instructions |
| [DJANGO_APP_VERIFICATION.md](DJANGO_APP_VERIFICATION.md) | Verification checklist |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was completed |

## 🧪 Run Tests

```bash
cd /root/goit/python_web/module_10/03_django_app

# All tests
python manage.py test users

# Verbose output
python manage.py test users --verbosity=2

# Specific test
python manage.py test users.tests.UserModelTests.test_user_creation
```

## 📋 Common Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Interactive shell
python manage.py shell

# Check for issues
python manage.py check

# Run development server on different port
python manage.py runserver 8001
```

## 🔗 URLs

| URL | Purpose |
|-----|---------|
| `/` | Home page |
| `/admin/` | Django admin |
| `/users/` | Users list |
| `/users/create/` | Create user |
| `/users/<id>/` | User detail |
| `/users/<id>/edit/` | Edit user |
| `/users/<id>/delete/` | Delete user |
| `/users/cities/` | Cities list |
| `/users/countries/` | Countries list |

## 🗄️ Database

### Default (SQLite)
- File: `db.sqlite3`
- No setup required
- Good for development

### Production (PostgreSQL)
- User: `goit`
- Password: `goit_password`
- Database: `goit_module10`
- Host: `localhost`
- Port: `5432`

## 📁 Project Structure

```
03_django_app/
├── manage.py
├── config/
│   ├── settings.py      # ← .env support added
│   └── urls.py
├── users/
│   ├── models.py        # Country, City, User
│   ├── views.py         # CRUD views
│   ├── forms.py         # Form validation
│   ├── urls.py          # URL patterns
│   ├── tests.py         # 44 unit tests ✅
│   └── templates/
└── templates/
    ├── base.html
    └── home.html
```

## ✅ Features

### Models (3)
- Country (name, code, population)
- City (name, country, population, is_capital)
- User (first_name, last_name, email, phone, city, bio)

### Views (15)
- 5 Country views (list, detail, create, edit, delete)
- 5 City views (list, detail, create, edit, delete)
- 5 User views (list, detail, create, edit, delete)

### Forms (4)
- CountryForm - with code validation
- CityForm - with duplicate prevention
- UserForm - with email uniqueness
- UserSearchForm - with filtering and sorting

### Tests (44)
- 7 Country tests
- 6 City tests
- 9 User tests
- 5 CountryForm tests
- 4 CityForm tests
- 7 UserForm tests
- 3 UserSearchForm tests
- 3 View tests

## 🔧 Configuration

Create `.env` file in `03_django_app/`:

**For SQLite (development):**
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

**For PostgreSQL (production):**
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=goit_module10
DB_USER=goit
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'django'"**
```bash
source venv/bin/activate
pip install -r ../requirements.txt
```

**"Database does not exist"**
```bash
python manage.py migrate
```

**"Port 8000 already in use"**
```bash
python manage.py runserver 8001
```

**Docker container won't start**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Statistics

- **Code Files**: 8 main files
- **Lines of Code**: ~1,200+ lines
- **Models**: 3 models
- **Views**: 15 class-based views
- **Forms**: 4 forms with validation
- **Tests**: 44 comprehensive tests
- **Templates**: 12 HTML templates
- **Documentation**: 4 guides

## 🎯 Next Steps

1. **Explore the code**
   - Read models in `users/models.py`
   - Check views in `users/views.py`
   - Review forms in `users/forms.py`

2. **Run the app**
   - Follow setup instructions above
   - Create sample data via Django shell
   - Test features in web interface

3. **Run tests**
   - `python manage.py test users --verbosity=2`
   - All 44 tests should pass

4. **Enhance further** (optional)
   - Add REST API with Django REST Framework
   - Add user authentication
   - Add background tasks with Celery
   - Add caching with Redis

## 📞 Files at a Glance

| File | Lines | Purpose |
|------|-------|---------|
| models.py | 215 | Data models |
| views.py | 350+ | CRUD operations |
| forms.py | 313 | Form validation |
| tests.py | 538 | Unit tests |
| settings.py | 150+ | Configuration |
| README.md | 128 | Documentation |
| SETUP_GUIDE.md | 500+ | Setup instructions |

## 🔒 Security Features

✅ Environment-based configuration  
✅ CSRF protection  
✅ SQL injection prevention (ORM)  
✅ XSS prevention (auto-escaping)  
✅ Secure password handling  
✅ Input validation on all forms  

## ⚡ Performance Features

✅ Database indexes on key fields  
✅ Query optimization with annotations  
✅ Pagination for large datasets  
✅ Form validation (client + server)  
✅ Optional Redis caching configured  

## 📦 Dependencies

```
Django==5.0.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pytest==7.4.3
pytest-django==4.7.0
+ 5 more packages
```

See `requirements.txt` for full list.

---

**Last Updated**: December 20, 2024  
**Status**: ✅ Production Ready
