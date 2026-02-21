# Deployment Guide — Render.com

## Why Render.com

| Platform | Free PostgreSQL | No credit card | Auto-deploy | Notes |
|----------|----------------|----------------|-------------|-------|
| **Render** | ✅ | ✅ | ✅ | Best free tier for this stack |
| Railway | ✅ | ❌ | ✅ | Free tier removed |
| Fly.io | ❌ | ❌ | ✅ | Requires CLI + billing |
| Heroku | ❌ | ❌ | ✅ | No longer free |

Render's free tier includes: 1 PostgreSQL database, 1 Redis instance, 1 web service. Sufficient for this app.

---

## Step 1: Prepare Your Repository

Push your code to GitHub:

```bash
cd contacts_api
git init
git add .
git commit -m "contacts api initial"
git remote add origin https://github.com/YOUR_USERNAME/contacts-api.git
git push -u origin main
```

Your `Dockerfile` must be at the root of `contacts_api/`.

---

## Step 2: Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com) → **New** → **PostgreSQL**
2. Name: `contacts-db`
3. Region: Frankfurt (EU) or closest to you
4. Plan: **Free**
5. Click **Create Database**
6. Copy the **Internal Database URL** — you'll need it in Step 4

---

## Step 3: Create Redis on Upstash (Better Free Tier)

Render's Redis free tier has no persistence. Use [Upstash](https://upstash.com) instead:

1. Go to [upstash.com](https://upstash.com) → **Create Database**
2. Type: **Redis**, Region: EU-West
3. Plan: **Free** (10,000 requests/day)
4. Copy the **Redis URL** (`rediss://...` with TLS)

---

## Step 4: Create Web Service on Render

1. **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `contacts-api`
   - **Root Directory:** `contacts_api` (if contacts_api is a subdirectory)
   - **Runtime:** Docker
   - **Plan:** Free

4. **Start Command:**
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   Render provides `$PORT` automatically.

---

## Step 5: Set Environment Variables on Render

In **Environment** → add these variables:

```bash
# Database (from Step 2 — Internal URL)
DATABASE_URL=postgresql+asyncpg://user:pass@host/contacts-db

# JWT
JWT_SECRET_KEY=generate-with-python-secrets-token-hex-32
EMAIL_TOKEN_SECRET=another-random-32-char-secret

# Redis (from Step 3 — Upstash URL)
REDIS_URL=rediss://default:password@region.upstash.io:6379

# Email — Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-16-char-app-password   ← see below
SMTP_FROM=your-gmail@gmail.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# App
FRONTEND_URL=https://your-contacts-api.onrender.com
DEBUG=false
```

**Generate secrets:**
```python
import secrets
print(secrets.token_hex(32))  # Run twice for JWT_SECRET_KEY and EMAIL_TOKEN_SECRET
```

---

## Step 6: Gmail App Password Setup

You need an App Password (not your regular Gmail password):

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (required)
3. Search for **App passwords**
4. Generate password for "Mail" → "Other device" → name it "contacts-api"
5. Copy the 16-character password (spaces don't matter)

This password only works for SMTP, not for your Gmail account login.

---

## Step 7: Verify Deployment

Render will build and deploy automatically. Check:

1. **Build logs** in Render dashboard — watch for migration output:
   ```
   INFO  [alembic.runtime.migration] Running upgrade  -> 001, create users
   INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, create contacts
   INFO:     Application startup complete.
   ```

2. **Test the deployed API:**
   ```bash
   curl https://your-app.onrender.com/api/v1/health
   # {"status": "ok"}
   ```

3. **Register and verify the email flow works** with real email.

---

## Step 8: GitHub Actions CI/CD

Generate the workflow file:
```bash
python standalone_examples/07_github_actions_explained.py > .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "add CI workflow"
git push
```

The workflow runs tests on every push. Render only deploys if the build succeeds (not the tests directly, but you can configure Render to not deploy on failed CI via GitHub deployment environments).

For strict CI → deploy gating, use **Render's GitHub integration**: Settings → Auto-Deploy → only when CI passes.

---

## S3 Alternative to Cloudinary

For production with high traffic, S3 is more cost-effective at scale:

```python
# Install: pip install aiobotocore

import aiobotocore.session

async def upload_to_s3(file_bytes: bytes, filename: str) -> str:
    session = aiobotocore.session.get_session()
    async with session.create_client(
        's3',
        region_name='eu-central-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    ) as client:
        await client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=f"avatars/{filename}",
            Body=file_bytes,
            ContentType='image/jpeg'
        )
        return f"https://{settings.S3_BUCKET}.s3.amazonaws.com/avatars/{filename}"
```

The rest of the app (`app/api/v1/users.py`) is identical — only the service function changes.

---

## Monitoring Free Options

- **Render logs** — available in dashboard, last 24h on free tier
- **Sentry** — free tier, error tracking (add `sentry-sdk[fastapi]` to requirements)
- **UptimeRobot** — free uptime monitoring, pings your `/health` endpoint every 5min (prevents Render free tier sleep)

---

## Production Hardening (Next Steps)

Things not covered in this module but worth knowing:

1. **Rate limiting per user** (not just per IP) — requires authenticated user ID as limiter key
2. **Password reset flow** — same email token pattern, different `purpose` claim
3. **Two-factor authentication** — TOTP (Google Authenticator) via `pyotp`
4. **Horizontal scaling** — multiple app instances, Redis-backed sessions
5. **CDN for static files** — Cloudflare in front of Render
