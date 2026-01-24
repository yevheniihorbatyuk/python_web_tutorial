"""Main FastAPI application for Todo App."""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from contextlib import asynccontextmanager

from .database import engine, get_db, Base
from . import models, schemas, auth

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created")
    yield
    # Shutdown: Clean up
    await engine.dispose()
    print("✓ Database connection closed")


app = FastAPI(
    title="Todo API",
    description="A simple todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "todo-api"}


# ============================================================================
# Authentication Endpoints
# ============================================================================


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_user = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=auth.get_password_hash(user.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login(
    credentials: schemas.LoginRequest, db: AsyncSession = Depends(get_db)
):
    """Login and receive JWT token."""
    # Find user
    result = await db.execute(
        select(models.User).where(models.User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Create token with role
    access_token = auth.create_access_token(user.id, user.role)
    return {"access_token": access_token}


@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    user_id: int = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ============================================================================
# Todo Endpoints
# ============================================================================


@app.get("/todos", response_model=List[schemas.TodoResponse])
async def list_todos(
    completed: bool | None = Query(None, description="Filter by completion status"),
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all todos for the current user."""
    query = select(models.Todo).where(models.Todo.owner_id == user_id)

    if completed is not None:
        query = query.where(models.Todo.completed == completed)

    result = await db.execute(query.order_by(models.Todo.created_at.desc()))
    todos = result.scalars().all()

    return todos


@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
async def create_todo(
    todo: schemas.TodoCreate,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new todo."""
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        due_date=todo.due_date,
        owner_id=user_id,
    )
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    return db_todo


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
async def get_todo(
    todo_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific todo."""
    result = await db.execute(
        select(models.Todo).where(
            models.Todo.id == todo_id, models.Todo.owner_id == user_id
        )
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return todo


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a todo."""
    result = await db.execute(
        select(models.Todo).where(
            models.Todo.id == todo_id, models.Todo.owner_id == user_id
        )
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    # Update fields
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    await db.commit()
    await db.refresh(todo)

    return todo


@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a todo."""
    result = await db.execute(
        select(models.Todo).where(
            models.Todo.id == todo_id, models.Todo.owner_id == user_id
        )
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    await db.delete(todo)
    await db.commit()

    return None


@app.patch("/todos/{todo_id}/complete", response_model=schemas.TodoResponse)
async def complete_todo(
    todo_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a todo as complete."""
    result = await db.execute(
        select(models.Todo).where(
            models.Todo.id == todo_id, models.Todo.owner_id == user_id
        )
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    todo.completed = True
    await db.commit()
    await db.refresh(todo)

    return todo
