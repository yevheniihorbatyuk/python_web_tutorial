# Advanced Edition - Production FastAPI Patterns

This edition focuses on real-world architecture with a full ML Registry application and a focused async reference file.

---

## What's Included

### 1) Async Patterns Reference
File: `async_patterns.py`

Covers:
- Async/await basics
- Task scheduling
- Concurrency patterns
- Common pitfalls

### 2) ML Registry App
Path: `ml_registry_app/`

Features:
- JWT authentication with refresh tokens
- PostgreSQL + SQLAlchemy 2.0 (async)
- MinIO for file storage
- Redis integration
- Alembic migrations
- Comprehensive test suite
- Docker Compose stack

---

## Quick Start

```bash
cd ml_registry_app
cp .env.example .env

docker-compose up -d
```

Open:
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (minioadmin / minioadmin123)

Run tests:
```bash
pytest tests/ -v
```

---

## Suggested Extensions (Optional)

These are good advanced exercises but are not implemented by default:
- OAuth2 login (Google/GitHub)
- Role-based access control (RBAC)
- API key authentication for service clients
- Observability (tracing, metrics)
