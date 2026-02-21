# Module 14: Testing & Deployment of Web Applications

> **Prerequisite:** Module 12 (FastAPI + JWT auth + SQLAlchemy 2.0). JWT authentication and database setup are not re-explained here.

This module extends the FastAPI pattern from Module 12 into a production-grade **Contacts API** — a personal address book with email verification, file uploads, caching, comprehensive testing, and cloud deployment.

---

## Start Here

1. **[docs/LEARNING_PATH.md](docs/LEARNING_PATH.md)** — sequential 7-step path through the module
2. **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — run the app in 5 minutes
3. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — system design with Mermaid diagrams
4. [docs/LESSON_PLAN.md](docs/LESSON_PLAN.md) - lesson plan step-by-step

---

## What's Built

One realistic application built progressively across 7 steps:

```
Contacts API
├── Email verification on registration (FastAPI-Mail + JWT token)
├── File upload to cloud storage (Cloudinary avatar)
├── Rate limiting on auth endpoints (SlowAPI + Redis)
├── Birthday query caching (Redis cache-aside)
├── Comprehensive test suite (pytest-asyncio + 80% coverage)
└── CI/CD + cloud deployment (GitHub Actions + Render.com)
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register → send verification email |
| GET | `/api/v1/auth/verify/{token}` | Verify email via JWT token |
| POST | `/api/v1/auth/login` | Login (only if verified) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Blacklist refresh token in Redis |
| GET | `/api/v1/contacts` | List contacts (search + pagination) |
| POST | `/api/v1/contacts` | Create contact |
| GET/PUT/PATCH/DELETE | `/api/v1/contacts/{id}` | Manage contact |
| GET | `/api/v1/contacts/birthdays` | Birthdays in next 7 days (cached) |
| GET/PATCH | `/api/v1/users/me` | Profile management |
| POST | `/api/v1/users/me/avatar` | Upload avatar to Cloudinary |

---

## Standalone Examples

Single-concept files to study before or alongside the main app:

| File | Topic |
|------|-------|
| [01_email_sending.py](standalone_examples/01_email_sending.py) | smtplib → aiosmtplib → FastAPI-Mail |
| [02_email_verification_tokens.py](standalone_examples/02_email_verification_tokens.py) | Why email links expire (UUID → JWT+purpose+TTL) |
| [03_cloudinary_upload.py](standalone_examples/03_cloudinary_upload.py) | File upload, transform, delete |
| [04_rate_limiting.py](standalone_examples/04_rate_limiting.py) | SlowAPI rate limiting |
| [05_redis_caching.py](standalone_examples/05_redis_caching.py) | Cache-aside pattern with Redis |
| [06_async_testing.py](standalone_examples/06_async_testing.py) | pytest-asyncio + mocks |
| [07_github_actions_explained.py](standalone_examples/07_github_actions_explained.py) | Generates CI/CD YAML with explanations |

---

## Quick Commands

```bash
# Run the full app
cd contacts_api
cp .env.example .env           # fill in Cloudinary credentials
docker-compose up

# Swagger UI
open http://localhost:8000/docs

# Check emails (dev only — MailHog)
open http://localhost:8025

# Run tests
pytest tests/ -v --cov=app --cov-report=term-missing

# Generate CI/CD config
python standalone_examples/07_github_actions_explained.py > contacts_api/.github/workflows/ci.yml
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 async |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Email | FastAPI-Mail 1.4 + MailHog (dev) |
| File storage | Cloudinary |
| Caching / Rate limiting | Redis 7 + SlowAPI |
| Testing | pytest-asyncio + httpx + aiosqlite |
| CI/CD | GitHub Actions |
| Deployment | Render.com |

---

## Key Concepts Introduced

| Concept | Where |
|---------|-------|
| Email verification with time-limited JWT | `standalone_examples/02`, `app/services/email.py` |
| Why links without expiry are a security risk | `standalone_examples/02_email_verification_tokens.py` |
| Cloud file storage (upload + transform) | `standalone_examples/03`, `app/services/cloudinary_service.py` |
| Rate limiting on auth endpoints | `standalone_examples/04`, `app/core/rate_limit.py` |
| Cache-aside pattern with TTL | `standalone_examples/05`, `app/core/cache.py` |
| Async testing: mocks, fixtures, coverage | `standalone_examples/06`, `tests/` |
| CI/CD pipeline | `standalone_examples/07`, `.github/workflows/ci.yml` |

---

## Connection to Previous Modules

| Module | What was learned | How Module 14 extends it |
|--------|-----------------|--------------------------|
| **Module 12** | JWT access + refresh tokens | Adds email JWT with `purpose` claim; Redis token blacklist for logout |
| **Module 12** | `Settings(BaseSettings)`, async SQLAlchemy | Extended with SMTP, Cloudinary, Redis settings |
| **Module 12** | `AsyncClient + ASGITransport` test pattern | Same conftest.py pattern, extended with email/cloudinary mocks |
| **Module 8** | SQLAlchemy relationships, date queries | Birthday query uses `func.extract()` |
| **Module 10** | Django ORM filter patterns | Comparison notes in LEARNING_PATH.md |
