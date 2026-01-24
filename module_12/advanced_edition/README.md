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

### 2) OAuth2 Integration Example
File: `oauth2_integration_example.py`

Demonstrates:
- Google OAuth2 social login flow
- GitHub OAuth2 social login flow
- Authorization code exchange
- User information retrieval
- Frontend integration example (HTML/JavaScript)
- Complete setup instructions
- Type-safe OAuth2 implementations

Key Features:
- Token exchange (authorization code → access token)
- User info retrieval from providers
- Email handling (especially GitHub's quirks)
- Reusable OAuthUserInfo schema
- Production-ready error handling
- Comprehensive documentation

### 3) ML Registry App
Path: `ml_registry_app/`

Features:
- JWT authentication with refresh tokens
- **OAuth2 Social Login** (Google + GitHub)
- PostgreSQL + SQLAlchemy 2.0 (async)
- MinIO for file storage
- Redis integration
- Alembic migrations
- Comprehensive test suite
- Docker Compose stack

OAuth2 Integration in ML Registry:
- Endpoints: `/auth/oauth2/google/auth-url`, `/auth/oauth2/google/callback`
- Endpoints: `/auth/oauth2/github/auth-url`, `/auth/oauth2/github/callback`
- Automatic user creation on first OAuth2 login
- OAuth2 users seamlessly integrated with JWT auth
- Support for multiple OAuth2 providers per user

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

## RBAC Implementation Guide

**File:** `RBAC_PATTERNS.md`

Complete reference for Role-Based Access Control patterns including:
- Role hierarchy (user, reviewer, admin, superuser)
- Authorization patterns and best practices
- Security considerations
- Testing strategies
- How to extend with custom roles

The ML Registry application implements **Role + Ownership** RBAC where:
- Regular users manage their own models
- Reviewers have read-only access to all models
- Admins can modify any model
- Superusers have unrestricted access

## API Key Authentication

**Files:**
- `API_KEY_GUIDE.md` - Complete guide with examples
- `ml_registry_app/app/models/api_key.py` - APIKey model
- `ml_registry_app/app/auth/api_key_auth.py` - Authentication logic
- `ml_registry_app/app/api/v1/api_keys.py` - Management endpoints

Features:
- Generate secure API keys
- Scope-based permissions (resource:action model)
- Automatic expiration
- Rate limiting per key
- Key rotation
- Usage tracking
- FastAPI dependency injection support

Endpoints:
- `POST /api-keys` - Create new key
- `GET /api-keys` - List user's keys
- `GET /api-keys/{key_id}` - Get key details
- `PATCH /api-keys/{key_id}` - Update key
- `DELETE /api-keys/{key_id}` - Revoke key
- `POST /api-keys/{key_id}/rotate` - Rotate key

Usage in endpoints:
```python
@router.get("/models")
async def list_models(
    current_user: Annotated[User, Depends(get_api_key_user)]
):
    # Authenticated via API key
    pass
```

## Suggested Extensions (Optional)

These are good advanced exercises but are not implemented by default:
- Multi-factor authentication (MFA)
- Observability (tracing, metrics)
- Audit logging of all authorization events
- WebAuthn / Passkeys support
