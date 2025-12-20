# Event Hub - Полный план реализации

**Дата**: 20 Декабря 2025
**Тип**: Django + DRF + Celery + PostgreSQL + Mock Платежи
**Время**: ~6-8 часов
**Сложность**: Средняя-Высокая

---

## 🎯 Проект Overview

Event Hub - платформа для управления и бронирования событий (мастер-классы, конференции, вебинары и т.д.)

### Основной функционал:
- 📅 Каталог событий с фильтрацией
- 🎫 Система бронирования билетов
- 💳 Mock система оплаты (не реальные деньги)
- ⏳ Лист ожидания при переполнении
- ⭐ Рейтинги и отзывы о событиях
- 📧 Email напоминания (Celery)
- 👥 RBAC (Organizer, Attendee, Admin)
- 📊 Dashboard для организаторов
- 🔐 JWT Authentication

---

## 📁 Структура проекта

```
04_event_hub/
├── eventhub_config/              # Django project config
│   ├── settings.py               # Все settings с .env
│   ├── urls.py                   # Root URL patterns
│   ├── wsgi.py
│   └── celery.py                 # Celery configuration
│
├── apps/
│   ├── events/                   # Events management
│   │   ├── models.py             # Event, Session, Venue, Category
│   │   ├── views.py              # EventViewSet, SessionViewSet
│   │   ├── serializers.py        # Event, Session serializers
│   │   ├── filters.py            # Search & filtering
│   │   └── tests.py              # Unit tests
│   │
│   ├── bookings/                 # Booking management
│   │   ├── models.py             # Booking, Ticket, Waitlist
│   │   ├── views.py              # BookingViewSet
│   │   ├── serializers.py        # Booking serializers
│   │   └── tests.py
│   │
│   ├── payments/                 # Payment handling (Mock)
│   │   ├── models.py             # Payment, Transaction
│   │   ├── views.py              # PaymentViewSet
│   │   ├── serializers.py
│   │   ├── mock.py               # Mock payment service
│   │   └── tests.py
│   │
│   ├── users/                    # User management
│   │   ├── models.py             # CustomUser, Profile, Review
│   │   ├── views.py              # UserViewSet, AuthViewSet
│   │   ├── serializers.py        # User, Auth serializers
│   │   └── tests.py
│   │
│   └── notifications/            # Email notifications
│       ├── models.py             # Notification
│       ├── tasks.py              # Celery tasks
│       └── templates/            # Email templates
│
├── templates/                    # HTML templates (optional)
├── static/                       # Static files
├── manage.py
├── .env.example                  # Environment template
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md                     # Documentation
└── DEVELOPMENT.md                # Dev guide

```

---

## 💾 Database Models

### 1. **Event** (События)
```python
class Event(models.Model):
    title = CharField(100)
    description = TextField()
    organizer = ForeignKey(User)  # Who created
    category = ForeignKey(Category)  # Tech, Music, Business, etc.

    location = CharField(200)
    online_meeting_url = URLField(null=True)

    start_date = DateTimeField()
    end_date = DateTimeField()

    max_capacity = IntegerField()
    current_attendees = IntegerField(default=0)

    price = DecimalField()
    image = ImageField()

    status = CharField(choices=[DRAFT, PUBLISHED, CANCELLED])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### 2. **Session** (Сеансы события)
```python
class Session(models.Model):
    event = ForeignKey(Event)
    title = CharField(100)
    start_time = DateTimeField()
    end_time = DateTimeField()
    room = CharField(100)  # Room number or "Online"
    speaker = ForeignKey(User)  # Who's speaking
    capacity = IntegerField()
```

### 3. **Booking** (Бронирования)
```python
class Booking(models.Model):
    attendee = ForeignKey(User)
    event = ForeignKey(Event)
    quantity = IntegerField()

    total_price = DecimalField()
    status = CharField(choices=[PENDING, CONFIRMED, CANCELLED])

    booked_at = DateTimeField(auto_now_add=True)
    payment = OneToOneField(Payment, null=True)
