"""
Contacts CRUD endpoints + birthday lookup.

  GET    /contacts               → list (search, pagination)
  POST   /contacts               → create
  GET    /contacts/birthdays     → next 7 days (cached in Redis)
  GET    /contacts/{id}          → single contact
  PUT    /contacts/{id}          → full replace
  PATCH  /contacts/{id}          → partial update
  DELETE /contacts/{id}          → delete

Note: /contacts/birthdays must be declared BEFORE /contacts/{id}
so FastAPI doesn't treat "birthdays" as an integer path parameter.
"""

from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.core.dependencies import require_verified
from app.core.cache import get_or_set_cache, invalidate_cache
from app.services.contacts import (
    get_contact,
    list_contacts,
    create_contact,
    update_contact,
    delete_contact,
    get_upcoming_birthdays,
)

router = APIRouter()

_BIRTHDAY_CACHE_TTL = 3600  # 1 hour


def _birthday_cache_key(user_id: int) -> str:
    """Cache key includes today's date so it auto-expires at midnight."""
    return f"birthdays:{user_id}:{date.today()}"


@router.get("/", response_model=List[ContactResponse])
async def list_contacts_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
    search: Optional[str] = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[ContactResponse]:
    return await list_contacts(current_user.id, db, search=search, skip=skip, limit=limit)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_endpoint(
    body: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> ContactResponse:
    contact = await create_contact(body, current_user.id, db)
    # Invalidate birthday cache since a new contact (possibly with birthday) was added
    await invalidate_cache(_birthday_cache_key(current_user.id))
    return contact


@router.get("/birthdays", response_model=List[dict])
async def upcoming_birthdays(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> List[dict]:
    """
    Return contacts with birthdays in the next 7 days.

    Result is cached per user per day in Redis (TTL = 1 hour).
    Second call within the same hour does not hit the database.
    """
    key = _birthday_cache_key(current_user.id)
    return await get_or_set_cache(
        key,
        _BIRTHDAY_CACHE_TTL,
        lambda: get_upcoming_birthdays(current_user.id, db),
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_endpoint(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> ContactResponse:
    contact = await get_contact(contact_id, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def replace_contact(
    contact_id: int,
    body: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> ContactResponse:
    contact = await get_contact(contact_id, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    updated = await update_contact(contact, ContactUpdate(**body.model_dump()), db)
    await invalidate_cache(_birthday_cache_key(current_user.id))
    return updated


@router.patch("/{contact_id}", response_model=ContactResponse)
async def patch_contact(
    contact_id: int,
    body: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> ContactResponse:
    contact = await get_contact(contact_id, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    updated = await update_contact(contact, body, db)
    await invalidate_cache(_birthday_cache_key(current_user.id))
    return updated


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_endpoint(
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> None:
    contact = await get_contact(contact_id, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    await delete_contact(contact, db)
    await invalidate_cache(_birthday_cache_key(current_user.id))
