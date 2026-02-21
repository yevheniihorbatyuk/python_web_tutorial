"""
Integration tests for user profile + avatar upload.

Avatar upload mocks Cloudinary — no real upload happens.
We verify that:
  - The returned URL is stored on the user object
  - Non-image files are rejected with 422
  - MIME validation catches misnamed files (e.g. .txt renamed to .jpg)
"""

import io
from unittest.mock import AsyncMock, patch
import pytest


async def test_get_me(client, auth_headers, verified_user):
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == verified_user["email"]
    assert response.json()["is_verified"] is True


async def test_upload_avatar_success(client, auth_headers):
    fake_jpeg = b"\xff\xd8\xff" + b"\x00" * 100  # JPEG magic bytes + padding

    with patch("app.api.v1.users.upload_avatar", new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = "https://res.cloudinary.com/demo/image/upload/v1/avatar.jpg"

        response = await client.post(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.jpg", io.BytesIO(fake_jpeg), "image/jpeg")},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["avatar_url"] == "https://res.cloudinary.com/demo/image/upload/v1/avatar.jpg"


async def test_upload_non_image_returns_422(client, auth_headers):
    """
    Cloudinary upload should be rejected before even reaching Cloudinary
    when the file is not an image.
    """
    # Plain text — no valid image magic bytes
    fake_text = b"this is not an image content"

    # Don't mock upload_avatar here — we want real MIME validation
    response = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("document.jpg", io.BytesIO(fake_text), "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_get_me_unauthenticated_returns_401(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
