# Event Hub - Setup & Development Guide

Complete instructions for setting up the Event Hub Django application.

---

## 🚀 Quick Start (Choose One)

### Option 1: Local Development (SQLite) - 5 minutes

Best for: Learning, quick testing, no database setup

```bash
# Navigate to project
cd 04_event_hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env to use SQLite (uncomment SQLite lines):
# DATABASE_ENGINE=django.db.backends.sqlite3
# DATABASE_NAME=db.sqlite3

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Enter: username, email, password

# Run development server
python manage.py runserver
```

**Access:**
- App: http://localhost:8000
- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/

**Note**: Without Celery tasks won't run (notifications won't be sent)

---

### Option 2: Docker (PostgreSQL + Redis + Celery) - 10 minutes

Best for: Full featured setup, production-like environment

```bash
# Navigate to project
cd 04_event_hub

# Create .env from template
cp .env.example .env
# Keep PostgreSQL settings (already configured)

# Build and start all services
docker-compose up -d

# Watch logs
docker-compose logs -f app

# In another terminal, run migrations
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser

# Check Celery worker
docker-compose logs -f celery
```

**Access:**
- App: http://localhost:8000
- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/
- PostgreSQL: localhost:5432 (eventhub/eventhub_pass)
- Redis: localhost:6379

