"""
04. Rate Limiting with SlowAPI
==============================

Rate limiting prevents:
- Brute force attacks on login (try 10,000 passwords/second)
- Bot registration (create 1000 accounts/minute)
- API abuse (scrape all contacts from everyone)

SlowAPI is the standard rate limiting library for FastAPI.
It mirrors Flask-Limiter's API.

Self-contained — memory backend (no Redis needed for this demo).
Run: python 04_rate_limiting.py
Then: for i in {1..7}; do curl -s http://localhost:8001/login | python -c "import sys,json; d=json.load(sys.stdin); print(d)"; done
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# ============================================================
# SETUP
# ============================================================

# key_func: how to identify a "client"
# get_remote_address: use IP address (most common)
# For authenticated endpoints: use user ID instead of IP
limiter = Limiter(
    key_func=get_remote_address,
    # storage_uri="redis://localhost:6379"  # in production (contacts_api)
    # default: in-memory (fine for single instance, not distributed)
)

app = FastAPI(title="Rate Limiting Demo")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ============================================================
# ENDPOINTS WITH DIFFERENT LIMITS
# ============================================================

@app.post("/register")
@limiter.limit("5/minute")  # 5 registration attempts per minute per IP
async def register(request: Request, email: str = "user@example.com"):
    """
    Strict limit: 5/minute.
    Registration abuse enables spam accounts, so we limit hard.
    """
    return {"message": f"Registered: {email}", "remaining": "check X-RateLimit-Remaining header"}


@app.post("/login")
@limiter.limit("10/minute")  # 10 login attempts per minute per IP
async def login(request: Request, email: str = "user@example.com"):
    """
    Slightly more generous than register, but still strict.
    Prevents brute force password attacks.
    """
    return {"message": "Login attempt processed"}


@app.get("/contacts")
@limiter.limit("60/minute")  # 60 reads per minute — generous for legit use
async def list_contacts(request: Request):
    """
    Read endpoints get more generous limits.
    Normal browsing doesn't exceed 60 requests/minute.
    """
    return {"contacts": [], "message": "Within limit"}


@app.get("/health")
async def health():
    """No limit on health check — used by load balancers."""
    return {"status": "ok"}


# ============================================================
# CUSTOM RATE LIMIT RESPONSE
# ============================================================
"""
By default, SlowAPI returns a plain 429 response.
You can customize the response with a custom handler.
"""


# Override the default handler with a JSON response:
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after_seconds": 60,
        },
        headers={"Retry-After": "60"},
    )


# ============================================================
# TESTING RATE LIMITS
# ============================================================
"""
When testing your FastAPI app, you need to disable rate limiting.
Otherwise tests interfere with each other (test 1 uses up some
of test 2's quota).

In conftest.py (contacts_api):

from slowapi.wrappers import Limit
import limits.storage

@pytest.fixture(autouse=True)
def reset_rate_limits(app):
    # Use in-memory storage that resets between tests
    app.state.limiter._storage = limits.storage.MemoryStorage()
    yield
"""


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Rate Limiting Demo")
    print("=" * 50)
    print()
    print("Starting server at http://localhost:8001")
    print()
    print("Test the rate limits:")
    print()
    print("Register (limit: 5/minute):")
    print("  for i in {1..7}; do curl -s -X POST 'http://localhost:8001/register?email=test@test.com' | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('message','') or d.get('error',''))\"; done")
    print()
    print("Login (limit: 10/minute):")
    print("  for i in {1..12}; do curl -s -X POST 'http://localhost:8001/login' | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('message','') or d.get('error',''))\"; done")
    print()
    print("Contacts (limit: 60/minute):")
    print("  for i in {1..65}; do curl -s 'http://localhost:8001/contacts' | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('message','') or d.get('error',''))\"; done")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")
