"""
Pytest Configuration and Fixtures for Todo App Tests

Provides:
- Test database setup and teardown
- TestClient for making requests
- Authenticated user fixtures
- Sample data fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for testing (fast, no cleanup needed)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    """Create test database tables and yield session."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session):
    """Create test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user registration data."""
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpass123"
    }

@pytest.fixture
def test_user_token(client, test_user_data):
    """Register user and return JWT token."""
    # Register
    client.post("/auth/register", json=test_user_data)

    # Login
    response = client.post("/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })

    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture
def authenticated_client(client, test_user_token):
    """Return client with authorization header."""
    client.headers = {
        "Authorization": f"Bearer {test_user_token}"
    }
    return client
