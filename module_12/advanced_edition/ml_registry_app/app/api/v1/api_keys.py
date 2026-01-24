"""
API Key management endpoints.

Provides endpoints for users to:
- Create new API keys
- List their API keys
- Update API key properties
- Revoke (deactivate) API keys
- Rotate API keys
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.auth.dependencies import get_current_user
from app.auth.api_key_auth import generate_api_key, hash_api_key
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyUpdate,
    APIKeyInfo,
    APIKeyRotateRequest,
    APIKeyRotateResponse,
)

router = APIRouter()


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Create a new API key for the current user.

    The response includes the plain API key string. This is the only time
    the plain key is shown - store it securely! If lost, you must
    create a new key.

    Args:
        key_data: API key creation parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created API key with plain key visible
    """
    # Generate key and hash
    plain_key, key_hash = generate_api_key()

    # Calculate expiration if requested
    expires_at = None
    if key_data.expires_in_days:
        from datetime import datetime, timedelta, timezone
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)

    # Create API key record
    new_key = APIKey(
        name=key_data.name,
        description=key_data.description,
        key_hash=key_hash,
        user_id=current_user.id,
        scopes=key_data.scopes,
        expires_at=expires_at,
        rate_limit_requests=key_data.rate_limit_requests,
        is_active=True
    )

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    return {
        "id": new_key.id,
        "name": new_key.name,
        "description": new_key.description,
        "key": plain_key,  # Plain key shown only here
        "scopes": new_key.scopes,
        "rate_limit_requests": new_key.rate_limit_requests,
        "expires_at": new_key.expires_at,
        "created_at": new_key.created_at
    }


@router.get("/", response_model=List[APIKeyInfo])
async def list_api_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    include_inactive: bool = False
) -> List[APIKey]:
    """
    List all API keys for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user
        include_inactive: Include revoked/inactive keys

    Returns:
        List of user's API keys (without plain key)
    """
    query = select(APIKey).where(APIKey.user_id == current_user.id)

    if not include_inactive:
        query = query.where(APIKey.is_active == True)

    query = query.order_by(APIKey.created_at.desc())

    result = await db.execute(query)
    keys = result.scalars().all()

    return keys


@router.get("/{key_id}", response_model=APIKeyInfo)
async def get_api_key(
    key_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> APIKey:
    """
    Get details of a specific API key.

    Args:
        key_id: ID of the API key
        db: Database session
        current_user: Current authenticated user

    Returns:
        API key details

    Raises:
        HTTPException: If key not found or not owned by user
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return api_key


@router.patch("/{key_id}", response_model=APIKeyInfo)
async def update_api_key(
    key_id: int,
    key_data: APIKeyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> APIKey:
    """
    Update an API key's properties.

    Note: Cannot update the key itself - use rotate endpoint for that.

    Args:
        key_id: ID of the API key
        key_data: Updated properties
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated API key

    Raises:
        HTTPException: If key not found or not owned by user
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    # Update only provided fields
    if key_data.name is not None:
        api_key.name = key_data.name

    if key_data.description is not None:
        api_key.description = key_data.description

    if key_data.scopes is not None:
        api_key.scopes = key_data.scopes

    if key_data.is_active is not None:
        api_key.is_active = key_data.is_active

    if key_data.rate_limit_requests is not None:
        api_key.rate_limit_requests = key_data.rate_limit_requests

    await db.commit()
    await db.refresh(api_key)

    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    Revoke (deactivate) an API key.

    The key is marked as inactive and can no longer be used.
    It's not deleted so the audit trail remains.

    Args:
        key_id: ID of the API key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If key not found or not owned by user
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    api_key.is_active = False
    await db.commit()


@router.post("/{key_id}/rotate", response_model=APIKeyRotateResponse)
async def rotate_api_key(
    key_id: int,
    rotate_data: APIKeyRotateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Rotate an API key (create new key, deactivate old key).

    This is useful for key rotation in compliance with security policies.
    The old key is immediately deactivated.

    Args:
        key_id: ID of the API key to rotate
        rotate_data: Rotation parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        New API key with plain key visible

    Raises:
        HTTPException: If key not found or not owned by user
    """
    # Find old key
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    old_key = result.scalar_one_or_none()

    if not old_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    # Deactivate old key
    old_key.is_active = False

    # Create new key with same properties
    plain_key, key_hash = generate_api_key()

    # Calculate expiration
    expires_at = None
    if rotate_data.expires_in_days:
        from datetime import datetime, timedelta, timezone
        expires_at = datetime.now(timezone.utc) + timedelta(days=rotate_data.expires_in_days)
    elif old_key.expires_at:
        # Keep same expiration as old key if not specified
        from datetime import timedelta, timezone
        expires_at = old_key.expires_at

    new_key = APIKey(
        name=old_key.name,
        description=old_key.description,
        key_hash=key_hash,
        user_id=current_user.id,
        scopes=old_key.scopes,
        expires_at=expires_at,
        rate_limit_requests=old_key.rate_limit_requests,
        is_active=True
    )

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    return {
        "old_key_id": old_key.id,
        "new_key_id": new_key.id,
        "new_key": plain_key,
        "message": f"Old API key (ID: {old_key.id}) has been deactivated. Update your applications to use the new key."
    }
