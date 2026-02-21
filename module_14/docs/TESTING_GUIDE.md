# Testing Guide

## Test Structure

```
tests/
├── conftest.py              ← fixtures shared across all tests
├── unit/                    ← fast, no external services
│   ├── test_security.py     ← JWT functions, password hashing
│   ├── test_contact_service.py  ← birthday date logic
│   └── test_email_service.py    ← mock email sending
└── integration/             ← full HTTP request/response
    ├── test_auth.py         ← register → verify → login flow
    ├── test_contacts.py     ← CRUD + birthday + caching
    └── test_users.py        ← profile + avatar upload
```

## Unit vs Integration Tests

| | Unit | Integration |
|--|------|-------------|
| Database | SQLite in-memory | SQLite in-memory |
| HTTP | No | Yes (AsyncClient) |
| Email | No (pure functions) | Mocked (AsyncMock) |
| Cloudinary | No | Mocked (AsyncMock) |
| Rate limiter | Disabled | Disabled |
| Speed | < 2s | < 15s |

**Unit tests** test individual functions in isolation. No HTTP, no database required for the simplest ones.

**Integration tests** send real HTTP requests to the app and check responses. External services (email, Cloudinary) are mocked at the service layer.

## Running Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Only unit tests (fastest)
pytest tests/unit/ -v

# Only integration tests
pytest tests/integration/ -v

# Specific file
pytest tests/integration/test_auth.py -v

# Specific test
pytest tests/integration/test_auth.py::test_login_unverified_returns_403 -v
```

## conftest.py Pattern

Same pattern as Module 12 advanced edition, extended with email and Cloudinary mocks:

```python
# SQLite in-memory (no PostgreSQL needed for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(async_session, mock_email_service):
    app.dependency_overrides[get_db] = lambda: async_session
    # Disable rate limiting in tests
    app.state.limiter._storage = MemoryStorage()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def mock_email_service(monkeypatch):
    """Prevent real emails from being sent in tests."""
    mock = AsyncMock()
    monkeypatch.setattr("app.services.email.send_verification_email", mock)
    return mock
```

## Mocking External Services

### Email (FastAPI-Mail)

```python
# Mock at service layer, not SMTP socket level
@pytest.fixture
def mock_send_email(monkeypatch):
    mock = AsyncMock(return_value=None)
    monkeypatch.setattr("app.api.v1.auth.send_verification_email", mock)
    return mock

# Test: verify email was called
async def test_register_sends_email(client, mock_send_email):
    await client.post("/api/v1/auth/register", json={...})
    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args
    assert "alice@example.com" in str(call_args)
```

### Cloudinary

```python
@pytest.fixture
def mock_cloudinary(monkeypatch):
    mock = AsyncMock(return_value="https://res.cloudinary.com/test/avatar.jpg")
    monkeypatch.setattr("app.services.cloudinary_service.upload_avatar", mock)
    return mock
```

## Coverage Report

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Sample output:
```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
app/core/security.py             45      2    96%   78-79
app/services/contacts.py         62      8    87%   102-109
app/api/v1/auth.py               55      4    93%   45-48
-----------------------------------------------------------
TOTAL                           312     28    91%
```

**Lines 78-79 in security.py:** The `except JWTError` branch when signature is invalid. Hard to trigger naturally — covered by unit tests that pass a tampered token.

**What 80% means:** Every function's happy path is tested. Error branches (network failures, disk full, external API down) may not all be covered, which is acceptable at this stage. Lines 102-109 in contacts.py are the birthday year-boundary edge case — covered in `test_contact_service.py`.

## pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"   # no @pytest.mark.asyncio needed on each test
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "alembic/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

`asyncio_mode = "auto"` is from `pytest-asyncio` 0.21+. It means any `async def test_...()` function is automatically treated as an async test.

## Unit Test Examples

### test_security.py — JWT purpose claim

```python
def test_email_token_wrong_purpose_rejected():
    """An access token must not be usable as a verification token."""
    access_token = create_access_token(user_id=1)
    with pytest.raises(HTTPException) as exc_info:
        decode_email_token(access_token)
    assert exc_info.value.status_code == 400
```

### test_contact_service.py — Birthday year-boundary

```python
@pytest.mark.parametrize("birthday,today,expect_in_result", [
    (date(1990, 1, 3), date(2025, 12, 30), True),  # Jan 3 is within 7 days of Dec 30
    (date(1990, 1, 8), date(2025, 12, 30), False), # Jan 8 is 9 days away
    (date(1990, 12, 30), date(2025, 12, 30), True), # today's birthday
])
def test_birthday_year_boundary(birthday, today, expect_in_result):
    result = is_birthday_within_days(birthday, today, days=7)
    assert result == expect_in_result
```

## Integration Test Example

```python
async def test_full_auth_flow(client, mock_send_email):
    # 1. Register
    resp = await client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "Password123!"
    })
    assert resp.status_code == 201

    # 2. Login without verification → 403
    resp = await client.post("/api/v1/auth/login", json={
        "email": "alice@example.com",
        "password": "Password123!"
    })
    assert resp.status_code == 403

    # 3. Verify email
    token = create_email_token(email="alice@example.com")
    resp = await client.get(f"/api/v1/auth/verify/{token}")
    assert resp.status_code == 200

    # 4. Login → success
    resp = await client.post("/api/v1/auth/login", json={
        "email": "alice@example.com",
        "password": "Password123!"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
```

## CI vs Local Testing

| | Local | CI (GitHub Actions) |
|--|-------|---------------------|
| Unit tests | SQLite | SQLite |
| Integration tests | SQLite | PostgreSQL service container |
| Email | Mocked | Mocked |
| Cloudinary | Mocked | Mocked |
| Redis | Mocked / disabled | Redis service container |

Why PostgreSQL in CI for integration tests? SQLite and PostgreSQL have different behavior for:
- `EXTRACT()` on dates (birthday query)
- JSON field support
- Case sensitivity in LIKE queries

Local tests use SQLite for speed. CI catches PostgreSQL-specific issues before deployment.
