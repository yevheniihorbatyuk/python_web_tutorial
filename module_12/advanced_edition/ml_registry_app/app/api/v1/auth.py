"""
Authentication API endpoints.

Provides user registration, login, token refresh, and user info endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, OAuth2Callback
from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import get_current_user
from app.auth.oauth2 import GoogleOAuth2, GitHubOAuth2

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If user with email/username already exists
    """
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    username: str,
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Login with username/email and password.

    Args:
        username: Username or email
        password: User password
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    result = await db.execute(
        select(User).where(
            (User.username == username) | (User.email == username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Refresh access token using refresh token.

    Args:
        refresh_token: Valid refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid or user not found
    """
    payload = decode_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return current_user


@router.post("/oauth2/google/callback", response_model=Token)
async def google_oauth2_callback(
    callback_data: OAuth2Callback,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Handle Google OAuth2 callback.

    This endpoint is called after the user authenticates with Google.
    It exchanges the authorization code for user information and creates
    or updates the user in our database.

    Args:
        callback_data: OAuth2 callback data with authorization code
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If OAuth2 exchange fails or user creation fails
    """
    try:
        # Exchange code for user information
        user = await GoogleOAuth2.handle_callback(
            code=callback_data.code,
            redirect_uri=callback_data.redirect_uri,
            db=db
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )

        # Create JWT tokens for the user
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google OAuth2 authentication failed: {str(e)}"
        )


@router.post("/oauth2/github/callback", response_model=Token)
async def github_oauth2_callback(
    callback_data: OAuth2Callback,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Handle GitHub OAuth2 callback.

    This endpoint is called after the user authenticates with GitHub.
    It exchanges the authorization code for user information and creates
    or updates the user in our database.

    Args:
        callback_data: OAuth2 callback data with authorization code
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If OAuth2 exchange fails or user creation fails
    """
    try:
        # Exchange code for user information
        user = await GitHubOAuth2.handle_callback(
            code=callback_data.code,
            redirect_uri=callback_data.redirect_uri,
            db=db
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with GitHub"
            )

        # Create JWT tokens for the user
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"GitHub OAuth2 authentication failed: {str(e)}"
        )
