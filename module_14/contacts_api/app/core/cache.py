"""
Redis async helpers.

Two responsibilities:
  1. Cache-aside helper (get_or_set_cache) for read-heavy endpoints
  2. Token blacklist for logout (JWT tokens are stateless, so we store
     invalidated tokens in Redis until they naturally expire)
"""

import json
from typing import Any, Callable, Optional

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

# Single shared connection pool — created once at import time.
# None when Redis is unavailable (tests can mock it out).
_redis: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


# ─── Cache-aside ──────────────────────────────────────────────────────────────


async def get_or_set_cache(key: str, ttl: int, loader: Callable) -> Any:
    """
    Classic cache-aside pattern:
      1. Try to get the value from Redis.
      2. On cache miss: call *loader()*, store the result, return it.

    Args:
        key:    Redis key (should be unique per resource + owner + date)
        ttl:    Time-to-live in seconds
        loader: Async callable that returns a JSON-serialisable value
    """
    redis = get_redis()
    cached = await redis.get(key)
    if cached is not None:
        return json.loads(cached)

    fresh = await loader()
    await redis.setex(key, ttl, json.dumps(fresh, default=str))
    return fresh


async def invalidate_cache(key: str) -> None:
    redis = get_redis()
    await redis.delete(key)


# ─── Token blacklist ─────────────────────────────────────────────────────────


async def blacklist_token(token: str, ttl_seconds: int) -> None:
    """Add token to Redis blacklist until it naturally expires."""
    redis = get_redis()
    await redis.setex(f"blacklist:{token}", ttl_seconds, "1")


async def is_token_blacklisted(token: str) -> bool:
    redis = get_redis()
    return await redis.exists(f"blacklist:{token}") == 1
