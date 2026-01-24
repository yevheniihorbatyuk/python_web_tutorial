# Testing Guide for Module 12

## Overview

Comprehensive testing is essential for building reliable web applications. This guide covers testing strategies used in Module 12.

## Test Types

### 1. Unit Tests

Test individual functions in isolation.

**Example: Password hashing**
```python
def test_password_hashing():
    password = "MyPassword123!"
    hashed = get_password_hash(password)

    # Hashed password differs from input
    assert hashed != password

    # Verification works
    assert verify_password(password, hashed) == True

    # Wrong password fails
    assert verify_password("WrongPassword", hashed) == False
```

**Characteristics**:
- Fast execution
- No external dependencies
- Test single function
- Easy to debug

### 2. Integration Tests

Test multiple components working together.

**Example: User registration flow**
```python
@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Step 1: Register
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        }
    )
    assert register_response.status_code == 201

    # Step 2: Login with created user
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "SecurePass123!"}
    )
    assert login_response.status_code == 200

    # Step 3: Use token
    token = login_response.json()["access_token"]
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
```

**Characteristics**:
- Slower than unit tests
- Tests component interaction
- Closer to real scenarios
- More realistic

### 3. End-to-End Tests

Test complete user workflows.

**Example: Create and update model**
```python
@pytest.mark.asyncio
async def test_full_model_workflow(client: AsyncClient, auth_headers):
    # 1. Create model
    create_response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "My Model",
            "framework": "sklearn",
            "task_type": "classification",
            "accuracy": 0.90
        }
    )
    assert create_response.status_code == 201
    model_id = create_response.json()["id"]

    # 2. Retrieve model
    get_response = await client.get(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200

    # 3. Update model
    update_response = await client.put(
        f"/api/v1/models/{model_id}",
        headers=auth_headers,
        json={"accuracy": 0.95}
    )
    assert update_response.status_code == 200
    assert update_response.json()["accuracy"] == 0.95

    # 4. Delete model
    delete_response = await client.delete(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204

    # 5. Verify deletion
    get_response = await client.get(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404
```

---

## Test Fixtures

Fixtures provide reusable test setup.

### Database Fixture
```python
@pytest_asyncio.fixture
async def async_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()
```

### Session Fixture
```python
@pytest_asyncio.fixture
async def async_session(async_engine):
    """Create test database session"""
    AsyncTestSession = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with AsyncTestSession() as session:
        yield session
```

### Client Fixture
```python
@pytest_asyncio.fixture
async def client(async_session):
    """Create test client with DB override"""
    # Override get_db dependency
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()
```

### Authentication Fixture
```python
@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific File
```bash
pytest tests/test_auth.py -v
```

### Run Specific Test
```bash
pytest tests/test_auth.py::test_login_success -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Run Parallel
```bash
pytest tests/ -v -n auto
```

---

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_models.py           # Model CRUD tests
├── test_files.py            # File upload/download tests
└── test_integration.py      # End-to-end tests
```

### conftest.py Structure
```python
# Database fixtures
@pytest_asyncio.fixture
async def async_engine():
    ...

@pytest_asyncio.fixture
async def async_session(async_engine):
    ...

# Application fixtures
@pytest_asyncio.fixture
async def client(async_session):
    ...

# Data fixtures
@pytest_asyncio.fixture
async def test_user(async_session):
    ...

@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    ...
```

---

## Common Test Patterns

### 1. Success Path
```python
@pytest.mark.asyncio
async def test_operation_succeeds(client, auth_headers):
    response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={"name": "Model", "framework": "sklearn", ...}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Model"
```

### 2. Failure Path
```python
@pytest.mark.asyncio
async def test_invalid_input_fails(client, auth_headers):
    response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={"name": ""}  # Empty name
    )

    assert response.status_code == 422  # Validation error
