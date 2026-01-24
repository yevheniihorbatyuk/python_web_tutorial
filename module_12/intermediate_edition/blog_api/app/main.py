"""FastAPI application for Blog API."""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from contextlib import asynccontextmanager

from .database import engine, get_db, Base
from . import models, schemas, auth

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created")
    yield
    await engine.dispose()
    print("✓ Database connection closed")


app = FastAPI(
    title="Blog API",
    description="A simple blog application with posts and comments",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "blog-api"}


# ============================================================================
# Authentication Endpoints
# ============================================================================


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
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
    """Login and receive JWT token with role."""
    result = await db.execute(
        select(models.User).where(models.User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create token with role
    access_token = auth.create_access_token(user.id, user.role)
    return {"access_token": access_token}


@app.get("/auth/me", response_model=schemas.UserResponse)
async def get_me(
    user_id: int = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ============================================================================
# Post Endpoints
# ============================================================================


@app.get("/posts", response_model=List[schemas.PostResponse])
async def list_posts(
    author_id: int | None = Query(None, description="Filter by author"),
    published: bool | None = Query(None, description="Filter by publication status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all posts with optional filtering."""
    query = select(models.Post)

    if author_id is not None:
        query = query.where(models.Post.author_id == author_id)

    if published is not None:
        query = query.where(models.Post.published == published)

    query = query.order_by(desc(models.Post.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    posts = result.scalars().all()

    return posts


@app.post("/posts", response_model=schemas.PostResponse, status_code=201)
async def create_post(
    post: schemas.PostCreate,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new blog post."""
    db_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        author_id=user_id,
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    return db_post


@app.get("/posts/{post_id}", response_model=schemas.PostWithCommentsResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific post with comments."""
    result = await db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a blog post (author only)."""
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id, models.Post.author_id == user_id
        )
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = post_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)

    return post


@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a blog post (author only)."""
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id, models.Post.author_id == user_id
        )
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()

    return None


# ============================================================================
# Comment Endpoints
# ============================================================================


@app.post("/posts/{post_id}/comments", response_model=schemas.CommentResponse, status_code=201)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to a post."""
    # Verify post exists
    post_result = await db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        author_id=user_id,
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    return db_comment


@app.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment (author only)."""
    result = await db.execute(
        select(models.Comment).where(
            models.Comment.id == comment_id, models.Comment.author_id == user_id
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    await db.delete(comment)
    await db.commit()

    return None
