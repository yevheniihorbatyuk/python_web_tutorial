# Architecture — Contacts API

## System Overview

```mermaid
graph TB
    Client["Client\n(Browser / curl / Postman)"]

    subgraph Docker Compose — Development
        API["FastAPI app\n:8000"]
        PG[("PostgreSQL 16\ncontacts_db")]
        Redis[("Redis 7\ncache + rate limits")]
        MailHog["MailHog\n:8025 web UI\n:1025 SMTP"]
    end

    Cloudinary["Cloudinary CDN\navatar storage"]
    Gmail["Gmail SMTP\nproduction email"]
    Render["Render.com\nproduction host"]
    GH["GitHub Actions\nCI/CD"]

    Client -->|"REST + JSON"| API
    API -->|"SQLAlchemy async"| PG
    API -->|"redis-py async"| Redis
    API -->|"FastAPI-Mail\n(dev)"| MailHog
    API -->|"cloudinary SDK"| Cloudinary
    MailHog -.->|"prod: replaced by"| Gmail
    GH -->|"tests pass → auto-deploy"| Render
```

## Application Structure

```
app/
├── main.py          ← app factory, routers, CORS, rate limit error handler
├── config.py        ← Settings(BaseSettings) — all env vars in one place
├── database.py      ← async engine, AsyncSession, get_db dependency
│
├── models/          ← SQLAlchemy ORM models (tables)
│   ├── user.py      ← User: email, password_hash, is_verified, avatar_url
│   └── contact.py   ← Contact: names, phone, email, birthday, owner FK
│
├── schemas/         ← Pydantic models (request/response validation)
│   ├── user.py
│   ├── contact.py
│   └── token.py
│
├── core/            ← cross-cutting concerns
│   ├── security.py      ← JWT: access token, refresh token, email token
│   ├── dependencies.py  ← get_current_user, require_verified
│   ├── rate_limit.py    ← SlowAPI limiter
│   └── cache.py         ← Redis get_or_set helper
│
├── services/        ← business logic (no HTTP, no DB sessions — pure functions + db calls)
│   ├── auth.py          ← get_user_by_email, create_user
│   ├── contacts.py      ← CRUD + birthday query
│   ├── email.py         ← send_verification_email
│   └── cloudinary_service.py ← upload_avatar
│
└── api/v1/          ← HTTP endpoints (thin layer: validate → call service → return)
    ├── auth.py
    ├── contacts.py
    └── users.py
```

## Data Model

```mermaid
erDiagram
    User {
        int id PK
        string email UK
        string hashed_password
        bool is_verified
        string avatar_url
        datetime created_at
        datetime updated_at
    }

    Contact {
        int id PK
        string first_name
        string last_name
        string email
        string phone
        date birthday
        text notes
        int owner_id FK
        datetime created_at
        datetime updated_at
    }

    User ||--o{ Contact : "owns"
```

## Email Verification Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Mail as Email Service

    C->>API: POST /api/v1/auth/register {email, password}
    API->>DB: INSERT user (is_verified=False)
    API->>API: create_email_token(sub=email, purpose="email_verify", exp=+24h)
    API->>Mail: send email with link
    API-->>C: 201 UserResponse (email, is_verified=false, ...)

    Note over C,Mail: User clicks link in email

    C->>API: GET /api/v1/auth/verify/{token}
    API->>API: decode JWT<br/>check purpose == "email_verify"<br/>check not expired
    alt Token valid
        API->>DB: UPDATE is_verified=True
        API-->>C: 200 "Email verified"
    else Expired or wrong purpose
        API-->>C: 400 "Invalid or expired token"
    end

    C->>API: POST /api/v1/auth/login (OAuth2 form-data)
    alt Not verified
        API-->>C: 403 "Verify your email first"
    else Verified
        API-->>C: 200 {access_token, refresh_token}
    end
```

## Birthday Caching Flow

```mermaid
flowchart TD
    Req["GET /api/v1/contacts/birthdays"] --> Auth["Validate JWT"]
    Auth --> Key["cache key:\nbirthdays:{user_id}:{today}"]
    Key --> Check{Redis HIT?}
    Check -->|"HIT (within 1h)"| Cached["Return cached JSON\n(no DB query)"]
    Check -->|"MISS"| DB["SELECT contacts\nWHERE birthday in next 7 days\nAND owner_id = user_id"]
    DB --> Store["Redis SET key\nTTL = 1 hour"]
    Store --> Fresh["Return fresh list"]
```

**Why include today's date in the cache key?**
Because `birthdays:{user_id}` would return stale data across midnight. `birthdays:{user_id}:{2025-01-24}` automatically becomes a cache miss at midnight when the date changes.

## Rate Limiting

```
POST /api/v1/auth/register  → 5 requests/minute per IP
POST /api/v1/auth/login     → 10 requests/minute per IP

429 Too Many Requests response on violation.
Rate limit counters stored in Redis — works across multiple app instances.
```

## JWT Token Types

Three token types, all signed with Jose (same library as Module 12):

| Token | Secret | Payload | TTL |
|-------|--------|---------|-----|
| Access | `JWT_SECRET_KEY` | `{sub: email, purpose: "access"}` | 30 min |
| Refresh | `JWT_REFRESH_SECRET` | `{sub: email, purpose: "refresh"}` | 7 days |
| Email | `EMAIL_TOKEN_SECRET` | `{sub: email, purpose: "email_verify"}` | 24h |

The `purpose` claim on email tokens prevents an access token from being used as a verification token even if intercepted.

## Services: Why Direct SQLAlchemy (No Repository Pattern)

Services call SQLAlchemy's `AsyncSession` directly. There is no `ContactRepository` class wrapping the queries.

A repository pattern adds a useful abstraction when:
- You need to swap the data source (e.g., DB → in-memory for tests)
- Multiple services need the same complex query

In this app, tests use `dependency_overrides` to swap the DB session (SQLite instead of PostgreSQL), which achieves data source isolation without a repository class. Adding a repository layer here would be an abstraction looking for a problem to solve.

## What's in Redis

| Key pattern | Value | TTL | Purpose |
|-------------|-------|-----|---------|
| `birthdays:{user_id}:{date}` | JSON list | 1h | Birthday query cache |
| `slowapi:{ip}:{endpoint}` | request count | 1min | Rate limiting |
| `blacklist:{refresh_token}` | 1 | token expiry | Logout invalidation |
