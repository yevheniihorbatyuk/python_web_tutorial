# Django App Setup Guide

Complete instructions for setting up and running the Module 10 Django application.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 15+ (if using PostgreSQL locally)
- Git

## Option 1: Local Development (SQLite)

### Step 1: Clone and navigate to project

```bash
cd /root/goit/python_web/module_10/03_django_app
```

### Step 2: Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

### Step 4: Create .env file (optional - uses SQLite by default)

```bash
cp .env.example .env
```

For SQLite (already default):
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Step 5: Initialize database

```bash
python manage.py migrate
```

### Step 6: Create superuser (admin account)

```bash
python manage.py createsuperuser
```

Enter when prompted:
- Username: `admin`
- Email: `admin@example.com`
- Password: (your choice)

### Step 7: Create sample data (optional)

```bash
python manage.py shell
```

Then in the shell:

```python
from users.models import Country, City, User

# Create countries
ukraine = Country.objects.create(name='Ukraine', code='UA', population=41000000)
poland = Country.objects.create(name='Poland', code='PL', population=38000000)

# Create cities
kyiv = City.objects.create(
    name='Kyiv',
    country=ukraine,
    population=2900000,
    founded_year=1200,
    is_capital=True
)
lviv = City.objects.create(
    name='Lviv',
    country=ukraine,
    population=717000,
    founded_year=1256
)

# Create users
User.objects.create(
    first_name='John',
    last_name='Doe',
    email='john@example.com',
    phone='+380123456789',
    city=kyiv,
    bio='A sample user from Kyiv'
)

print("Sample data created!")
exit()
```

### Step 8: Run development server

```bash
python manage.py runserver
```

**Access the application:**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- Users: http://localhost:8000/users/
- Countries: http://localhost:8000/users/countries/
- Cities: http://localhost:8000/users/cities/

---

## Option 2: Local Development (PostgreSQL)

### Step 1-3: Same as SQLite option above

```bash
cd /root/goit/python_web/module_10/03_django_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r ../requirements.txt
```

### Step 4: Create .env file with PostgreSQL configuration

```bash
cp .env.example .env
```

Edit `.env` to use PostgreSQL:

```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=goit_module10
DB_USER=goit
DB_PASSWORD=goit_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 5: Install PostgreSQL (if not already installed)

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Step 6: Create database and user

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql shell:
CREATE USER goit WITH PASSWORD 'goit_password';
CREATE DATABASE goit_module10 OWNER goit;
ALTER ROLE goit SET client_encoding TO 'utf8';
ALTER ROLE goit SET default_transaction_isolation TO 'read committed';
ALTER ROLE goit SET default_transaction_deferrable TO on;
ALTER ROLE goit SET default_timezone TO 'UTC';

# Exit psql
\q
```

### Step 7: Run migrations

```bash
python manage.py migrate
```

### Step 8: Create superuser

```bash
python manage.py createsuperuser
```

### Step 9: Run server

```bash
python manage.py runserver
```

---

## Option 3: Docker Compose (Recommended for Production-like setup)

### Step 1: Navigate to module_10 directory

```bash
cd /root/goit/python_web/module_10
```

### Step 2: Create .env file for Docker

```bash
cp 03_django_app/.env.example .env
```

The `.env` should contain (already in docker-compose.yml as environment):
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
POSTGRES_USER=goit
POSTGRES_PASSWORD=goit_password
POSTGRES_DB=goit_module10
```

### Step 3: Build and start containers

```bash
docker-compose up -d
```

This starts:
- **postgres** service (PostgreSQL database on port 5432)
- **redis** service (Redis cache on port 6379)
- **app** service (Django app on port 8000)

### Step 4: Run migrations in container

```bash
docker-compose exec app python manage.py migrate
```

### Step 5: Create superuser

```bash
docker-compose exec app python manage.py createsuperuser
```

### Step 6: Create sample data (optional)

```bash
docker-compose exec app python manage.py shell < create_sample_data.py
```

Or manually:
```bash
docker-compose exec app python manage.py shell
```

### Step 7: Access the application

- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- PostgreSQL: localhost:5432 (credentials: goit/goit_password)
- Redis: localhost:6379

### Step 8: View logs

```bash
docker-compose logs -f app
```

### Step 9: Stop containers

```bash
docker-compose down
```

### Step 10: Remove data (careful!)

```bash
docker-compose down -v  # -v removes volumes (database data)
```

---

## Running Tests

### Unit Tests

```bash
# Run all tests
python manage.py test

# Run tests with verbose output
python manage.py test users --verbosity=2

