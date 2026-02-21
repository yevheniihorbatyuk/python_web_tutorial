# Module 14 — Index

## Documentation

| File | Purpose |
|------|---------|
| [README.md](README.md) | Overview, quick commands, tech stack |
| [docs/LEARNING_PATH.md](docs/LEARNING_PATH.md) | Sequential 7-step path through module |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Run app in 5 minutes |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mermaid diagrams: system, email flow, caching |
| [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) | Unit vs integration tests, coverage, mocking |
| [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | Render.com step-by-step + Gmail SMTP setup |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | All endpoints with curl examples |

## Standalone Examples

| File | Topic | Runnable |
|------|-------|---------|
| [01_email_sending.py](standalone_examples/01_email_sending.py) | SMTP basics → FastAPI-Mail | MailHog needed |
| [02_email_verification_tokens.py](standalone_examples/02_email_verification_tokens.py) | Token security: UUID → JWT+TTL | Self-contained |
| [03_cloudinary_upload.py](standalone_examples/03_cloudinary_upload.py) | Cloudinary SDK | Cloudinary account |
| [04_rate_limiting.py](standalone_examples/04_rate_limiting.py) | SlowAPI rate limiting | Self-contained |
| [05_redis_caching.py](standalone_examples/05_redis_caching.py) | Cache-aside pattern | Redis needed |
| [06_async_testing.py](standalone_examples/06_async_testing.py) | pytest-asyncio patterns | `pytest 06_async_testing.py` |
| [07_github_actions_explained.py](standalone_examples/07_github_actions_explained.py) | Generates CI YAML | Self-contained |

## Contacts API

### Infrastructure
| File | Purpose |
|------|---------|
| [contacts_api/docker-compose.yml](contacts_api/docker-compose.yml) | postgres + redis + mailhog + app |
| [contacts_api/Dockerfile](contacts_api/Dockerfile) | App container |
| [contacts_api/.env.example](contacts_api/.env.example) | Required env vars |
| [contacts_api/pyproject.toml](contacts_api/pyproject.toml) | pytest config + coverage |
| [contacts_api/requirements.txt](contacts_api/requirements.txt) | Production deps |
| [contacts_api/requirements-dev.txt](contacts_api/requirements-dev.txt) | Dev/test deps |

### Application Code
| File | Purpose |
|------|---------|
| `app/main.py` | App factory, router registration, middleware |
| `app/config.py` | Settings (extends Module 12 pattern) |
| `app/database.py` | Async engine, session factory, `get_db` |
| `app/models/user.py` | User + is_verified + avatar_url |
| `app/models/contact.py` | Contact with birthday field |
| `app/schemas/user.py` | UserCreate, UserResponse, UserUpdate |
| `app/schemas/contact.py` | ContactCreate, ContactResponse, ContactUpdate |
| `app/schemas/token.py` | Token, TokenData |
| `app/core/security.py` | JWT: access + refresh + email tokens |
| `app/core/dependencies.py` | get_current_user, require_verified |
| `app/core/rate_limit.py` | SlowAPI + Redis limiter |
| `app/core/cache.py` | Redis cache-aside helper |
| `app/services/auth.py` | get_user_by_email, create_user |
| `app/services/email.py` | FastAPI-Mail integration |
| `app/services/cloudinary_service.py` | Upload, validate MIME type |
| `app/services/contacts.py` | CRUD + birthday query |
| `app/api/v1/auth.py` | register, verify, login, refresh, logout |
| `app/api/v1/contacts.py` | CRUD + birthdays endpoint |
| `app/api/v1/users.py` | me, avatar upload |

### Tests
| File | What it tests |
|------|--------------|
| `tests/conftest.py` | AsyncClient + ASGITransport + SQLite fixture |
| `tests/unit/test_security.py` | JWT claims, purpose, expiry, passwords |
| `tests/unit/test_contact_service.py` | Birthday date arithmetic edge cases |
| `tests/unit/test_email_service.py` | Mock FastMail.send_message |
| `tests/integration/test_auth.py` | Full register→verify→login→refresh flow |
| `tests/integration/test_contacts.py` | CRUD + birthday + caching + rate limit |
| `tests/integration/test_users.py` | Profile + avatar upload (mock Cloudinary) |

### Migrations & CI
| File | Purpose |
|------|---------|
| `alembic/versions/001_create_users.py` | Create users table |
| `alembic/versions/002_create_contacts.py` | Create contacts table |
| `.github/workflows/ci.yml` | Run tests on push, fail before deploy |
