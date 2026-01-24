"""
Pydantic schemas for User models.

Used for request/response validation in API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        """Ensure bcrypt-compatible length (<=72 bytes)."""
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user responses."""

    id: int
    is_active: bool
    is_superuser: bool
    role: UserRole

    class Config:
        from_attributes = True
