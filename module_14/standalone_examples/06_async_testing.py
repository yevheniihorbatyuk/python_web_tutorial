"""
06. Async Testing with pytest-asyncio
======================================

This file is both a tutorial and a runnable test file.
Run it with: pytest 06_async_testing.py -v

Topics covered:
- asyncio_mode = "auto" (no @pytest.mark.asyncio needed)
- AsyncClient + ASGITransport (same pattern as Module 12)
- Fixtures: function scope vs session scope
- Mocking async dependencies (AsyncMock)
- parametrize with async tests
- Testing HTTP status codes, headers, response bodies

Requirements:
    pip install pytest pytest-asyncio httpx fastapi aiosqlite sqlalchemy
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# ============================================================
# A MINIMAL APP TO TEST
# ============================================================
# (In contacts_api tests, this is replaced by importing from app/)

from fastapi import FastAPI
from pydantic import BaseModel

demo_app = FastAPI()

# Fake "database" for demo
_users: dict[int, dict] = {
    1: {"id": 1, "email": "alice@example.com", "is_verified": True},
    2: {"id": 2, "email": "bob@example.com", "is_verified": False},
}


async def get_fake_user(user_id: int) -> dict:
    """Simulate async database lookup."""
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def send_email_notification(email: str) -> None:
    """External service — we'll mock this in tests."""
    import asyncio
    await asyncio.sleep(0.5)  # Simulate real SMTP delay


@demo_app.get("/users/{user_id}")
async def get_user(user_id: int):
    return await get_fake_user(user_id)


@demo_app.post("/notify")
async def notify_user(user_id: int):
    user = await get_fake_user(user_id)
    await send_email_notification(user["email"])
    return {"message": f"Notification sent to {user['email']}"}


@demo_app.get("/items")
async def list_items(limit: int = 10):
    return [{"id": i, "name": f"item_{i}"} for i in range(1, limit + 1)]


# ============================================================
# FIXTURES
# ============================================================

@pytest_asyncio.fixture
async def client():
    """
    AsyncClient with ASGITransport.

    This sends requests directly to the ASGI app — no real HTTP server needed.
    Same pattern used in contacts_api/tests/conftest.py.

    Fixture scope: "function" (default) — each test gets a fresh client.
    """
    transport = ASGITransport(app=demo_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================
# SECTION 1: Basic async tests
# ============================================================

async def test_get_existing_user(client):
    response = await client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["is_verified"] is True


async def test_get_nonexistent_user(client):
    response = await client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_list_items_default_limit(client):
    response = await client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 10


async def test_list_items_custom_limit(client):
    response = await client.get("/items?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3


# ============================================================
# SECTION 2: Parametrize with async tests
# ============================================================

@pytest.mark.parametrize("user_id,expected_status,expected_verified", [
    (1, 200, True),
    (2, 200, False),
    (999, 404, None),
])
async def test_user_verification_status(client, user_id, expected_status, expected_verified):
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["is_verified"] == expected_verified


# ============================================================
# SECTION 3: Mocking async external services
# ============================================================

async def test_notify_user_sends_email(client):
    """
    Test that the notification endpoint calls the email service.
    We mock the email service so the test doesn't actually send email
    or wait 0.5 seconds.
    """
    with patch(
        "06_async_testing.send_email_notification",
        new_callable=AsyncMock
    ) as mock_email:
        response = await client.post("/notify?user_id=1")

        assert response.status_code == 200
        assert "alice@example.com" in response.json()["message"]

        # Verify the mock was called with the right argument
        mock_email.assert_called_once_with("alice@example.com")


async def test_notify_nonexistent_user_does_not_send_email(client):
    """Email should not be sent if user doesn't exist."""
    with patch(
        "06_async_testing.send_email_notification",
        new_callable=AsyncMock
    ) as mock_email:
        response = await client.post("/notify?user_id=999")

        assert response.status_code == 404
        mock_email.assert_not_called()


# ============================================================
# SECTION 4: Testing state isolation
# ============================================================
"""
Each test gets a fresh client fixture (function scope).
But our _users dict is module-level, so mutations persist.

In contacts_api, isolation is achieved differently:
- SQLite in-memory database created fresh for each test
- Database tables created and dropped in the fixture

This demonstrates why SQLite in-memory is better than a shared dict.
"""

async def test_users_are_not_modified_by_tests(client):
    """
    This test would fail if another test modified _users.
    In contacts_api, using SQLite in-memory prevents this issue entirely.
    """
    response = await client.get("/users/1")
    assert response.status_code == 200
    # Original data unchanged
    assert response.json()["email"] == "alice@example.com"


# ============================================================
# SECTION 5: Dependency override (contacts_api pattern)
# ============================================================
"""
In contacts_api, we override the database dependency to use SQLite
instead of PostgreSQL. Same technique works for any dependency.
"""

_override_active = False


async def original_dependency():
    return {"source": "original"}


@demo_app.get("/with-dependency")
async def endpoint_with_dep(data: dict = Depends(original_dependency)):
    return data


async def test_dependency_override(client):
    """Override a dependency for testing."""
    async def mock_dependency():
        return {"source": "test_override"}

    demo_app.dependency_overrides[original_dependency] = mock_dependency

    response = await client.get("/with-dependency")
    assert response.json()["source"] == "test_override"

    # Always clean up overrides after the test
    demo_app.dependency_overrides.clear()


# ============================================================
# SUMMARY
# ============================================================

"""
Key takeaways for contacts_api tests:

1. asyncio_mode = "auto" in pyproject.toml:
   No @pytest.mark.asyncio needed on any test function.

2. AsyncClient + ASGITransport:
   Tests the real ASGI app without a running server.
   Response objects are identical to real HTTP responses.

3. AsyncMock for external services:
   Replace email.send() and cloudinary.upload() with AsyncMock.
   Tests run in milliseconds, not seconds.

4. dependency_overrides for database:
   app.dependency_overrides[get_db] = lambda: test_session
   Swap PostgreSQL for SQLite in-memory.
   Always clear overrides after the test.

5. SQLite in-memory for isolation:
   Each test starts with a clean empty database.
   No test state bleeds into the next test.
"""
