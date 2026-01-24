"""
Authentication Tests for Todo App

Tests:
- User registration with valid/invalid data
- User login with correct/incorrect credentials
- JWT token generation and validation
- Duplicate email/username prevention
"""

import pytest
from fastapi.testclient import TestClient

def test_register_user_success(client, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "password" not in data  # Password should never be in response
    assert "id" in data
    assert "created_at" in data

def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails."""
    # Register first user
    client.post("/auth/register", json=test_user_data)

    # Try to register with same email
    duplicate = test_user_data.copy()
    duplicate["username"] = "different_username"
    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_register_duplicate_username(client, test_user_data):
    """Test registration with duplicate username fails."""
    # Register first user
    client.post("/auth/register", json=test_user_data)

    # Try to register with same username
    duplicate = test_user_data.copy()
    duplicate["email"] = "different@example.com"
    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()

def test_register_invalid_email(client):
    """Test registration with invalid email fails."""
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "username": "testuser",
        "password": "testpass123"
    })

    assert response.status_code == 422  # Validation error

def test_register_short_password(client):
    """Test registration with password too short fails."""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "short"  # Less than 8 characters
    })

    assert response.status_code == 422

def test_login_success(client, test_user_data):
    """Test successful login returns JWT token."""
    # Register user
    client.post("/auth/register", json=test_user_data)

    # Login
    response = client.post("/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password fails."""
    # Register user
    client.post("/auth/register", json=test_user_data)

    # Try login with wrong password
    response = client.post("/auth/login", data={
        "username": test_user_data["username"],
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    response = client.post("/auth/login", data={
        "username": "doesnotexist",
        "password": "anypassword"
    })

    assert response.status_code == 401

def test_get_current_user(client, test_user_data, test_user_token):
    """Test getting current authenticated user info."""
    client.headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]

def test_unauthorized_without_token(client):
    """Test that protected route fails without token."""
    response = client.get("/me")

    assert response.status_code == 403  # Forbidden (missing auth)

def test_unauthorized_with_invalid_token(client):
    """Test that protected route fails with invalid token."""
    client.headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/me")

    assert response.status_code == 401  # Unauthorized (invalid token)
