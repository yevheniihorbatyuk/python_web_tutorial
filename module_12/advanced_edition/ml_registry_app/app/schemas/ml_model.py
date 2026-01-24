"""
Pydantic schemas for ML Model.

Used for request/response validation in API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.ml_model import ModelLifecycle, MLFramework, TaskType


class MLModelBase(BaseModel):
    """Base ML model schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    framework: MLFramework
    task_type: TaskType


class MLModelCreate(MLModelBase):
    """Schema for creating a new ML model."""

    lifecycle: Optional[ModelLifecycle] = ModelLifecycle.DEVELOPMENT
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    precision: Optional[float] = Field(None, ge=0.0, le=1.0)
    recall: Optional[float] = Field(None, ge=0.0, le=1.0)
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    hyperparameters: Optional[dict] = None


class MLModelUpdate(BaseModel):
    """Schema for updating an ML model."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    precision: Optional[float] = Field(None, ge=0.0, le=1.0)
    recall: Optional[float] = Field(None, ge=0.0, le=1.0)
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    hyperparameters: Optional[dict] = None


class MLModelResponse(MLModelBase):
    """Schema for ML model responses."""

    id: int
    lifecycle: ModelLifecycle
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    hyperparameters: Optional[dict]
    model_file_path: Optional[str]
    owner_id: int
    experiment_id: Optional[int]

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
    )
