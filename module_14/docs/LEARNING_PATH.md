# Learning Path — Module 14

Module 14 follows a **single progressive application** approach: one Contacts API built step by step, where each step adds a new real-world capability. The order mirrors how you'd actually build this at work.

---

## Why no separate "beginner/advanced" editions?

The four topics in this module (email, file uploads, testing, deployment) are **sequential, not parallel**. You can't meaningfully test code you haven't written, and you can't deploy something that doesn't work. Separate editions would require duplicating the same contacts domain across three codebases for no educational gain. Instead, each step builds directly on the previous one.

---

## Recommended Order

### Before You Start

- Complete Module 12 (FastAPI + JWT + SQLAlchemy)
- Read [QUICKSTART.md](QUICKSTART.md) — run the app locally
- Read [ARCHITECTURE.md](ARCHITECTURE.md) — understand the system before diving into code

---

### Step 1: Domain Foundation — Contacts CRUD

**Files to read:**
- `app/models/contact.py` — Contact model with birthday field
- `app/schemas/contact.py` — Pydantic schemas
- `app/services/contacts.py` — business logic
- `app/api/v1/contacts.py` — endpoints

**What's new vs Module 12:**
- `Date` field type (birthday)
- Partial updates with `PATCH` and `model_dump(exclude_unset=True)`
- Search with SQLAlchemy `ilike()` (compare: Django's `filter(name__icontains=q)`)
- Pagination with `offset` + `limit`

**Module 12 connection:**
The `Contact` model follows the same `Mapped[]` + `mapped_column()` pattern as Module 12's User model. The `get_current_user` dependency is imported unchanged.

---

### Step 2: Email Verification

**Standalone example first:** `standalone_examples/02_email_verification_tokens.py`

This is the conceptual core of the step. Run it and read the output before touching the app code.

**Files to read:**
- `app/core/security.py` — `create_email_token()`, `decode_email_token()`
- `app/services/email.py` — FastAPI-Mail integration
- `app/api/v1/auth.py` — register + verify endpoints
- `app/models/user.py` — `is_verified` field

**What's new:**
- Email JWT with `purpose` claim: why the same JWT library serves two different token types safely
- Why email links without expiry are a security risk (standalone 02 demonstrates this)
- FastAPI-Mail vs smtplib: async vs blocking I/O (standalone 01 shows the difference)
- MailHog for local email testing (no real SMTP needed)

**Key security concept:**
```python
# Access token payload (Module 12):
{"sub": 42, "type": "access", "exp": ...}

# Email verification token payload (Module 14):
{"sub": "alice@example.com", "purpose": "email_verify", "exp": now + 24h}

# The 'purpose' claim prevents an access token from being used
# as a verification token, even though both are JWTs.
```

---

### Step 3: File Upload to Cloud Storage

**Standalone example first:** `standalone_examples/03_cloudinary_upload.py`

**Files to read:**
- `app/services/cloudinary_service.py` — upload, MIME validation
- `app/api/v1/users.py` — `POST /users/me/avatar`
- `app/schemas/user.py` — UserResponse with `avatar_url`

**What's new:**
- `UploadFile` in FastAPI — how multipart form data differs from JSON
- MIME type validation before uploading (server-side security)
- Cloudinary URL structure — why store a URL, not a file path
- Image transformations via URL (resize to 200×200 avatar without re-uploading)

**Why Cloudinary and not S3:**
- Free tier, no credit card, instant signup
- Built-in image transformations
- Python SDK with sync + async support
- `DEPLOYMENT_GUIDE.md` covers S3 as the production alternative with equivalent code

---

### Step 4: Rate Limiting

**Standalone example first:** `standalone_examples/04_rate_limiting.py`

**Files to read:**
- `app/core/rate_limit.py` — SlowAPI setup
- `app/api/v1/auth.py` — `@limiter.limit("5/minute")` on register/login

**What's new:**
- Why rate limiting belongs on auth endpoints specifically (prevent brute force, bot registration)
- SlowAPI's Redis backend for distributed rate limits (one counter per IP across multiple app instances)
- Testing: rate limiter must be disabled in tests to avoid test isolation issues

---

### Step 5: Redis Caching

**Standalone example first:** `standalone_examples/05_redis_caching.py`

**Files to read:**
- `app/core/cache.py` — `get_or_set_cache()` helper
- `app/api/v1/contacts.py` — birthday endpoint using cache

**What's new:**
- Cache-aside pattern: check cache → miss → query DB → store → return
- Cache key design: `birthdays:{user_id}:{today_date}` — why include today's date
- TTL = 1 hour: birthday data changes rarely, so stale for up to 1h is acceptable
- Cache invalidation: delete key when contact is created/updated/deleted

**Birthday query (interesting SQL):**
```python
# Find contacts whose birthday falls within next 7 days
# This requires comparing month+day across year boundaries
# e.g., Dec 28 + 7 days = Jan 4 of next year
```

See `app/services/contacts.py` for the PostgreSQL `EXTRACT()` approach.

---

### Step 6: Testing

**Standalone example first:** `standalone_examples/06_async_testing.py`

This is both a tutorial and a runnable test file.

**Files to read:**
- `tests/conftest.py` — fixture setup
- `tests/unit/test_security.py` — pure function tests
- `tests/unit/test_contact_service.py` — birthday edge cases
- `tests/integration/test_auth.py` — full auth flow

**What's new:**
- Difference between unit tests (SQLite + no mocks) and integration tests (full HTTP)
- `AsyncMock` for mocking async I/O (email, Cloudinary)
- `dependency_overrides` to replace email service and rate limiter in tests
- `pytest-cov` — reading coverage reports, what 80% means in practice
- `asyncio_mode = "auto"` — no `@pytest.mark.asyncio` needed on every test

**Test isolation principle:**
Each test starts with a clean SQLite in-memory database. No test state leaks between tests.

---

### Step 7: CI/CD and Deployment

**Standalone example first:**
```bash
python standalone_examples/07_github_actions_explained.py
```

Read the generated YAML and the Python comments that explain each section.

**Files to read:**
- [docs/DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — full Render.com walkthrough
- `.github/workflows/ci.yml` — the generated CI config
- `docker-compose.yml` vs `Dockerfile` — dev vs production image

**What's new:**
- GitHub Actions: workflow triggers, job steps, service containers
- Why unit tests use SQLite but CI integration tests use PostgreSQL
- Render.com: free PostgreSQL, environment variables, auto-deploy from GitHub
- Alembic migration as part of the start command (not a separate step)
- Gmail App Password vs main password (for SMTP in production)

---

## Time Estimates

| Step | Topic | Time |
|------|-------|------|
| 1 | Contacts CRUD | 1h |
| 2 | Email verification | 1.5h |
| 3 | File uploads | 1h |
| 4 | Rate limiting | 0.5h |
| 5 | Redis caching | 1h |
| 6 | Testing | 2h |
| 7 | Deployment | 1.5h |
| **Total** | | **~8.5h** |

---

## Where These Topics Appear Next

| Topic | Where it shows up later |
|-------|------------------------|
| Email verification | Any production web app: password reset, notifications |
| File uploads | Profile photos, document management, media applications |
| Rate limiting | All public APIs to prevent abuse |
| Redis caching | Session storage, feed caching, leaderboards |
| pytest-asyncio | All subsequent async Python projects |
| GitHub Actions | All professional projects with automated testing |
| Render/cloud deployment | Alternative: Railway, Fly.io, AWS, GCP |
