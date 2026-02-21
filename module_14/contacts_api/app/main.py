"""
Application entry point.

Registers:
  - CORS middleware (all origins in dev; restrict in production)
  - SlowAPI rate-limit middleware
  - API routers
  - 429 error handler for rate limit exceeded responses
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.v1 import auth, contacts, users

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Contacts management API — Module 14 demo project.",
    version="1.0.0",
)

# ─── Middleware ───────────────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


# ─── Health check ────────────────────────────────────────────────────────────

@app.get("/healthz", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}


# ─── Static UI ───────────────────────────────────────────────────────────────
# Монтується після роутерів щоб /api/v1/* мав пріоритет.
# Відкрий: http://localhost:8000/app/login.html
app.mount("/app", StaticFiles(directory="static", html=True), name="static")
