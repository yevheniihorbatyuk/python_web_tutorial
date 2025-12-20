# Event Hub - Django Event Management Platform

A complete event management and ticketing platform built with Django, Django REST Framework, Celery, and PostgreSQL.

**Status**: 🚀 Ready for Development
**Complexity**: Средняя-Высокая
**Time to Complete**: 6-8 hours
**Technologies**: Django 5.0, DRF, Celery, PostgreSQL, Redis, JWT Auth

---

## 🎯 Features

### Core Features
- 📅 **Event Management** - Create, edit, and manage events
- 🎫 **Ticketing System** - Sell and manage event tickets
- 💳 **Mock Payment System** - Process payments (simulated, no real money)
- ⏳ **Waitlist Management** - Queue system when events are full
- ⭐ **Reviews & Ratings** - Attendees can rate and review events
- 📧 **Email Notifications** - Async email sending with Celery
- 👥 **RBAC** - Role-based access control (Attendee, Organizer, Admin)
- 📊 **Organizer Dashboard** - Statistics and analytics for event creators
- 🔐 **JWT Authentication** - Secure API with token-based auth
- 📱 **REST API** - Full REST API for all operations

### Advanced Features
- Celery background tasks for async operations
- Celery Beat for scheduled tasks
- Redis caching and message broker
- Email templates for notifications
- Certificate generation for attendees
- Search and filtering with pagination
- Admin panel customization

---

## 🗂️ Project Structure

```
04_event_hub/
├── eventhub_config/              # Django config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py                 # Celery configuration
│
├── apps/
│   ├── events/                   # Event management
│   │   ├── models.py
│   │   ├── views.py              # EventViewSet
│   │   ├── serializers.py
│   │   ├── filters.py
│   │   └── tests.py
│   │
│   ├── bookings/                 # Booking system
│   │   ├── models.py
│   │   ├── views.py              # BookingViewSet
│   │   ├── serializers.py
│   │   └── tests.py
│   │
│   ├── payments/                 # Payment processing
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── mock.py               # Mock payment service
│   │   └── tests.py
│   │
│   ├── users/                    # User management
│   │   ├── models.py
│   │   ├── views.py              # AuthViewSet, UserViewSet
│   │   ├── serializers.py
│   │   └── tests.py
│   │
│   └── notifications/            # Email notifications
│       ├── models.py
│       ├── tasks.py              # Celery tasks
│       └── templates/            # Email templates
│
├── templates/                    # HTML templates
├── static/                       # Static files
├── manage.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── EVENT_HUB_PLAN.md             # Detailed implementation plan
```

---

## 🚀 Quick Start

### Option 1: Local Development (SQLite)

```bash
# Clone/navigate to project
cd 04_event_hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env to use SQLite
# DATABASE_ENGINE=django.db.backends.sqlite3
# DATABASE_NAME=db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit: http://localhost:8000

### Option 2: Docker (PostgreSQL + Redis + Celery)

```bash
# Create .env file
cp .env.example .env

# Build and start containers
docker-compose up -d

# Run migrations in container
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser

# Monitor Celery worker
docker-compose logs -f celery
```

Visit: http://localhost:8000

---

## 📚 API Endpoints

### Events
```
GET    /api/events/                    # List all events
POST   /api/events/                    # Create event (Organizer)
GET    /api/events/{id}/               # Event details
PUT    /api/events/{id}/               # Update event
DELETE /api/events/{id}/               # Delete event
GET    /api/events/{id}/sessions/      # Event sessions
POST   /api/events/{id}/reviews/       # Post review
GET    /api/events/{id}/reviews/       # Get reviews
```

### Bookings
```
GET    /api/bookings/                  # My bookings
POST   /api/bookings/                  # Create booking
GET    /api/bookings/{id}/             # Booking details
DELETE /api/bookings/{id}/             # Cancel booking
```

### Payments (Mock)
```
POST   /api/payments/                  # Process payment
GET    /api/payments/{id}/             # Payment status
POST   /api/payments/{id}/simulate-webhook/  # Simulate callback
```

### Waitlist
```
GET    /api/events/{id}/waitlist/      # My position
POST   /api/events/{id}/waitlist/      # Join waitlist
```

### Authentication
```
POST   /api/auth/register/             # Register
POST   /api/auth/login/                # Login (returns JWT)
POST   /api/auth/refresh/              # Refresh token
```

### Users
```
GET    /api/users/me/                  # Current user
PUT    /api/users/me/                  # Update profile
GET    /api/users/{id}/                # Public profile
GET    /api/users/{id}/events/         # User's organized events
```

---

## 🔐 Database Models

### Event
- Title, description, category
- Organizer (ForeignKey to User)
- Location, online_meeting_url
- Start/end dates
- Capacity, current attendees
- Price, image
- Status (draft, published, cancelled)

### Booking
- Attendee, event
- Quantity of tickets
- Total price
- Status (pending, confirmed, cancelled)
- Payment link

### Payment (Mock)
- Booking reference
- Amount, method (mock_card, mock_paypal)
- Status (pending, completed, failed)
- Transaction ID

### Waitlist
- Event, user
- Quantity requested
- Queue position
- Notification status

### Review
- Event, author (User)
- Rating (1-5 stars)
- Comment
- Created timestamp

### User (Custom)
- Email, name
- User type (attendee, organizer, admin)
- Profile info
- Joined date

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

### 5. Run Celery (in separate terminal)

```bash
# Worker
celery -A eventhub_config worker --loglevel=info

