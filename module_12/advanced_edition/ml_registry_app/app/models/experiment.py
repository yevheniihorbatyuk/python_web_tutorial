"""
Experiment model for tracking ML experiments.

Stores experiment metadata and links to resulting models.
"""

from typing import List, Optional
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Experiment(Base, TimestampMixin):
    """Experiment tracking for ML model development."""

    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Experiment metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="experiments")
    models: Mapped[List["MLModel"]] = relationship(
        "MLModel",
        back_populates="experiment"
    )

    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name={self.name})>"
