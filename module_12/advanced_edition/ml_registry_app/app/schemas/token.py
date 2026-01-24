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


class OAuth2AuthURL(BaseModel):
    """OAuth2 authorization URL response."""

    auth_url: str
    description: str = "Redirect the user to this URL to authenticate with the provider"
