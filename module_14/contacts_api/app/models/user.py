"""
User model — extends the Module 12 pattern.

New fields compared to Module 12:
  - is_verified: email must be confirmed before login is allowed
  - avatar_url:  Cloudinary URL set after uploading a photo
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Email verification (new in Module 14)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Avatar uploaded to Cloudinary (new in Module 14)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', verified={self.is_verified})>"