**Services Running:**
- Django app (port 8000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery worker
- Celery beat (scheduler)

**Useful Commands:**
```bash
# View logs
docker-compose logs -f app
docker-compose logs -f celery
docker-compose logs -f postgres

# Stop containers
docker-compose down

# Remove everything (careful!)
docker-compose down -v

# Restart a service
docker-compose restart app

# Run commands in container
docker-compose exec app python manage.py shell
docker-compose exec app python manage.py test
```

---

## 📋 Project Setup Checklist

After choosing your setup option above:

### 1. ✅ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. ✅ Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (usually no changes needed for dev)
```

### 3. ✅ Create Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. ✅ Create Admin User
```bash
python manage.py createsuperuser
```

### 5. ✅ Run Development Server
```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: Celery worker (if using local Celery)
celery -A eventhub_config worker --loglevel=info

# Terminal 3: Celery beat (if using local scheduling)
celery -A eventhub_config beat --loglevel=info
```

---

## 🏗️ Initialize Django Project Structure

The following has already been prepared, but if you're starting fresh:

```bash
# Create Django project
django-admin startproject eventhub_config .

# Create apps
python manage.py startapp events
python manage.py startapp bookings
python manage.py startapp payments
python manage.py startapp users
python manage.py startapp notifications
```

---

## 📝 Create .env File

```bash
cp .env.example .env
```

**For SQLite (development):**
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

**For PostgreSQL (production-like):**
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=eventhub
DATABASE_USER=eventhub
DATABASE_PASSWORD=eventhub_pass
DATABASE_HOST=localhost
DATABASE_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

---

## 🎯 Development Tasks

### Task 1: Create Models

Location: `apps/*/models.py`

**Events App** (apps/events/models.py):
```python
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_capacity = models.IntegerField()
    current_attendees = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[...])
    created_at = models.DateTimeField(auto_now_add=True)
```

Similar for: Booking, Payment, User, Waitlist, Review, Certificate

See EVENT_HUB_PLAN.md for full model specifications.

### Task 2: Create Serializers

Location: `apps/*/serializers.py`

DRF serializers for API request/response validation.

### Task 3: Create ViewSets

Location: `apps/*/views.py`

Use DRF ViewSets for REST endpoints.

### Task 4: Configure API URLs

Location: `eventhub_config/urls.py`

Use DRF routers for automatic URL generation.

### Task 5: Add Tests

Location: `apps/*/tests.py`

Unit tests for models, serializers, and views.

### Task 6: Configure Celery

Location: `eventhub_config/celery.py`

Setup Celery for async tasks.

---

## 🧪 Testing

### Run all tests
```bash
python manage.py test
# or
pytest
```

### Run specific app tests
```bash
python manage.py test apps.events
```

### With coverage
```bash
pytest --cov=apps --cov-report=html
```

### Watch mode (auto-rerun on changes)
```bash
pytest-watch
```

---

## 📱 API Testing

### Using curl

```bash
# List events
curl http://localhost:8000/api/events/

# Create event (requires auth)
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Event","price":"99.99",...}'

# Create booking
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer {token}" \
  -d '{"event":1,"quantity":2}'
```

### Using Postman

1. Import API collection (will be provided)
2. Set up authentication
3. Test endpoints

### Using Python requests

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', {
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access']

# Get events
headers = {'Authorization': f'Bearer {token}'}
events = requests.get('http://localhost:8000/api/events/', headers=headers)
print(events.json())
```

---

## 🔧 Django Admin Panel

Access: http://localhost:8000/admin/

**Customize admin:**

```python
# apps/events/admin.py
from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_date', 'status')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'
```

---

## 🔄 Celery Tasks

### Test tasks locally

```bash
# Terminal 1: Django shell
python manage.py shell

# Terminal 2: Celery worker
celery -A eventhub_config worker --loglevel=info
```

In Django shell:
```python
from apps.notifications.tasks import send_booking_confirmation

# Test task
result = send_booking_confirmation.delay(booking_id=1)
print(result.get())  # Wait for result
```

### Monitor tasks

```bash
# Install Flower (Celery monitoring)
pip install flower

# Run Flower
celery -A eventhub_config worker --loglevel=info
# In another terminal:
celery -A eventhub_config events
# Visit: http://localhost:5555
```

---

## 🐛 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'django'"
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "relation 'events_event' does not exist"
```bash
# Run migrations
python manage.py migrate
```

### "ConnectionRefusedError: [Errno 111] Connection refused" (Redis)
```bash
# Install Redis (if not using Docker)
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
# Windows: Download from https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server
```

### Celery tasks not running
```bash
# Make sure Celery worker is running
celery -A eventhub_config worker --loglevel=debug

# Check for errors
docker-compose logs celery  # if using Docker
```

### "CSRF token missing"
- API requests need headers: `'Content-Type': 'application/json'`
- For form data: need CSRF token

### Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001

# Or find & kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Django Shell

Access database interactively:

```bash
python manage.py shell
```

Example:
```python
from apps.events.models import Event
from apps.users.models import User

# Create event
user = User.objects.first()
event = Event.objects.create(
    title='Python Workshop',
    description='Learn Django',
    organizer=user,
    price=99.99,
    max_capacity=30
)

# Query events
events = Event.objects.filter(status='published')
print(events.count())

# Update
event.price = 79.99
event.save()

# Delete
event.delete()
```

---

## 🚀 Development Workflow

### 1. Start Services
```bash
# Option A: Local
python manage.py runserver &
celery -A eventhub_config worker --loglevel=info

# Option B: Docker
docker-compose up -d
```

### 2. Make Changes
- Edit models, views, serializers
- Write tests
- Test in shell or with requests

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Test
```bash
pytest
# or
python manage.py test
```

### 5. Commit
```bash
git add .
git commit -m "Add feature"
```

---

## 📊 Project Statistics

Expected after complete implementation:
- **7-8 models** with relationships
- **30+ API endpoints**
- **100+ unit tests**
- **3000+ lines of code**
- **Full test coverage** (80%+)

---

## ✅ Implementation Checklist

- [ ] Project initialized
- [ ] Models created (Event, Booking, Payment, etc.)
- [ ] Migrations created and applied
- [ ] API serializers created
- [ ] ViewSets implemented
- [ ] URL routing configured
- [ ] Authentication (JWT) setup
- [ ] RBAC permissions configured
- [ ] Mock payment system implemented
- [ ] Celery tasks created
- [ ] Email templates created
- [ ] Tests written (50+ tests)
- [ ] Docker setup verified
- [ ] Documentation complete
- [ ] Production ready

---

## 🎓 Learning Resources

- [Django Official Docs](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)

---

## 📞 Getting Help

1. Check EVENT_HUB_PLAN.md for implementation details
2. Review example code in each app
3. Check test files for usage examples
4. Read Django/DRF documentation
5. Use Django shell for experimentation

---

**Last Updated**: December 20, 2025
**Status**: Ready for Development
**Next**: Begin with Task 1 - Create Models