# Beat (scheduler) - in another terminal
celery -A eventhub_config beat --loglevel=info
```

### 6. Access the Application

- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/ (if configured)

---

## 🧪 Testing

### Run all tests

```bash
python manage.py test

# With verbose output
python manage.py test -v 2

# With coverage
pytest --cov=apps
```

### Run specific test

```bash
python manage.py test apps.events.tests.EventModelTest
```

### Test mock payments

```bash
# Success payment test
POST /api/payments/
{
    "booking_id": 1,
    "card_number": "4111111111111111",
    "amount": 99.99
}

# Failed payment test
{
    "booking_id": 1,
    "card_number": "4000000000000002",
    "amount": 99.99
}
```

---

## 📊 Admin Panel

Features:
- Event management
- Booking overview
- Payment tracking
- User management
- Email template editing
- System statistics

Access: http://localhost:8000/admin/

---

## 🔄 Celery Tasks

Configured tasks:
- `send_booking_confirmation` - Confirmation email after booking
- `send_event_reminder` - 1 day before event
- `send_waitlist_notification` - When space opens
- `send_post_event_survey` - After event feedback
- `process_payment_timeout` - Auto-cancel unpaid bookings

Scheduled:
- Event reminders - Daily at 9 AM
- Payment timeouts - Every 5 minutes
- Surveys - 1 day after event end

---

## 📧 Email Templates

Configured notifications:
- Booking confirmation
- Event reminders (1 day before)
- Waitlist notifications
- Post-event surveys
- Certificate delivery

All sent asynchronously via Celery.

---

## 🔐 Authentication

- JWT-based (JSON Web Tokens)
- Token refresh support
- User roles: Attendee, Organizer, Admin
- Permission-based access control

### Login Flow
1. POST /api/auth/login/ with email/password
2. Receive JWT token
3. Include token in Authorization header: `Bearer {token}`
4. Token refreshes automatically

---

## 🚢 Deployment

### Docker

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec app python manage.py migrate

# Collect static files
docker-compose exec app python manage.py collectstatic --noinput
```

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Set secure SECRET_KEY
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure email service (SendGrid, AWS SES, etc.)
- [ ] Set up Redis on production host
- [ ] Monitor Celery workers
- [ ] Set up proper logging
- [ ] Configure backups

---

## 📚 Learning Resources

This project teaches:
- Django ORM & relationships
- Django REST Framework
- Celery & async tasks
- Redis caching
- JWT authentication
- RBAC & permissions
- Testing strategies
- Docker containerization
- Production patterns

---

## 🐛 Troubleshooting

### "No module named 'eventhub_config'"
```bash
# Ensure you're in the right directory and venv is activated
python manage.py migrate
```

### Celery not working
```bash
# Make sure Redis is running
redis-cli ping  # Should return "PONG"

# Check Celery worker logs
celery -A eventhub_config worker --loglevel=debug
```

### PostgreSQL connection error
```bash
# Check connection string in .env
# Make sure PostgreSQL is running
psql -U eventhub -h localhost -d eventhub
```

### Migration issues
```bash
# Reset migrations (dev only!)
python manage.py migrate apps 0001 --fake-initial
python manage.py migrate
```

---

## 📝 Development Phases

1. **Setup** (30 min) - Project initialization
2. **Core Models** (1 hour) - Event, Booking, Payment
3. **API Endpoints** (1.5 hours) - ViewSets, Serializers
4. **Authentication** (45 min) - JWT, Permissions
5. **Celery Tasks** (1 hour) - Async notifications
6. **Testing** (1 hour) - Unit and integration tests
7. **Documentation** (30 min) - README, docstrings

**Total**: ~6-8 hours

---

## 🎯 Next Steps

### Completed in This Phase
- [ ] Django project setup
- [ ] Database models created
- [ ] API endpoints implemented
- [ ] Mock payment system
- [ ] Celery tasks configured
- [ ] Unit tests written
- [ ] Documentation complete

### Future Enhancements
- [ ] Real Stripe integration
- [ ] WebSocket for real-time updates
- [ ] Search with Elasticsearch
- [ ] Admin analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Advanced caching strategies
- [ ] GraphQL API support

---

## 📞 Support

For issues or questions:
1. Check EVENT_HUB_PLAN.md for detailed implementation guide
2. Review test files for examples
3. Check Django/DRF documentation
4. Review Celery best practices

---

## 📄 License

Educational project for learning purposes.

---

**Last Updated**: December 20, 2025
**Status**: Ready for Development
**Version**: 1.0
