"""
Test Examples - FastAPI Testing Basics

Learn how to test FastAPI applications properly:

✅ Unit testing - Test individual functions
✅ Route testing - Test endpoints with TestClient
✅ Database testing - Test ORM operations
✅ Authentication testing - Test login and token flows
✅ Error handling - Test what happens when things go wrong
✅ Fixtures - Setup and teardown test data

WHY TESTING MATTERS:
    - Catch bugs before users see them
    - Ensure your API works as expected
    - Make refactoring safer
    - Document how your API should work
    - Build confidence in your code

RUN THESE TESTS:
    pytest test_examples.py -v          # Run all tests with details
    pytest test_examples.py -v --cov    # Show code coverage
    pytest test_examples.py::test_register_user  # Run one specific test

PATTERNS TO LEARN:
    1. Using TestClient to test HTTP routes
    2. Using pytest fixtures for setup/teardown
    3. Testing with a separate test database
    4. Testing authentication flows
    5. Testing error cases (validation, not found, unauthorized)
    6. Using mocks for external dependencies
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import sys
import os

# ============================================================================
# EXAMPLE 1: SIMPLE FUNCTION TESTING
# ============================================================================

def greet(name: str) -> str:
    """Simple function to demonstrate unit testing."""
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"

def test_greet_with_name():
    """Test that greet works with a name."""
    result = greet("Alice")
    assert result == "Hello, Alice!"
    # 'assert' checks if condition is True
    # If False, the test fails

def test_greet_with_empty_name():
    """Test that greet raises error with empty name."""
    with pytest.raises(ValueError):
        greet("")
    # 'pytest.raises' checks that an exception is raised

# ============================================================================
# EXAMPLE 2: TESTING FASTAPI ROUTES
# ============================================================================

# Create a minimal FastAPI app for testing
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

app = FastAPI()

# Route 1: Simple GET
@app.get("/items/")
def list_items():
    """Get all items."""
    return [
        {"id": 1, "name": "Apple", "price": 1.00},
        {"id": 2, "name": "Banana", "price": 0.50}
    ]

# Route 2: GET with path parameter
@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Get an item by ID."""
    items = {
        1: {"id": 1, "name": "Apple", "price": 1.00},
        2: {"id": 2, "name": "Banana", "price": 0.50}
    }
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

# Route 3: POST with request body
@app.post("/items/", status_code=201)
def create_item(item: Item):
    """Create a new item."""
    return {"id": 3, **item.dict()}

# ============================================================================
# FIXTURES - Setup for Tests
# ============================================================================

@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.

    The TestClient:
    - Makes HTTP requests to your app
    - Does NOT start a server
    - Runs tests in-memory (fast!)

    Fixtures are run BEFORE each test that requests them.
    """
    return TestClient(app)

@pytest.fixture
def sample_data():
    """
    Fixture that provides sample data for tests.

    This is called before tests that need it.
    """
    return {
        "items": [
            {"id": 1, "name": "Apple", "price": 1.00},
            {"id": 2, "name": "Banana", "price": 0.50}
        ]
    }

# ============================================================================
# ROUTE TESTING EXAMPLES
# ============================================================================

def test_list_items(client):
    """Test GET /items/ returns all items."""
    response = client.get("/items/")

    # Check HTTP status code is 200 OK
    assert response.status_code == 200

    # Check response contains expected data
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Apple"
    assert data[1]["name"] == "Banana"

def test_get_item_success(client):
    """Test GET /items/{id} returns specific item."""
    response = client.get("/items/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Apple"
    assert data["price"] == 1.00

def test_get_item_not_found(client):
    """Test GET /items/{id} with invalid ID returns 404."""
    response = client.get("/items/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_create_item(client):
    """Test POST /items/ creates new item."""
    new_item = {"name": "Orange", "price": 0.75}
    response = client.post("/items/", json=new_item)

    # Check status code is 201 Created
    assert response.status_code == 201

    # Check response contains the created item
    data = response.json()
    assert data["name"] == "Orange"
    assert data["price"] == 0.75
    assert "id" in data

def test_create_item_invalid_data(client):
    """Test POST /items/ with invalid data raises error."""
    # Missing required 'price' field
    invalid_item = {"name": "Orange"}
    response = client.post("/items/", json=invalid_item)

    # Should return 422 Unprocessable Entity (validation error)
    assert response.status_code == 422

# ============================================================================
# EXAMPLE 3: TESTING WITH DATABASE
# ============================================================================

# For this example, we'll create a simple in-memory database for testing

users_db = {}  # Simulated database

class User:
    """Simple user class for testing."""
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

def find_user(user_id: int):
    """Find user by ID."""
    if user_id not in users_db:
        raise ValueError(f"User {user_id} not found")
    return users_db[user_id]

def create_user(name: str, email: str) -> User:
    """Create a user."""
    user_id = len(users_db) + 1
    user = User(user_id, name, email)
    users_db[user_id] = user
    return user

# Testing database operations

@pytest.fixture
def clean_db():
    """
    Fixture that clears the test database before each test.

    This ensures tests are ISOLATED - each test starts with a clean state.
    Without this, test results would depend on test order!
    """
    global users_db
    users_db.clear()
    yield  # Run the test here
    users_db.clear()  # Clean up after test

def test_create_user(clean_db):
    """Test creating a user."""
    user = create_user("Alice", "alice@example.com")

    assert user.id == 1
    assert user.name == "Alice"
    assert user.email == "alice@example.com"

def test_find_user(clean_db):
    """Test finding a user."""
    created_user = create_user("Bob", "bob@example.com")

    found_user = find_user(created_user.id)
    assert found_user.name == "Bob"
    assert found_user.email == "bob@example.com"

def test_find_nonexistent_user(clean_db):
    """Test finding user that doesn't exist."""
    with pytest.raises(ValueError, match="not found"):
        find_user(999)

