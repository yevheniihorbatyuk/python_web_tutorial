"""
Pydantic schemas for API key endpoints.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Request to create a new API key."""

    name: str = Field(..., min_length=1, max_length=255, description="Name for the API key")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    scopes: str = Field(
        default="read:*",
        description='Comma-separated scopes (e.g., "models:read,experiments:write")'
    )
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=36500,  # 100 years max
        description="Days until key expires (optional, no expiration if not set)"
    )
    rate_limit_requests: int = Field(
        default=1000,
        ge=1,
        description="Maximum requests per hour"
    )


class APIKeyResponse(BaseModel):
    """Response when API key is created (includes plain key)."""

    id: int
    name: str
    description: Optional[str]
    key: str = Field(
        ...,
        description="Plain API key (shown only once, save it securely!)"
    )
    scopes: str
    rate_limit_requests: int
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyUpdate(BaseModel):
    """Request to update API key."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    scopes: Optional[str] = None
    is_active: Optional[bool] = None
    rate_limit_requests: Optional[int] = Field(None, ge=1)


class APIKeyInfo(BaseModel):
    """API key information (without plain key)."""

    id: int
    name: str
    description: Optional[str]
    key_hash: str = Field(
        ...,
        description="Hash of the key (first 8 chars visible for reference)"
    )
    scopes: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    total_requests: int
    rate_limit_requests: int
    created_at: datetime
    updated_at: datetime

    @property
    def key_preview(self) -> str:
        """Show first 8 characters of key hash."""
        return self.key_hash[:8] + "..."

    class Config:
        from_attributes = True


class APIKeyRotateRequest(BaseModel):
    """Request to rotate an API key."""

    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=36500,
        description="Days until new key expires"
    )


class APIKeyRotateResponse(BaseModel):
    """Response when API key is rotated."""

    old_key_id: int
    new_key_id: int
    new_key: str = Field(
        ...,
        description="New plain API key (save it securely!)"
    )
    message: str = Field(
        ...,
        description="Note about the old key being deactivated"
    )
