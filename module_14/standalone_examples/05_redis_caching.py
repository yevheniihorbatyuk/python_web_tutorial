"""
05. Redis Caching — Cache-Aside Pattern
========================================

The cache-aside pattern (also called lazy loading):
1. Check cache first
2. If miss: query the real source, store in cache, return
3. On data change: invalidate (delete) the cache key

Used in contacts_api for the birthday query:
- Birthday data rarely changes
- Query involves date arithmetic across all contacts
- A 1-hour cache is acceptable (birthdays don't move)

Requirements:
    docker run -p 6379:6379 redis:7-alpine
    pip install redis

Run: python 05_redis_caching.py
"""

import asyncio
import json
import time
from datetime import date, datetime, timedelta
from typing import Any

import redis.asyncio as redis

# ============================================================
# SETUP
# ============================================================

REDIS_URL = "redis://localhost:6379/0"


async def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


# ============================================================
# SECTION 1: Basic cache-aside helper
# ============================================================

async def get_or_set_cache(
    r: redis.Redis,
    key: str,
    fetch_func,  # async callable that returns the value
    ttl_seconds: int = 3600,
) -> Any:
    """
    Cache-aside pattern implementation.

    Args:
        r: Redis client
        key: Cache key
        fetch_func: Async function that fetches fresh data on cache miss
        ttl_seconds: How long to keep data in cache

    Returns:
        Cached or freshly fetched data
    """
    # Try cache first
    cached = await r.get(key)
    if cached is not None:
        print(f"  CACHE HIT: {key}")
        return json.loads(cached)

    print(f"  CACHE MISS: {key} — fetching from source...")

    # Fetch fresh data
    value = await fetch_func()

    # Store in cache
    await r.setex(key, ttl_seconds, json.dumps(value, default=str))
    print(f"  Cached with TTL={ttl_seconds}s")

    return value


# ============================================================
# SECTION 2: Birthday cache in contacts_api
# ============================================================

async def simulate_birthday_query(user_id: int) -> list[dict]:
    """
    Simulate the birthday database query (slow operation).
    In contacts_api this is a PostgreSQL query with EXTRACT().
    """
    await asyncio.sleep(0.1)  # Simulate DB query latency
    today = date.today()
    return [
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "birthday": str(today + timedelta(days=2)),
            "days_until": 2,
        }
    ]


async def get_upcoming_birthdays_with_cache(
    r: redis.Redis, user_id: int
) -> list[dict]:
    """
    Get contacts with birthdays in next 7 days, with caching.

    Cache key includes today's date so the cache automatically
    becomes invalid at midnight (the date changes → new key → cache miss).
    """
    today = date.today().isoformat()
    cache_key = f"birthdays:{user_id}:{today}"

    return await get_or_set_cache(
        r,
        key=cache_key,
        fetch_func=lambda: simulate_birthday_query(user_id),
        ttl_seconds=3600,  # 1 hour
    )


# ============================================================
# SECTION 3: Cache invalidation
# ============================================================

async def invalidate_birthday_cache(r: redis.Redis, user_id: int) -> None:
    """
    Delete birthday cache when contact data changes.

    Called when:
    - A contact is created
    - A contact's birthday is updated
    - A contact is deleted

    Pattern: Delete the key for today (and optionally yesterday/tomorrow
    to handle edge cases around midnight).
    """
    today = date.today().isoformat()
    key = f"birthdays:{user_id}:{today}"
    deleted = await r.delete(key)
    print(f"  Invalidated cache key: {key} (deleted: {deleted})")


# ============================================================
# SECTION 4: TTL inspection and monitoring
# ============================================================

async def inspect_cache(r: redis.Redis, pattern: str = "birthdays:*") -> None:
    """Inspect all birthday cache entries."""
    print(f"\n  Cache entries matching '{pattern}':")
    async for key in r.scan_iter(pattern):
        ttl = await r.ttl(key)
        value = await r.get(key)
        data = json.loads(value) if value else None
        print(f"    {key}")
        print(f"      TTL: {ttl}s remaining")
        print(f"      Value: {data}")


# ============================================================
# SECTION 5: Logout token blacklist (Redis as a set of revoked tokens)
# ============================================================
"""
contacts_api uses Redis to implement logout by storing revoked
refresh token IDs (JTI claims). This is a simple token blacklist.
"""

async def blacklist_token(r: redis.Redis, jti: str, expires_in_seconds: int) -> None:
    """Add a token JTI to the blacklist. Expires with the token."""
    key = f"blacklist:{jti}"
    await r.setex(key, expires_in_seconds, "1")
    print(f"  Token blacklisted: {key} (TTL: {expires_in_seconds}s)")


async def is_token_blacklisted(r: redis.Redis, jti: str) -> bool:
    """Check if a token has been blacklisted (logged out)."""
    key = f"blacklist:{jti}"
    return await r.exists(key) > 0


# ============================================================
# DEMO
# ============================================================

async def main():
    print("Redis Cache-Aside Pattern Demo")
    print("=" * 50)
    print()

    try:
        r = await get_redis()
        await r.ping()
    except Exception as e:
        print(f"Redis not available: {e}")
        print("Start Redis: docker run -p 6379:6379 redis:7-alpine")
        return

    USER_ID = 42

    # Clean up from previous runs
    await r.delete(f"birthdays:{USER_ID}:{date.today().isoformat()}")

    print("=== Birthday Cache Demo ===")
    print()

    # First call: cache miss
    print("First call:")
    t1 = time.perf_counter()
    result = await get_upcoming_birthdays_with_cache(r, USER_ID)
    t2 = time.perf_counter()
    print(f"  Result: {result}")
    print(f"  Time: {(t2-t1)*1000:.1f}ms")
    print()

    # Second call: cache hit
    print("Second call (same user, same day):")
    t1 = time.perf_counter()
    result = await get_upcoming_birthdays_with_cache(r, USER_ID)
    t2 = time.perf_counter()
    print(f"  Result: {result}")
    print(f"  Time: {(t2-t1)*1000:.1f}ms  ← much faster, no DB query")
    print()

    # Inspect cache
    await inspect_cache(r)
    print()

    # Invalidate cache
    print("=== Cache Invalidation (contact updated) ===")
    await invalidate_birthday_cache(r, USER_ID)
    print()

    # Next call: cache miss again
    print("After invalidation:")
    t1 = time.perf_counter()
    result = await get_upcoming_birthdays_with_cache(r, USER_ID)
    t2 = time.perf_counter()
    print(f"  Time: {(t2-t1)*1000:.1f}ms  ← cache miss again, DB queried")
    print()

    # Token blacklist demo
    print("=== Token Blacklist Demo (logout) ===")
    import uuid
    jti = str(uuid.uuid4())
    print(f"Token JTI: {jti[:20]}...")

    is_blocked = await is_token_blacklisted(r, jti)
    print(f"Before logout — blacklisted: {is_blocked}")

    await blacklist_token(r, jti, expires_in_seconds=30)

    is_blocked = await is_token_blacklisted(r, jti)
    print(f"After logout — blacklisted: {is_blocked}")

    await r.aclose()
    print()
    print("Demo complete.")


if __name__ == "__main__":
    asyncio.run(main())
