"""
Model version model for tracking model versions.

Stores version history and snapshots of model metrics.
"""

from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ModelVersion(Base, TimestampMixin):
    """Model versioning for tracking changes."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_tag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Snapshot of metrics at this version
    metrics_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # File path for this version
    model_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Foreign keys
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ml_models.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    model: Mapped["MLModel"] = relationship("MLModel", back_populates="versions")

    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.id}, model_id={self.model_id}, version={self.version_number})>"
