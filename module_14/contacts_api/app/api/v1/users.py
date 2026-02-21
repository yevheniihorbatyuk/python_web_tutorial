"""
User profile endpoints:
  GET   /users/me         → current user profile
  PATCH /users/me         → update email
  POST  /users/me/avatar  → upload image to Cloudinary, store URL
"""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.dependencies import require_verified
from app.services.cloudinary_service import upload_avatar

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(require_verified)],
) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> UserResponse:
    if body.email is not None:
        current_user.email = body.email
        await db.commit()
        await db.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_avatar(
    file: Annotated[UploadFile, File(description="Image file (JPEG, PNG, GIF, WebP, max 5 MB)")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_verified)],
) -> UserResponse:
    """
    Upload a profile photo to Cloudinary.

    The same public_id is reused so each upload overwrites the previous
    one — no orphaned files accumulate in Cloudinary storage.
    """
    url = await upload_avatar(file, current_user.id)
    current_user.avatar_url = url
    await db.commit()
    await db.refresh(current_user)
    return current_user
