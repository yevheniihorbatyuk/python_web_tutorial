"""
API Key authentication for service-to-service communication.

API keys provide a simple way for external services to authenticate
without requiring user interaction or login.

Usage in headers:
    X-API-Key: your-secret-key-here

Or in query parameters:
    GET /api/models?api_key=your-secret-key-here
"""

import secrets
import hashlib
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.api_key import APIKey


def generate_api_key() -> Tuple[str, str]:
    """
    Generate a new API key.

    Returns a tuple of (plain_key, key_hash).
    The plain_key should be shown to the user once.
    The key_hash should be stored in the database.

    Returns:
        Tuple of (plain_key, key_hash)
    """
    # Generate random 32-byte key encoded as hex (64 characters)
    plain_key = secrets.token_hex(32)

    # Hash the key using SHA-256
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

    return plain_key, key_hash


def hash_api_key(key: str) -> str:
    """Hash an API key for comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_user_by_api_key(
    api_key: str,
    db: AsyncSession
) -> Optional[Tuple[User, APIKey]]:
    """
    Validate API key and return associated user.

    Args:
        api_key: The API key string from request
        db: Database session

    Returns:
        Tuple of (User, APIKey) if valid, None otherwise
    """
    # Hash the provided key
    key_hash = hash_api_key(api_key)

    # Look up key in database
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash)
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        return None

    # Check if API key is valid (active and not expired)
    if not api_key_record.is_valid():
        return None

    # Load associated user
    result = await db.execute(
        select(User).where(User.id == api_key_record.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user, api_key_record


async def validate_api_key_scope(
    api_key_record: APIKey,
    required_scope: str
) -> bool:
    """
    Check if API key has required scope.

    Args:
        api_key_record: The APIKey database record
        required_scope: Required scope (e.g., "models:read")

    Returns:
        True if key has scope, False otherwise
    """
    return api_key_record.has_scope(required_scope)


class APIKeyNotFoundError(Exception):
    """API key not found or invalid."""

    pass


class APIKeyScopeError(Exception):
    """API key doesn't have required scope."""

    pass


class APIKeyExpiredError(Exception):
    """API key has expired."""

    pass


async def require_api_key(
    api_key: str,
    db: AsyncSession,
    required_scope: Optional[str] = None
) -> Tuple[User, APIKey]:
    """
    Validate API key and check scope.

    This is a utility function for manual API key validation.
    Use get_api_key_user() dependency for FastAPI endpoints.

    Args:
        api_key: The API key string
        db: Database session
        required_scope: Optional scope to check (e.g., "models:read")

    Returns:
        Tuple of (User, APIKey)

    Raises:
        APIKeyNotFoundError: If key is invalid
        APIKeyScopeError: If key doesn't have required scope
        APIKeyExpiredError: If key is expired
    """
    # Validate API key
    result = await get_user_by_api_key(api_key, db)

    if not result:
        raise APIKeyNotFoundError("Invalid or expired API key")

    user, api_key_record = result

    # Check if expired
    if api_key_record.is_expired():
        raise APIKeyExpiredError("API key has expired")

    # Check scope if required
    if required_scope:
        if not api_key_record.has_scope(required_scope):
            raise APIKeyScopeError(
                f"API key does not have required scope: {required_scope}"
            )

    return user, api_key_record


class APIKeyCredentials:
    """Container for API key credentials."""

    def __init__(self, api_key: str, source: str = "header"):
        self.api_key = api_key
        self.source = source  # "header" or "query"


async def extract_api_key_from_request(
    headers: dict = None,
    query_params: dict = None
) -> Optional[str]:
    """
    Extract API key from request headers or query parameters.

    Headers take precedence over query parameters.

    Supported locations:
    1. X-API-Key header
    2. Authorization: Bearer <api_key>
    3. api_key query parameter

    Args:
        headers: Request headers
        query_params: Query parameters

    Returns:
        API key string or None if not found
    """
    headers = headers or {}
    query_params = query_params or {}

    # Check X-API-Key header first
    if "x-api-key" in headers:
        return headers["x-api-key"]

    if "X-API-Key" in headers:
        return headers["X-API-Key"]

    # Check Authorization header (Bearer format)
    auth_header = headers.get("authorization", "").lower()
    if auth_header.startswith("bearer "):
        return auth_header[7:]  # Remove "bearer " prefix

    # Check query parameter (least preferred for security reasons)
    if "api_key" in query_params:
        return query_params["api_key"]

    return None


# ============================================================================
# FastAPI Dependency Injection
# ============================================================================

from typing import Annotated
from fastapi import Depends, Header, Query
from fastapi.security import HTTPException

from app.database import get_db


async def get_api_key_user(
    x_api_key: Annotated[Optional[str], Header()] = None,
    api_key_query: Annotated[Optional[str], Query()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None
) -> User:
    """
    FastAPI dependency to validate API key and return user.

    Supports API key from:
    1. X-API-Key header (preferred)
    2. api_key query parameter

    Usage:
        @router.get("/models")
        async def list_models(
            current_user: Annotated[User, Depends(get_api_key_user)]
        ):
            # User is authenticated via API key
            pass

    Raises:
        HTTPException: If API key is invalid or missing
    """
    api_key = x_api_key or api_key_query

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user, _ = await require_api_key(api_key, db)
        return user
    except APIKeyNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    except APIKeyExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )


async def get_api_key_user_with_scope(
    required_scope: str
):
    """
    Create a dependency that validates API key and checks scope.

    Usage:
        @router.post("/models")
        async def create_model(
            current_user: Annotated[User, Depends(
                get_api_key_user_with_scope("models:write")
            )]
        ):
            # User is authenticated via API key with write scope
            pass

    Args:
        required_scope: Required scope (e.g., "models:write")

    Returns:
        Dependency function
    """
    async def dependency(
        x_api_key: Annotated[Optional[str], Header()] = None,
        api_key_query: Annotated[Optional[str], Query()] = None,
        db: Annotated[AsyncSession, Depends(get_db)] = None
    ) -> User:
        api_key = x_api_key or api_key_query

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )

        try:
            user, _ = await require_api_key(api_key, db, required_scope)
            return user
        except APIKeyNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key"
            )
        except APIKeyExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )
        except APIKeyScopeError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key does not have required scope: {required_scope}"
            )

    return dependency
