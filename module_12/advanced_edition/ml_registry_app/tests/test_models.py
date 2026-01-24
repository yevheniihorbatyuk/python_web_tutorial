"""
Tests for ML model endpoints.

Tests CRUD operations, filtering, and pagination for ML models.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_model(client: AsyncClient, auth_headers):
    """Test creating an ML model."""
    response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "My First Model",
            "framework": "sklearn",
            "task_type": "classification",
            "description": "Test model",
            "accuracy": 0.95,
            "f1_score": 0.93
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My First Model"
    assert data["framework"] == "sklearn"
    assert data["lifecycle"] == "development"
    assert data["accuracy"] == 0.95
    assert "id" in data


@pytest.mark.asyncio
async def test_list_models(client: AsyncClient, auth_headers):
    """Test listing ML models."""
    # Create a model first
    await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Test Model",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )

    response = await client.get(
        "/api/v1/models/",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_models_scoped_to_owner(client: AsyncClient, auth_headers):
    """Test that regular users only see their own models."""
    await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Owner Model",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "username": "otheruser",
            "password": "otherpassword123"
        }
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "otheruser", "password": "otherpassword123"}
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    await client.post(
        "/api/v1/models/",
        headers=other_headers,
        json={
            "name": "Other Model",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )

    response = await client.get(
        "/api/v1/models/",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    names = {item["name"] for item in data}
    assert "Owner Model" in names
    assert "Other Model" not in names


@pytest.mark.asyncio
async def test_admin_sees_all_models(client: AsyncClient, auth_headers, admin_auth_headers):
    """Test that admin can see models from all users."""
    await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "User Model",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )

    response = await client.get(
        "/api/v1/models/",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    names = {item["name"] for item in data}
    assert "User Model" in names


@pytest.mark.asyncio
async def test_list_models_with_filter(client: AsyncClient, auth_headers):
    """Test filtering models by lifecycle."""
    # Create models with different lifecycles
    await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Dev Model",
            "framework": "sklearn",
            "task_type": "classification",
            "lifecycle": "development"
        }
    )

    # Filter by development lifecycle
    response = await client.get(
        "/api/v1/models/?lifecycle=development",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(m["lifecycle"] == "development" for m in data)


@pytest.mark.asyncio
async def test_get_model(client: AsyncClient, auth_headers):
    """Test getting a specific model."""
    # Create a model
    create_response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Test Model",
            "framework": "pytorch",
            "task_type": "regression"
        }
    )
    model_id = create_response.json()["id"]

    # Get the model
    response = await client.get(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == model_id
    assert data["name"] == "Test Model"


@pytest.mark.asyncio
async def test_get_nonexistent_model(client: AsyncClient, auth_headers):
    """Test getting a nonexistent model."""
    response = await client.get(
        "/api/v1/models/9999",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_model(client: AsyncClient, auth_headers):
    """Test updating a model."""
    # Create a model
    create_response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Original Name",
            "framework": "sklearn",
            "task_type": "classification",
            "accuracy": 0.85
        }
    )
    model_id = create_response.json()["id"]

    # Update the model
    response = await client.put(
        f"/api/v1/models/{model_id}",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "accuracy": 0.92
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["accuracy"] == 0.92


@pytest.mark.asyncio
async def test_delete_model(client: AsyncClient, auth_headers):
    """Test deleting a model."""
    # Create a model
    create_response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Model to Delete",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )
    model_id = create_response.json()["id"]

    # Delete the model
    response = await client.delete(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/models/{model_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_update_model_lifecycle(client: AsyncClient, auth_headers):
    """Test updating model lifecycle."""
    # Create a model
    create_response = await client.post(
        "/api/v1/models/",
        headers=auth_headers,
        json={
            "name": "Test Model",
            "framework": "sklearn",
            "task_type": "classification"
        }
    )
    model_id = create_response.json()["id"]

    # Update lifecycle
    response = await client.patch(
        f"/api/v1/models/{model_id}/lifecycle",
        headers=auth_headers,
        json="production"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["lifecycle"] == "production"


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, auth_headers):
    """Test pagination of models."""
    # Create multiple models
    for i in range(5):
        await client.post(
            "/api/v1/models/",
            headers=auth_headers,
            json={
                "name": f"Model {i}",
                "framework": "sklearn",
                "task_type": "classification"
            }
        )

    # Get with limit
    response = await client.get(
        "/api/v1/models/?limit=2",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
