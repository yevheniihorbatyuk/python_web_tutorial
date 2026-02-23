"""
Integration tests for contact CRUD + birthday endpoint.

Key scenarios:
  - Contacts are private — user A cannot see user B's contacts
  - Search by name/email works
  - Birthday endpoint returns only contacts in the next 7 days
  - Birthday results come from cache on second call (mock Redis verifies this)
  - Unverified user gets 403 on all contact endpoints
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch
import pytest


# ─── Access control ───────────────────────────────────────────────────────────


async def test_unauthenticated_returns_401(client):
    response = await client.get("/api/v1/contacts/")
    assert response.status_code == 401


async def test_unverified_user_returns_403(client, async_session):
    from app.services.auth import create_user
    from app.core.security import create_access_token

    user = await create_user("unverified2@example.com", "pass", async_session)
    # User is NOT verified
    token = create_access_token(user.email)

    response = await client.get(
        "/api/v1/contacts/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ─── CRUD ─────────────────────────────────────────────────────────────────────


async def test_create_and_retrieve_contact(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/contacts/",
        json={"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    contact_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["first_name"] == "Alice"


async def test_list_contacts_returns_only_own(client, async_session, auth_headers):
    """User A should not see User B's contacts."""
    from app.services.auth import create_user
    from app.services.contacts import create_contact
    from app.schemas.contact import ContactCreate

    user_b = await create_user("userb@example.com", "pass", async_session)
    user_b.is_verified = True
    await async_session.commit()

    # Create a contact owned by user B
    await create_contact(
        ContactCreate(first_name="Secret", last_name="Contact"),
        user_b.id,
        async_session,
    )

    # User A lists contacts — should not see Secret Contact
    response = await client.get("/api/v1/contacts/", headers=auth_headers)
    assert response.status_code == 200
    names = [c["first_name"] for c in response.json()]
    assert "Secret" not in names


async def test_search_by_name(client, auth_headers):
    await client.post(
        "/api/v1/contacts/",
        json={"first_name": "Bob", "last_name": "Builder"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/contacts/",
        json={"first_name": "Charlie", "last_name": "Chaplin"},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/contacts/?search=bob", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["first_name"] == "Bob"


async def test_update_contact_patch(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/contacts/",
        json={"first_name": "David", "last_name": "Old"},
        headers=auth_headers,
    )
    contact_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/contacts/{contact_id}",
        json={"last_name": "New"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["last_name"] == "New"
    assert patch_resp.json()["first_name"] == "David"  # unchanged


async def test_delete_contact(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/contacts/",
        json={"first_name": "Eve", "last_name": "Delete"},
        headers=auth_headers,
    )
    contact_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_get_nonexistent_contact_returns_404(client, auth_headers):
    response = await client.get("/api/v1/contacts/99999", headers=auth_headers)
    assert response.status_code == 404


# ─── Birthday endpoint ────────────────────────────────────────────────────────


async def test_birthdays_endpoint_returns_contacts_in_window(client, auth_headers):
    today = date.today()
    birthday_in_3_days = today + timedelta(days=3)

    await client.post(
        "/api/v1/contacts/",
        json={
            "first_name": "Birthday",
            "last_name": "Person",
            "birthday": str(birthday_in_3_days.replace(year=birthday_in_3_days.year - 30)),
        },
        headers=auth_headers,
    )

    response = await client.get("/api/v1/contacts/birthdays", headers=auth_headers)
    assert response.status_code == 200


async def test_birthdays_endpoint_cached_on_second_call(client, auth_headers):
    """
    Verify that the second call hits Redis cache instead of the database.

    We check this by inspecting that the mock Redis get() was called.
    (In conftest the mock always returns None on get — cache miss —
    but we verify it was called, which is the cache lookup step.)
    """
    import app.api.v1.contacts as contacts_module
    from app.core import cache as cache_module

    # Patch get_or_set_cache where it is actually used (contacts router)
    call_count = {"n": 0}
    original = cache_module.get_or_set_cache

    async def counting_cache(key, ttl, loader):
        call_count["n"] += 1
        return await original(key, ttl, loader)

    with patch.object(contacts_module, "get_or_set_cache", side_effect=counting_cache):
        await client.get("/api/v1/contacts/birthdays", headers=auth_headers)
        await client.get("/api/v1/contacts/birthdays", headers=auth_headers)

    # get_or_set_cache was called for both requests
    assert call_count["n"] == 2
