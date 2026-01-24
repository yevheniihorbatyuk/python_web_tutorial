"""
ML Models API endpoints.

Provides CRUD operations for ML models with filtering and pagination.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.ml_model import MLModel, ModelLifecycle, MLFramework
from app.schemas.ml_model import MLModelCreate, MLModelUpdate, MLModelResponse
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MLModelResponse])
async def list_models(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    lifecycle: Optional[ModelLifecycle] = Query(None),
    framework: Optional[MLFramework] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[MLModel]:
    """
    List ML models with filtering and pagination.

    Args:
        db: Database session
        current_user: Current authenticated user
        lifecycle: Filter by lifecycle stage
        framework: Filter by ML framework
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of ML models matching filters
    """
    query = select(MLModel)

    # Apply filters
    filters = []
    if lifecycle:
        filters.append(MLModel.lifecycle == lifecycle)
    if framework:
        filters.append(MLModel.framework == framework)

    if filters:
        query = query.where(and_(*filters))

    # RBAC: regular users can only see their own models
    if not current_user.is_superuser and current_user.role not in {
        UserRole.admin.value,
        UserRole.reviewer.value
    }:
        query = query.where(MLModel.owner_id == current_user.id)

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    models = result.scalars().all()

    return models


@router.post("/", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: MLModelCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MLModel:
    """
    Create a new ML model.

    Args:
        model_data: Model creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created ML model
    """
    new_model = MLModel(
        **model_data.model_dump(),
        owner_id=current_user.id
    )

    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)

    return new_model


@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MLModel:
    """
    Get a specific ML model by ID.

    Args:
        model_id: ID of the model to retrieve
        db: Database session
        current_user: Current authenticated user

    Returns:
        ML model with specified ID

    Raises:
        HTTPException: If model not found
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    return model


@router.put("/{model_id}", response_model=MLModelResponse)
async def update_model(
    model_id: int,
    model_data: MLModelUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MLModel:
    """
    Update an ML model.

    Args:
        model_id: ID of the model to update
        model_data: Updated model data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated ML model

    Raises:
        HTTPException: If model not found or user lacks permissions
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    # Check ownership
    if model.owner_id != current_user.id and not (
        current_user.is_superuser or current_user.role == UserRole.admin.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )

    # Update fields
    for field, value in model_data.model_dump(exclude_unset=True).items():
        setattr(model, field, value)

    await db.commit()
    await db.refresh(model)

    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    Delete an ML model.

    Args:
        model_id: ID of the model to delete
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If model not found or user lacks permissions
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    # Check ownership
    if model.owner_id != current_user.id and not (
        current_user.is_superuser or current_user.role == UserRole.admin.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )

    await db.delete(model)
    await db.commit()


@router.patch("/{model_id}/lifecycle", response_model=MLModelResponse)
async def update_model_lifecycle(
    model_id: int,
    new_lifecycle: ModelLifecycle,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MLModel:
    """
    Update model lifecycle stage.

    Args:
        model_id: ID of the model
        new_lifecycle: New lifecycle stage
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated ML model

    Raises:
        HTTPException: If model not found or user lacks permissions
    """
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    # Check ownership
    if model.owner_id != current_user.id and not (
        current_user.is_superuser or current_user.role == UserRole.admin.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )

    model.lifecycle = new_lifecycle
    await db.commit()
    await db.refresh(model)

    return model
