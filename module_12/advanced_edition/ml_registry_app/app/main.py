"""
FastAPI application entry point.

Main application setup with routes and middleware configuration.
"""

from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import engine
from app.models.base import Base
from app.api.v1 import auth, models, files

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown."""
    # Startup
    async with engine.begin() as conn:
        # Create tables (in production, use Alembic migrations)
        await conn.run_sync(Base.metadata.create_all)
        # Ensure legacy databases have the role column expected by the User model.
        await conn.execute(
            text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'user'"
            )
        )

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(models.router, prefix="/api/v1/models", tags=["ml-models"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])


@app.get("/")
async def root() -> dict:
    """Root endpoint with API info."""
    return {
        "message": "ML Model Registry API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
