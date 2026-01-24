"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        """Ensure bcrypt-compatible length (<=72 bytes)."""
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"


class TodoCreate(BaseModel):
    """Schema for creating a todo."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TodoResponse(BaseModel):
    """Schema for todo response."""

    id: int
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
