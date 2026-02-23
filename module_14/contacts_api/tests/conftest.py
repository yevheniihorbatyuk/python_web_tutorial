"""
Test fixtures shared across unit and integration tests.

Key design decisions:
  - SQLite in-memory (aiosqlite) instead of PostgreSQL — no external process needed
  - dependency_overrides replaces get_db so every test gets an isolated session
  - Rate limiter storage is overridden with MemoryStorage to prevent counter leak
  - Email and Cloudinary are mocked — tests never hit external services
  - asyncio_mode = "auto" in pyproject.toml means no @pytest.mark.asyncio needed

Usage:
  pytest tests/ -v --cov=app --cov-report=term-missing
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch
from limits.storage import MemoryStorage

from app.main import app
from app.database import Base, get_db
from app.core import cache as cache_module
from app.core.rate_limit import limiter

# ─── Database fixture ─────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_session():
    """
    In-memory SQLite database created fresh for each test function.

    StaticPool keeps the same in-memory database alive for the duration
    of the test — without it each connection sees a new, empty database.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ─── HTTP client fixture ──────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(async_session):
    """
    AsyncClient wired to the FastAPI app via ASGITransport.

    No real HTTP server starts — requests go directly to ASGI handlers.
    The database dependency is replaced with the test SQLite session.
    Redis cache is mocked to avoid requiring a Redis container.
    """
    # Override DB
    app.dependency_overrides[get_db] = lambda: async_session

    # Override rate limiter storage with in-memory backend (no Redis needed)
    mem_storage = MemoryStorage()
    limiter._storage = mem_storage
    limiter._limiter.storage = mem_storage

    # Mock Redis so tests don't need a Redis server
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None      # always cache miss
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = 0      # nothing is blacklisted

    with patch.object(cache_module, "get_redis", return_value=mock_redis):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()


# ─── Helper: registered + verified user ──────────────────────────────────────

@pytest_asyncio.fixture
async def verified_user(client, async_session):
    """
    Create a user, bypass email verification, return credentials dict.

    Used by integration tests that need an authenticated user without
    going through the full email flow.
    """
    from app.services.auth import create_user as svc_create_user

    user = await svc_create_user("test@example.com", "password123", async_session)
    user.is_verified = True
    await async_session.commit()

    return {"email": "test@example.com", "password": "password123", "user": user}


@pytest_asyncio.fixture
async def auth_headers(client, verified_user):
    """Return Authorization headers for the verified test user."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": verified_user["email"], "password": verified_user["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
