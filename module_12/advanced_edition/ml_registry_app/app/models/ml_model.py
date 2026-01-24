"""
ML Model entity for the model registry.

Core entity for storing machine learning models with metadata.
"""

from typing import List, Optional
from enum import Enum
from sqlalchemy import String, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ModelLifecycle(str, Enum):
    """Model lifecycle stages."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class MLFramework(str, Enum):
    """Supported ML frameworks."""

    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"


class TaskType(str, Enum):
    """ML task types."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"


class MLModel(Base, TimestampMixin):
    """ML Model entity for model registry."""

    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    framework: Mapped[MLFramework] = mapped_column(SQLEnum(MLFramework), nullable=False)
    task_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType), nullable=False)
    lifecycle: Mapped[ModelLifecycle] = mapped_column(
        SQLEnum(ModelLifecycle),
        default=ModelLifecycle.DEVELOPMENT,
        index=True,
        nullable=False
    )

    # Metrics (optional)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Hyperparameters stored as JSON
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Model file path in MinIO
    model_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    experiment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="ml_models")
    experiment: Mapped[Optional["Experiment"]] = relationship(
        "Experiment",
        back_populates="models"
    )
    versions: Mapped[List["ModelVersion"]] = relationship(
        "ModelVersion",
        back_populates="model",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MLModel(id={self.id}, name={self.name}, lifecycle={self.lifecycle})>"
