# Contacts API

FastAPI application built progressively through Module 14.
For the learning path, diagrams, and explanations see [../docs/](../docs/).

---

## Quick Start

```bash
# 1. Copy env and fill in Cloudinary credentials
cp .env.example .env

# 2. Start all services
docker-compose up

# 3. Run migrations
docker-compose exec app alembic upgrade head

# 4. Open Swagger UI
open http://localhost:8000/docs

# 5. Check emails (MailHog dev inbox)
open http://localhost:8025
```

## Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# All tests with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Unit tests only (no services needed, very fast)
pytest tests/unit/ -v
```

## Project Structure

```
app/
├── main.py             ← FastAPI app factory
├── config.py           ← Settings from .env
├── database.py         ← Async SQLAlchemy engine
├── models/             ← SQLAlchemy ORM models
├── schemas/            ← Pydantic request/response models
├── core/
│   ├── security.py     ← JWT: 3 token types (access, refresh, email)
│   ├── dependencies.py ← get_current_user, require_verified
│   ├── rate_limit.py   ← SlowAPI limiter
│   └── cache.py        ← Redis cache-aside + token blacklist
├── services/
│   ├── auth.py         ← User DB operations
│   ├── email.py        ← FastAPI-Mail
│   ├── cloudinary_service.py ← File upload + MIME validation
│   └── contacts.py     ← CRUD + birthday query
└── api/v1/
    ├── auth.py         ← register, verify, login, refresh, logout
    ├── contacts.py     ← CRUD + /birthdays (cached)
    └── users.py        ← profile, avatar upload

tests/
├── conftest.py         ← SQLite in-memory + mocked Redis/Email
├── unit/               ← No external services (fast)
└── integration/        ← Full HTTP flows

alembic/
└── versions/           ← Hand-written SQL migrations (readable!)
```

## Environment Variables

See [.env.example](.env.example) for all required variables with comments.

Minimum for local dev (MailHog handles email, no Cloudinary needed):

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/contacts_db
JWT_SECRET_KEY=any-random-string
JWT_REFRESH_SECRET=another-random-string
EMAIL_TOKEN_SECRET=yet-another-random-string
REDIS_URL=redis://redis:6379/0
```