# Run specific test class
python manage.py test users.tests.UserModelTests

# Run specific test method
python manage.py test users.tests.UserModelTests.test_user_creation
```

### Test Coverage (with Docker)

```bash
docker-compose exec app python manage.py test users --verbosity=2
```

---

## Development Commands

### Interactive Shell

```bash
python manage.py shell
```

### Create migrations

```bash
python manage.py makemigrations
```

### Apply migrations

```bash
python manage.py migrate
```

### Check for issues

```bash
python manage.py check
```

### Create superuser

```bash
python manage.py createsuperuser
```

### Collect static files (production)

```bash
python manage.py collectstatic --noinput
```

---

## Project Structure

```
03_django_app/
├── config/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI server
│   └── asgi.py              # ASGI server
├── users/
│   ├── models.py            # Data models: Country, City, User
│   ├── views.py             # CRUD views
│   ├── forms.py             # Model forms with validation
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Django admin configuration
│   ├── tests.py             # Unit tests
│   └── templates/users/     # HTML templates
├── templates/
│   ├── base.html            # Base template with Bootstrap
│   └── home.html            # Home page
├── static/
│   ├── css/style.css
│   └── js/main.js
├── manage.py                # Django management script
└── README.md                # Application documentation
```

---

## URL Routes

### Users
- `GET /users/` - List all users
- `GET /users/<id>/` - View user details
- `POST /users/create/` - Create new user
- `POST /users/<id>/edit/` - Edit user
- `POST /users/<id>/delete/` - Delete user

### Cities
- `GET /users/cities/` - List all cities
- `GET /users/cities/<id>/` - View city details
- `POST /users/cities/create/` - Create new city
- `POST /users/cities/<id>/edit/` - Edit city
- `POST /users/cities/<id>/delete/` - Delete city

### Countries
- `GET /users/countries/` - List all countries
- `GET /users/countries/<id>/` - View country details
- `POST /users/countries/create/` - Create new country
- `POST /users/countries/<id>/edit/` - Edit country
- `POST /users/countries/<id>/delete/` - Delete country

### Admin
- `GET /admin/` - Django admin panel
- `GET /admin/users/` - Manage users
- `GET /admin/users/country/` - Manage countries
- `GET /admin/users/city/` - Manage cities

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Make sure you're in the correct virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r ../requirements.txt
```

### Issue: "Database does not exist"

**Solution:**
```bash
# For SQLite, just run migrations
python manage.py migrate

# For PostgreSQL, create the database first
psql -U postgres -c "CREATE DATABASE goit_module10;"
python manage.py migrate
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Issue: "No such table" error

**Solution:**
```bash
python manage.py migrate
```

### Issue: Docker container won't start

**Solution:**
```bash
# Check logs
docker-compose logs app

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 worker processes)
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

### Using Docker (Recommended)

Update `Dockerfile` to use Gunicorn:

```dockerfile
CMD ["gunicorn", "config.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8000"]
```

Then rebuild and run:
```bash
docker-compose build
docker-compose up -d
```

### Production Settings Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set a secure `SECRET_KEY` in .env
- [ ] Whitelist allowed hosts in `.env` ALLOWED_HOSTS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Use Gunicorn or similar production server
- [ ] Set up HTTPS/SSL
- [ ] Configure static file serving (nginx recommended)
- [ ] Set up error logging and monitoring
- [ ] Run `python manage.py check --deploy`

---

## Database Schema

### Country Model
```
- id (PK)
- name (CharField, unique)
- code (CharField, unique, 2 chars ISO code)
- population (BigIntegerField, nullable)
- created_at (DateTimeField, auto)
- updated_at (DateTimeField, auto)
```

### City Model
```
- id (PK)
- name (CharField)
- country (FK → Country)
- population (IntegerField, nullable)
- founded_year (IntegerField, nullable, 1-current_year)
- is_capital (BooleanField)
- created_at (DateTimeField, auto)
- updated_at (DateTimeField, auto)
```

### User Model
```
- id (PK)
- first_name (CharField)
- last_name (CharField)
- email (EmailField, unique)
- phone (CharField, nullable)
- city (FK → City, nullable)
- bio (TextField, nullable)
- is_active (BooleanField)
- created_at (DateTimeField, auto)
- updated_at (DateTimeField, auto)
```

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Models](https://docs.djangoproject.com/en/5.0/topics/db/models/)
- [Django Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/)
- [Django Forms](https://docs.djangoproject.com/en/5.0/topics/forms/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Last Updated**: December 20, 2024
**Version**: 1.0
