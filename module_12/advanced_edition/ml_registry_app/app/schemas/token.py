"""
Pydantic schemas for JWT tokens.

Used for authentication request/response validation.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Response schema for token endpoints."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    sub: int | None = None  # Subject (user_id)
    type: str = "access"  # Token type: access or refresh


class OAuth2Callback(BaseModel):
    """OAuth2 callback request with authorization code."""

    code: str
    redirect_uri: str