```

### 4. **Payment** (Платежи - MOCK)
```python
class Payment(models.Model):
    booking = ForeignKey(Booking)
    amount = DecimalField()

    # Mock платежи
    payment_method = CharField(choices=[MOCK_CARD, MOCK_PAYPAL])
    reference_id = CharField()  # Mock transaction ID

    status = CharField(choices=[PENDING, COMPLETED, FAILED])
    processed_at = DateTimeField(null=True)
```

### 5. **Waitlist** (Лист ожидания)
```python
class Waitlist(models.Model):
    event = ForeignKey(Event)
    user = ForeignKey(User)
    quantity = IntegerField()

    position = IntegerField()  # Queue position
    created_at = DateTimeField()
    notified = BooleanField(default=False)
```

### 6. **Review** (Отзывы)
```python
class Review(models.Model):
    event = ForeignKey(Event)
    author = ForeignKey(User)
    rating = IntegerField(1-5)
    comment = TextField()

    created_at = DateTimeField(auto_now_add=True)
```

### 7. **Certificate** (Сертификаты)
```python
class Certificate(models.Model):
    event = ForeignKey(Event)
    attendee = ForeignKey(User)
    certificate_number = CharField(unique=True)
    issued_at = DateTimeField()
```

---

## 🔑 API Endpoints (DRF)

### Events
- `GET /api/events/` - List with filtering, pagination
- `GET /api/events/{id}/` - Event details
- `POST /api/events/` - Create event (Organizer only)
- `PUT /api/events/{id}/` - Update (Organizer only)
- `DELETE /api/events/{id}/` - Delete (Organizer only)

### Sessions
- `GET /api/events/{id}/sessions/` - Sessions for event
- `POST /api/events/{id}/sessions/` - Create session

### Bookings
- `GET /api/bookings/` - My bookings
- `POST /api/bookings/` - Create booking
- `POST /api/bookings/{id}/cancel/` - Cancel booking

### Payments (Mock)
- `POST /api/payments/` - Process payment (Mock)
- `GET /api/payments/{id}/` - Payment status
- `POST /api/payments/{id}/simulate-webhook/` - Simulate payment callback

### Waitlist
- `GET /api/events/{id}/waitlist/` - Current position
- `POST /api/events/{id}/waitlist/` - Join waitlist

### Reviews
- `GET /api/events/{id}/reviews/` - Event reviews
- `POST /api/events/{id}/reviews/` - Post review

### Auth
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login (JWT)
- `POST /api/auth/refresh/` - Refresh token

### Users
- `GET /api/users/me/` - Current user
- `PUT /api/users/me/` - Update profile
- `GET /api/users/{id}/` - Public profile
- `GET /api/users/{id}/events/` - User's organized events

---

## ⚡ Celery Tasks

```python
# В notifications/tasks.py

@shared_task
def send_booking_confirmation(booking_id):
    """Send confirmation email after booking"""

@shared_task
def send_event_reminder(event_id):
    """Send reminder 1 day before event"""

@shared_task
def send_waitlist_notification(waitlist_id):
    """Notify from waitlist when spot opens"""

@shared_task
def send_post_event_survey(event_id):
    """Send feedback survey after event"""

@shared_task
def process_payment_timeout(booking_id):
    """Cancel booking if payment not completed in 15 min"""
```

---

## 🔐 RBAC (Role-Based Access Control)

```
User Types:
├── Attendee (default)
│   ├── Can browse events
│   ├── Can book tickets
│   ├── Can leave reviews
│   └── Can manage own bookings
│
├── Organizer
│   ├── All Attendee permissions
│   ├── Can create/edit/delete own events
│   ├── Can view booking statistics
│   ├── Can manage sessions
│   └── Can generate certificates
│
└── Admin
    ├── All permissions
    ├── Can moderate reviews
    ├── Can create promotions/discounts
    ├── Can view platform statistics
    └── Can manage categories
```

**Реализация**: Django Permissions + DRF IsAuthenticated checks

---

## 💳 Mock Payment Flow

```
User clicks "Pay" on booking
    ↓
POST /api/payments/ with mock_payment_method
    ↓
Payment Service receives request
    ↓
Validate (mock - always success except edge cases)
    ↓
