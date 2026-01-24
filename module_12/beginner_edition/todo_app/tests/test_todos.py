"""
Todo CRUD Tests for Todo App

Tests:
- Create todos
- Read todos (list and individual)
- Update todos
- Delete todos
- Filter todos by completion status
- Authorization (users see only their todos)
"""

import pytest
from datetime import datetime, timezone

def test_create_todo(authenticated_client):
    """Test creating a new todo."""
    todo_data = {
        "title": "Learn FastAPI",
        "description": "Complete the tutorial",
    }

    response = authenticated_client.post("/todos/", json=todo_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Complete the tutorial"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data

def test_create_todo_minimal(authenticated_client):
    """Test creating todo with only required field."""
    response = authenticated_client.post("/todos/", json={
        "title": "Quick task"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Quick task"
    assert data["description"] is None

def test_create_todo_invalid_empty_title(authenticated_client):
    """Test creating todo with empty title fails."""
    response = authenticated_client.post("/todos/", json={
        "title": ""  # Empty title
    })

    assert response.status_code == 422  # Validation error

def test_list_todos(authenticated_client):
    """Test listing todos for authenticated user."""
    # Create a few todos
    authenticated_client.post("/todos/", json={"title": "Task 1"})
    authenticated_client.post("/todos/", json={"title": "Task 2"})
    authenticated_client.post("/todos/", json={"title": "Task 3"})

    response = authenticated_client.get("/todos/")

    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 3

def test_list_todos_empty(authenticated_client):
    """Test listing todos when none exist."""
    response = authenticated_client.get("/todos/")

    assert response.status_code == 200
    assert response.json() == []

def test_list_todos_filter_incomplete(authenticated_client):
    """Test filtering todos by incomplete status."""
    # Create mix of completed and incomplete todos
    authenticated_client.post("/todos/", json={"title": "Task 1"})
    response = authenticated_client.post("/todos/", json={"title": "Task 2"})
    todo_id = response.json()["id"]

    # Mark one as complete
    authenticated_client.patch(f"/todos/{todo_id}/toggle")

    # Get only incomplete todos
    response = authenticated_client.get("/todos/?completed=false")

    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "Task 1"

def test_list_todos_filter_complete(authenticated_client):
    """Test filtering todos by completed status."""
    # Create todos
    authenticated_client.post("/todos/", json={"title": "Task 1"})
    response = authenticated_client.post("/todos/", json={"title": "Task 2"})
    todo_id = response.json()["id"]

    # Mark one as complete
    authenticated_client.patch(f"/todos/{todo_id}/toggle")

    # Get only completed todos
    response = authenticated_client.get("/todos/?completed=true")

    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "Task 2"

def test_get_todo(authenticated_client):
    """Test getting a specific todo."""
    # Create a todo
    create_response = authenticated_client.post("/todos/", json={
        "title": "Specific task",
        "description": "Get this one"
    })
    todo_id = create_response.json()["id"]

    # Get the todo
    response = authenticated_client.get(f"/todos/{todo_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Specific task"

def test_get_nonexistent_todo(authenticated_client):
    """Test getting a todo that doesn't exist."""
    response = authenticated_client.get("/todos/999")

    assert response.status_code == 404

def test_update_todo(authenticated_client):
    """Test updating a todo."""
    # Create a todo
    create_response = authenticated_client.post("/todos/", json={
        "title": "Original title",
        "description": "Original description"
    })
    todo_id = create_response.json()["id"]

    # Update it
    response = authenticated_client.put(f"/todos/{todo_id}", json={
        "title": "Updated title",
        "description": "Updated description",
        "completed": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated description"
    assert data["completed"] is True

def test_update_todo_partial(authenticated_client):
    """Test partial update (update only some fields)."""
    # Create a todo
    create_response = authenticated_client.post("/todos/", json={
        "title": "Original",
        "description": "Description"
    })
    todo_id = create_response.json()["id"]

    # Update only title
    response = authenticated_client.put(f"/todos/{todo_id}", json={
        "title": "New title"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "Description"  # Unchanged

def test_toggle_todo_completion(authenticated_client):
    """Test toggling todo completion status."""
    # Create incomplete todo
    create_response = authenticated_client.post("/todos/", json={
        "title": "Task to toggle"
    })
    todo_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    # Toggle to complete
    response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # Toggle back to incomplete
    response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
    assert response.status_code == 200
    assert response.json()["completed"] is False

def test_delete_todo(authenticated_client):
    """Test deleting a todo."""
    # Create a todo
    create_response = authenticated_client.post("/todos/", json={
        "title": "To delete"
    })
    todo_id = create_response.json()["id"]

    # Delete it
    response = authenticated_client.delete(f"/todos/{todo_id}")

    assert response.status_code == 204  # No content

    # Verify it's gone
    response = authenticated_client.get(f"/todos/{todo_id}")
    assert response.status_code == 404

def test_delete_nonexistent_todo(authenticated_client):
    """Test deleting a todo that doesn't exist."""
    response = authenticated_client.delete("/todos/999")

    assert response.status_code == 404

def test_user_sees_only_own_todos(client, test_user_data):
    """Test that users can only see their own todos."""
    # Register and login as user 1
    client.post("/auth/register", json=test_user_data)
    response = client.post("/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    token1 = response.json()["access_token"]

    # Create todo as user 1
    client.headers = {"Authorization": f"Bearer {token1}"}
    client.post("/todos/", json={"title": "User 1 task"})

    # Register and login as user 2
    user2_data = {
        "email": "user2@example.com",
        "username": "user2",
        "password": "password123"
    }
    client.headers = {}
    client.post("/auth/register", json=user2_data)
    response = client.post("/auth/login", data={
        "username": user2_data["username"],
        "password": user2_data["password"]
    })
    token2 = response.json()["access_token"]

    # Create todo as user 2
    client.headers = {"Authorization": f"Bearer {token2}"}
    client.post("/todos/", json={"title": "User 2 task"})

    # User 2 should only see their own todo
    response = client.get("/todos/")
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "User 2 task"

    # User 1 should only see their own todo
    client.headers = {"Authorization": f"Bearer {token1}"}
    response = client.get("/todos/")
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "User 1 task"