# ============================================================================
# EXAMPLE 4: TESTING AUTHENTICATION
# ============================================================================

# Simplified authentication for testing

def hash_password(password: str) -> str:
    """Simple hash function (in production, use bcrypt!)."""
    # This is for testing only!
    return f"hashed_{password}"

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password."""
    return hash_password(plain) == hashed

class UserWithPassword:
    """User with password."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.hashed_password = hash_password(password)

def test_password_hashing():
    """Test that passwords are hashed correctly."""
    password = "secret123"
    hashed = hash_password(password)

    # Hashed password should not be the same as plain
    assert hashed != password
    assert hashed.startswith("hashed_")

def test_password_verification():
    """Test password verification."""
    user = UserWithPassword("alice", "mysecretpass")

    # Correct password should verify
    assert verify_password("mysecretpass", user.hashed_password) == True

    # Wrong password should not verify
    assert verify_password("wrongpass", user.hashed_password) == False

# ============================================================================
# EXAMPLE 5: TESTING WITH MOCKS
# ============================================================================

from unittest.mock import Mock, patch

def send_email(email: str, subject: str) -> bool:
    """Send an email (normally calls external service)."""
    # In production, this would call an email service
    # For testing, we'll mock it
    return True

def register_user(name: str, email: str) -> dict:
    """Register user and send welcome email."""
    # In production:
    # 1. Create user in database
    # 2. Send welcome email
    # 3. Return user

    user = {"id": 1, "name": name, "email": email}

    if send_email(email, "Welcome"):
        return user
    else:
        raise Exception("Failed to send email")

def test_register_user_with_mock():
    """Test user registration by mocking the email sending."""
    # MOCK: Replace send_email with a fake version
    with patch("test_examples.send_email") as mock_send_email:
        # Configure the mock to return True
        mock_send_email.return_value = True

        # Call the function
        user = register_user("Alice", "alice@example.com")

        # Verify the function worked
        assert user["name"] == "Alice"

        # Verify send_email was called with correct arguments
        mock_send_email.assert_called_once_with(
            "alice@example.com",
            "Welcome"
        )

def test_register_user_email_fails():
    """Test registration when email sending fails."""
    with patch("test_examples.send_email") as mock_send_email:
        # Configure mock to return False (failure)
        mock_send_email.return_value = False

        # Call should raise an exception
        with pytest.raises(Exception, match="Failed to send email"):
            register_user("Bob", "bob@example.com")

# ============================================================================
# EXAMPLE 6: PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("input_val,expected", [
    ("Alice", "Hello, Alice!"),
    ("Bob", "Hello, Bob!"),
    ("Charlie", "Hello, Charlie!"),
])
def test_greet_multiple_names(input_val, expected):
    """
    Test the same function with multiple inputs.

    This runs the test 3 times with different data.
    Much better than writing 3 separate tests!
    """
    assert greet(input_val) == expected

# ============================================================================
# BEST PRACTICES SUMMARY
# ============================================================================

"""
KEY TESTING PRINCIPLES:

1. ISOLATED TESTS
   - Each test should be independent
   - Use fixtures to setup/cleanup
   - Don't share state between tests

2. CLEAR NAMES
   - test_<what>_<expected_result>
   - Examples:
       test_create_user_success()
       test_create_user_duplicate_email_fails()

3. ARRANGE-ACT-ASSERT (AAA Pattern)
   def test_something():
       # ARRANGE: Setup test data
       user = User("Alice", "alice@example.com")

       # ACT: Do something
       result = user.is_admin()

       # ASSERT: Check result
       assert result == False

4. TEST THE HAPPY PATH AND ERROR CASES
   - Happy path: Everything works perfectly
   - Error cases: What if X goes wrong?
     - Missing data
     - Invalid data
     - Unauthorized access
     - Not found
     - Server errors

5. USE ASSERTIONS CORRECTLY
   assert value == expected        # Check equality
   assert value is not None        # Check not None
   assert len(list) == 3           # Check length
   assert "text" in string         # Check contains
   assert isinstance(obj, Class)   # Check type

6. MOCKING EXTERNAL DEPENDENCIES
   - Database connections
   - API calls
   - Email services
   - File system operations

   Reason: Tests should be:
   - FAST (don't need real database)
   - RELIABLE (don't depend on external services)
   - ISOLATED (don't need to setup external services)

7. COVERAGE TARGETS
   - 80%+ is good for most projects
   - 100% is not always necessary
   - Focus on critical paths

8. TEST ORGANIZATION
   conftest.py - Shared fixtures
   test_auth.py - Authentication tests
   test_routes.py - Route tests
   test_models.py - Model/database tests

NEXT STEPS:
   1. Look at actual test files in examples/
   2. Try writing tests for your own code
   3. Aim for >80% code coverage
   4. Use pytest-cov: pytest --cov=app tests/
"""

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         FastAPI TESTING EXAMPLES                       ║
    ╚════════════════════════════════════════════════════════╝

    Run tests with:
        pytest test_examples.py -v

    Run specific test:
        pytest test_examples.py::test_greet_with_name -v

    Show coverage:
        pytest test_examples.py --cov

    Watch mode (auto-rerun on file change):
        pytest-watch test_examples.py

    All tests in this file are RUNNABLE - they teach by example!
    Each test shows a different testing pattern.
    """)