Generate fake transaction ID
    ↓
Return payment status: PENDING (simulating processing)
    ↓
Celery task checks after 2 seconds
    ↓
Sets status to COMPLETED
    ↓
Calls booking confirmation task
    ↓
Sends email to user
```

**Mock Card Numbers** (всегда успешны):
- 4111 1111 1111 1111 - Success
- 4000 0000 0000 0002 - Decline (для тестирования)

---

## 📧 Email Notifications

Templates:
- `booking_confirmation.html` - Booking confirmed
- `event_reminder.html` - 1 day before event
- `waitlist_notification.html` - Your turn from waitlist!
- `post_event_survey.html` - How was the event?
- `certificate.html` - Your certificate ready

**Delivery**: Celery tasks (async)

---

## 🧪 Testing Strategy

### Unit Tests (~30 tests)
- Model tests (create, validation, methods)
- Serializer tests (data validation)
- View/ViewSet tests (permissions, responses)
- Task tests (Celery tasks)

### Integration Tests (~15 tests)
- Full booking flow
- Payment processing
- Waitlist notification
- Email sending

### Test Coverage Target: 80%+

---

## 🚀 Development Phases

### Phase 1: Setup (30 min)
- Django project init
- Models creation
- Database setup
- Admin panel

### Phase 2: Core API (2 hours)
- Event CRUD endpoints
- Serializers & filters
- Pagination & search
- Tests

### Phase 3: Booking System (1.5 hours)
- Booking model & views
- Ticket management
- Waitlist logic
- Tests

### Phase 4: Payments (1 hour)
- Mock payment service
- Payment model
- Webhook simulation
- Tests

### Phase 5: Notifications (1 hour)
- Celery setup
- Email tasks
- Celery Beat scheduling
- Tests

### Phase 6: Polish (30 min)
- Documentation
- Docker setup
- README
- Dev guide

**Total: ~6-8 часов работы**

---

## 🐳 Docker Setup

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: eventhub
      POSTGRES_USER: eventhub
      POSTGRES_PASSWORD: eventhub_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DEBUG=True
      - DATABASE_URL=postgres://...
      - REDIS_URL=redis://redis:6379

  celery:
    build: .
    command: celery -A eventhub_config worker --loglevel=info
    depends_on:
      - redis
      - postgres

  celery_beat:
    build: .
    command: celery -A eventhub_config beat --loglevel=info
    depends_on:
      - redis
      - postgres
```

---

## 📊 Database Statistics

Expected:
- ~7 models
- ~15 API endpoints
- ~50 unit tests
- ~200+ lines per model
- ~300+ lines per serializer
- ~500+ lines per viewset

**Total code**: ~3,000+ lines

---

## 🔧 Environment Variables

```
# .env.example
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://eventhub:eventhub_pass@localhost:5432/eventhub

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Mock Payments
MOCK_PAYMENT_SUCCESS_RATE=0.95  # 95% успешных платежей
```

---

## 📚 Learning Outcomes

After completing this project, you will understand:

✅ Advanced Django ORM (relationships, aggregations, annotations)
✅ Django REST Framework (ViewSets, Serializers, Filtering)
✅ Celery for async tasks & scheduled jobs
✅ Redis for caching & message broker
✅ RBAC & permission systems
✅ Payment processing (even mock)
✅ Testing Django applications
✅ Docker containerization
✅ Production-ready patterns
✅ API design best practices

---

## ✅ Success Criteria

- [ ] All models created and migrated
- [ ] All API endpoints working
- [ ] Mock payment system functional
- [ ] Celery tasks working
- [ ] At least 50+ unit tests
- [ ] 80%+ code coverage
- [ ] Docker setup complete
- [ ] Full documentation
- [ ] Ready for deployment

---

## 🎯 Next Steps After Event Hub

1. Add Stripe real integration
2. Add WebSocket for real-time updates
3. Add search with Elasticsearch
4. Add admin analytics dashboard
5. Deploy to production (AWS/Heroku)
6. Add mobile app (React Native)

---

**Status**: 📋 Planning
**Difficulty**: Средняя-Высокая
**Estimated Time**: 6-8 часов
