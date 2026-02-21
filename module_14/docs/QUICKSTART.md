# Quickstart — Run in 5 Minutes

## Prerequisites

- Docker Desktop running
- A free [Cloudinary](https://cloudinary.com) account (no credit card)
- Git

## Steps

### 1. Clone and configure

```bash
cd /path/to/module_14/contacts_api
cp .env.example .env
```

Open `.env` and fill in your Cloudinary credentials:

```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-api-secret
```

Everything else works with defaults for local development.

### 2. Start services

```bash
docker-compose up
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **MailHog** on ports 1025 (SMTP) and 8025 (web UI)
- **FastAPI app** on port 8000

Wait for `INFO: Application startup complete.`

### 3. Run migrations

In a second terminal:

```bash
docker-compose exec app alembic upgrade head
```

### 4. Open Swagger UI

```
http://localhost:8000/docs
```

### 5. Try the full flow

**Step 1:** Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "username": "alice", "password": "SecurePass123!"}'
```

**Step 2:** Check the verification email

Open **http://localhost:8025** (MailHog). You'll see the verification email.
Click the verification link, or copy the token and call:

```bash
curl http://localhost:8000/api/v1/auth/verify/YOUR_TOKEN_HERE
```

**Step 3:** Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "SecurePass123!"}'
```

Save the `access_token` from the response.

**Step 4:** Create a contact

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob@example.com",
    "phone": "+380501234567",
    "birthday": "1990-03-15"
  }'
```

**Step 5:** Get contacts with birthdays in next 7 days

```bash
curl http://localhost:8000/api/v1/contacts/birthdays \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Run Tests

```bash
# In a separate terminal (outside Docker, uses SQLite in-memory)
cd contacts_api
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Standalone Examples

Each file in `standalone_examples/` runs independently:

```bash
# Email sending basics (requires MailHog)
python standalone_examples/01_email_sending.py

# Token security demonstration (self-contained)
python standalone_examples/02_email_verification_tokens.py

# Rate limiting demo (self-contained)
python standalone_examples/04_rate_limiting.py

# Run async tests
pytest standalone_examples/06_async_testing.py -v

# Generate CI/CD workflow file
python standalone_examples/07_github_actions_explained.py > contacts_api/.github/workflows/ci.yml
```

---

## Troubleshooting

**Port already in use:**
```bash
docker-compose down && docker-compose up
```

**Database not ready:**
```bash
docker-compose exec app alembic upgrade head
```

**Email not arriving in MailHog:**
- Verify `SMTP_HOST=mailhog` in `.env` (not `localhost`)
- Check `docker-compose logs mailhog`

**Cloudinary upload fails:**
- Verify credentials in `.env`
- Test with `python standalone_examples/03_cloudinary_upload.py`
