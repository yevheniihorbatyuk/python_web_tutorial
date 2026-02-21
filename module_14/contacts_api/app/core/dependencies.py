"""
FastAPI dependencies for authentication and authorisation.

  get_current_user   — valid access token → User (verified or not)
  require_verified   — same but raises 403 if email is not confirmed
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.core.cache import is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if not email:
        raise credentials_exc

    # Check blacklist (logged-out tokens)
    if await is_token_blacklisted(token):
        raise credentials_exc

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exc

    return user


async def require_verified(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Adds on top of get_current_user: user must have verified their email."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address is not verified. Check your inbox.",
        )
    return current_user
