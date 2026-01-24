"""
User model for authentication and authorization.

Stores user accounts with email, username, and hashed passwords.
"""

from typing import List, Optional
from enum import Enum
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, Enum):
    """Role names for RBAC."""

    user = "user"
    reviewer = "reviewer"
    admin = "admin"


class User(Base, TimestampMixin):
    """User model with authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.user.value, nullable=False)

    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    ml_models: Mapped[List["MLModel"]] = relationship(
        "MLModel",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
