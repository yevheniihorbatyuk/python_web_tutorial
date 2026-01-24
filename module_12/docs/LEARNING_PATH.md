# Learning Paths - FastAPI Module 12

Choose a path based on your experience level and time.

---

## Quick Decision

**New to FastAPI?** → Beginner Path (6-8 hours)

**Know the basics?** → Intermediate Path (3-4 hours)

**Want production patterns?** → Advanced Path (4-6 hours)

---

## Beginner Path (6-8 hours)

### Phase 1: Standalone Concepts (1.5-2 hours)
Location: `beginner_edition/standalone_examples/`

1. `1_minimal_app.py` (30 min) - Routes, parameters, Pydantic
2. `2_database_basics.py` (40 min) - SQLAlchemy models & CRUD
3. `3_auth_basics.py` (40 min) - JWT & password hashing
4. `4_test_examples.py` (40 min) - pytest basics

**Method:** Run → Read → Modify → Break → Fix

### Phase 2: First Real App (2-3 hours)
Location: `beginner_edition/todo_app/`

- Read README and run with Docker
- Study `app/main.py`, `models.py`, `schemas.py`, `auth.py`
- Test endpoints in `/docs`
- Extend with one new feature

---

## Intermediate Path (3-4 hours)

Location: `intermediate_edition/blog_api/`

**Focus:** Relationships, pagination, filtering, multi-user authorization

1. Read `intermediate_edition/README.md`
2. Run `blog_api` with Docker Compose
3. Study `app/models.py` (User → Post → Comment)
4. Explore pagination and filtering in `/posts`
5. Build a small extension (e.g., categories or tags)

---

## Advanced Path (4-6 hours)

Location: `advanced_edition/`

**Focus:** Production architecture and system-level patterns

1. Read `advanced_edition/README.md`
2. Study `async_patterns.py`
3. Run `ml_registry_app` with Docker Compose
4. Explore the API in `/docs`
5. Review tests and Alembic migrations

---

## Optional Extensions (After Core)

Use these as capstone topics for senior-level discussion:

- OAuth2 login (Google/GitHub)
- Role-based access control (RBAC)
- API key management
- Async task queues (Celery/Arq)
- Observability (tracing, metrics)

---

## Next Steps

1. Pick a path
2. Use `docs/QUICKSTART.md` to run the app
3. Track progress in `docs/CHECKLIST.md`
