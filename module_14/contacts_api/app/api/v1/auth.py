"""
Auth endpoints:
  POST /register    → create user, send verification email
  GET  /verify/{token} → decode email token, mark is_verified=True
  POST /login       → verify credentials + email, return tokens
  POST /refresh     → exchange refresh token for new access token
  POST /logout      → blacklist the refresh token in Redis

Rate limits applied to sensitive endpoints to slow down brute-force:
  - /register: 5 per minute
  - /login:    10 per minute
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.token import Token, TokenRefresh
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import get_user_by_email, create_user
from app.services.email import send_verification_email
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_email_token,
)
from app.core.cache import blacklist_token
from app.core.rate_limit import limiter
from app.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Create a new user account.

    Sends a verification email — the account cannot log in until
    the link in that email is clicked.
    """
    existing = await get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = await create_user(body.email, body.password, db)
    await send_verification_email(user.email)

    return user


@router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Confirm email address via the token from the verification email.

    Returns 400 if:
      - token is expired (TTL 24h)
      - token has wrong purpose (someone passed an access token here)
      - token is invalid / tampered
    """
    email = decode_email_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link.",
        )

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")

    if user.is_verified:
        return {"message": "Email already verified."}

    user.is_verified = True
    await db.commit()

    return {"message": "Email verified. You can now log in."}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Authenticate with email + password.

    Returns HTTP 403 (not 401) when the account exists but email is
    not yet verified — helps the client show a useful error message.
    """
    user = await get_user_by_email(form_data.username, db)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address is not verified. Check your inbox.",
        )

    return Token(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    body: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Exchange a valid refresh token for a new access token."""
    email = decode_refresh_token(body.refresh_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return Token(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: TokenRefresh) -> None:
    """
    Invalidate the refresh token by adding it to the Redis blacklist.

    JWT tokens are stateless, so we can't delete them — instead we
    keep a blacklist in Redis until the token's natural expiry.
    """
    await blacklist_token(
        body.refresh_token,
        ttl_seconds=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