```

### 3. Permission Check
```python
@pytest.mark.asyncio
async def test_unauthorized_access_fails(client):
    # No auth header
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 403
```

### 4. Data Consistency
```python
@pytest.mark.asyncio
async def test_data_integrity(client, auth_headers):
    # Create
    create_resp = await client.post(..., json=data)
    model_id = create_resp.json()["id"]

    # Update
    await client.put(f"/api/v1/models/{model_id}", ...)

    # Verify
    get_resp = await client.get(f"/api/v1/models/{model_id}")
    assert get_resp.json()["accuracy"] == 0.95
```

---

## Edge Cases to Test

### 1. Boundary Conditions
- Empty lists
- Single item
- Maximum items (pagination)
- Negative numbers
- Zero values

### 2. Invalid Input
- Wrong types
- Missing required fields
- Malformed JSON
- SQL injection attempts
- XSS attempts

### 3. Concurrency
- Multiple requests simultaneously
- Race conditions
- Concurrent writes to same resource

### 4. Error Handling
- 404 Not Found
- 403 Forbidden
- 400 Bad Request
- 500 Server Error
- Timeout scenarios

---

## Test Data Management

### Using Fixtures for Test Data
```python
@pytest_asyncio.fixture
async def sample_model(async_session, test_user):
    """Create sample model for testing"""
    model = MLModel(
        name="Sample Model",
        framework=MLFramework.SKLEARN,
        task_type=TaskType.CLASSIFICATION,
        accuracy=0.92,
        owner_id=test_user.id
    )
    async_session.add(model)
    await async_session.commit()
    await async_session.refresh(model)
    return model
```

### Using Factory Pattern (with factory-boy - optional)
```python
from factory import AsyncSQLAlchemyModelFactory

class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = async_session

    email = "user@example.com"
    username = "testuser"
    hashed_password = "hashed"

# Usage
test_user = await UserFactory.create()
```

---

## Async Testing

### Key Points for Async Tests

1. **Use @pytest.mark.asyncio**
   ```python
   @pytest.mark.asyncio
   async def test_something():
       result = await async_function()
       assert result == expected
   ```

2. **Async Fixtures**
   ```python
   @pytest_asyncio.fixture
   async def my_fixture():
       # Setup
       yield result
       # Teardown
   ```

3. **Async Context Managers**
   ```python
   async with AsyncClient(...) as client:
       response = await client.get("/")
   ```

---

## Continuous Integration

### GitHub Actions Example (Planned for Advanced Edition)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run tests
        run: pytest tests/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Coverage Goals

**Target**: 80%+ code coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Areas to prioritize:
- ✅ Business logic (models, schemas)
- ✅ API endpoints
- ✅ Authentication logic
- ✅ Error handling
- ⚠️ External integrations (mock them)

---

## Common Issues

### Test Hangs
**Problem**: Test never completes

**Solutions**:
- Check for missing `await`
- Use `pytest-asyncio-timeout`
- Add explicit timeout: `@pytest.mark.timeout(10)`

### Database Locked
**Problem**: "database is locked"

**Solutions**:
- Use SQLite `:memory:` for tests
- Or use PostgreSQL test database
- Ensure fixtures clean up properly

### Import Errors
**Problem**: "ModuleNotFoundError"

**Solutions**:
- Run from project root
- Install package in dev mode: `pip install -e .`
- Check PYTHONPATH

### Fixture Scope Issues
**Problem**: Data persists between tests

**Solutions**:
- Use `function` scope (default)
- Clear data after each test
- Use in-memory database

---

## Best Practices

✅ **Do's**:
- Test one thing per test
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external services
- Test error cases
- Keep tests independent
- Use fixtures for setup

❌ **Don'ts**:
- Skip async/await
- Hardcode test data
- Use real external APIs
- Test implementation details
- Make tests interdependent
- Copy-paste test code

---

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://testingpython.com/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

---

## Summary

Module 12 includes:
- ✅ 17+ comprehensive tests
- ✅ Unit and integration test examples
- ✅ Fixture patterns for async testing
- ✅ Coverage of all API endpoints
- ✅ Error case handling
- ✅ Documentation with examples

Use these patterns and practices in your own code to ensure reliability and maintainability.
