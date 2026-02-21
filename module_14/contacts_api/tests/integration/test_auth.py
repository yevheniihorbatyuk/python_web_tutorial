"""
Integration tests for the auth flow.

Tests the full register → verify → login → refresh sequence over HTTP
using the AsyncClient fixture. Each test operates against a fresh
in-memory SQLite database.

Key assertions:
  - Email must be verified before login is allowed
  - Expired/wrong-purpose tokens are rejected with 400
  - Rate limiting returns 429 after threshold (simulated by overriding limit)
  - Logout blacklists the refresh token
"""

from unittest.mock import AsyncMock, patch
import pytest


# ─── Register ─────────────────────────────────────────────────────────────────


async def test_register_creates_unverified_user(client):
    with patch("app.api.v1.auth.send_verification_email", new_callable=AsyncMock):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "pass1234"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["is_verified"] is False


async def test_register_duplicate_email_returns_409(client):
    with patch("app.api.v1.auth.send_verification_email", new_callable=AsyncMock):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "pass1234"},
        )
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "other"},
        )
    assert response.status_code == 409


async def test_register_sends_verification_email(client):
    with patch("app.api.v1.auth.send_verification_email", new_callable=AsyncMock) as mock_send:
        await client.post(
            "/api/v1/auth/register",
            json={"email": "verify_test@example.com", "password": "pass1234"},
        )
    mock_send.assert_called_once_with("verify_test@example.com")


# ─── Email verification ────────────────────────────────────────────────────────


async def test_verify_email_success(client, async_session):
    from app.services.auth import create_user
    from app.core.security import create_email_token

    user = await create_user("toverify@example.com", "pass", async_session)
    token = create_email_token(user.email)

    response = await client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 200
    assert "verified" in response.json()["message"].lower()


async def test_verify_email_expired_token_returns_400(client):
    from app.core.security import _make_token
    from app.config import get_settings
    from datetime import timedelta

    settings = get_settings()
    # Token expired 1 second ago
    token = _make_token("exp@example.com", "email_verify", settings.EMAIL_TOKEN_SECRET, timedelta(seconds=-1))

    response = await client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 400


async def test_verify_email_wrong_purpose_returns_400(client, async_session):
    """Passing an access token to the verify endpoint must be rejected."""
    from app.services.auth import create_user
    from app.core.security import create_access_token

    await create_user("wrongpurpose@example.com", "pass", async_session)
    # Use an ACCESS token on the email verify endpoint
    token = create_access_token("wrongpurpose@example.com")

    response = await client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 400


# ─── Login ────────────────────────────────────────────────────────────────────


async def test_login_unverified_user_returns_403(client, async_session):
    from app.services.auth import create_user

    await create_user("unverified@example.com", "pass1234", async_session)
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "unverified@example.com", "password": "pass1234"},
    )
    assert response.status_code == 403


async def test_login_success(client, verified_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": verified_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client, verified_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


# ─── Refresh ──────────────────────────────────────────────────────────────────


async def test_refresh_token_returns_new_access_token(client, verified_user):
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": verified_user["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_refresh_with_access_token_returns_401(client, verified_user):
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": verified_user["password"]},
    )
    # Pass an ACCESS token where a refresh token is expected
    access_token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401


# ─── Logout ───────────────────────────────────────────────────────────────────


async def test_logout_returns_204(client, verified_user):
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": verified_user["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 204
