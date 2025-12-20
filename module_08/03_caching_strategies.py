"""
Module 8.3: Caching Strategies - Redis & LRU Cache
===================================================

Advanced caching patterns for performance optimization:
- LRU (Least Recently Used) cache - Python built-in @lru_cache
- Redis for distributed caching
- Cache invalidation strategies
- Performance benchmarking
- Real-world use cases (recommendations, ML predictions, etc.)

Author: Senior Data Science Engineer
"""

import time
import math
import json
import hashlib
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Try to import Redis, handle gracefully if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}

redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(**REDIS_CONFIG)
        redis_client.ping()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.warning(f"⚠ Redis not available: {str(e)}")
        redis_client = None


# ============================================================================
# BENCHMARK UTILITIES
# ============================================================================

@dataclass
class CacheStats:
    """Statistics for cache performance."""
    hits: int = 0
    misses: int = 0
    total_calls: int = 0
    hit_ratio: float = 0.0
    avg_time_cached: float = 0.0
    avg_time_uncached: float = 0.0

    def update(self, is_hit: bool, cached_time: float, uncached_time: float) -> None:
        """Update cache statistics."""
        self.total_calls += 1
        if is_hit:
            self.hits += 1
        else:
            self.misses += 1

        self.hit_ratio = self.hits / self.total_calls if self.total_calls > 0 else 0
        self.avg_time_cached = cached_time
        self.avg_time_uncached = uncached_time

    def __str__(self) -> str:
        return (
            f"Cache Stats: {self.hits} hits, {self.misses} misses, "
            f"Hit Ratio: {self.hit_ratio:.2%}, "
            f"Time saved: {(self.avg_time_uncached - self.avg_time_cached)*1000:.2f}ms"
        )


class PerformanceTimer:
    """Context manager for timing code execution."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time

    def __str__(self):
        return f"{self.name}: {self.elapsed*1000:.2f}ms"


# ============================================================================
# LRU CACHE PATTERNS
# ============================================================================

class FibonacciCalculator:
    """
    Demonstrate LRU cache benefits for recursive computations.
    Without caching: O(2^n) time complexity
    With caching: O(n) time complexity
    """

    @staticmethod
    def fibonacci_no_cache(n: int) -> int:
        """Fibonacci without caching (slow)."""
        if n <= 1:
            return n
        return FibonacciCalculator.fibonacci_no_cache(n-1) + FibonacciCalculator.fibonacci_no_cache(n-2)

    @staticmethod
    @lru_cache(maxsize=128)
    def fibonacci_with_cache(n: int) -> int:
        """Fibonacci with LRU cache (fast)."""
        if n <= 1:
            return n
        return FibonacciCalculator.fibonacci_with_cache(n-1) + FibonacciCalculator.fibonacci_with_cache(n-2)

    @staticmethod
    def benchmark_fibonacci(n: int) -> Tuple[float, float, float]:
        """
        Benchmark Fibonacci with and without cache.
        Return: (no_cache_time, with_cache_time, speedup)
        """
        # Note: Only test small n for uncached version to avoid timeout
        if n <= 30:
            with PerformanceTimer("Fibonacci no cache") as timer:
                result_no_cache = FibonacciCalculator.fibonacci_no_cache(n)
            time_no_cache = timer.elapsed
        else:
            time_no_cache = float('inf')
            result_no_cache = None

        # Clear cache before benchmarking
        FibonacciCalculator.fibonacci_with_cache.cache_clear()

        with PerformanceTimer("Fibonacci with cache") as timer:
            result_with_cache = FibonacciCalculator.fibonacci_with_cache(n)
        time_with_cache = timer.elapsed

        speedup = time_no_cache / time_with_cache if time_no_cache != float('inf') else "∞"
        return time_no_cache, time_with_cache, speedup


# ============================================================================
# CUSTOM CACHING DECORATORS
# ============================================================================

def timed_lru_cache(maxsize: int = 128, ttl_seconds: int = 3600):
    """
    LRU cache with TTL (Time To Live).
    Cache entries expire after ttl_seconds.
    """
    def decorator(func: Callable) -> Callable:
        # Store cache with timestamp
        cache: Dict[str, Tuple[Any, float]] = {}
        hits = misses = 0

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal hits, misses

            # Create cache key
            key = str(args) + str(kwargs)
            now = time.time()

            # Check if in cache and not expired
            if key in cache:
                cached_value, cached_time = cache[key]
                if now - cached_time < ttl_seconds:
                    hits += 1
                    logger.debug(f"Cache HIT for {func.__name__}")
                    return cached_value
                else:
                    # Expired, remove
                    del cache[key]

            # Cache miss - compute value
            misses += 1
            logger.debug(f"Cache MISS for {func.__name__}")
            result = func(*args, **kwargs)

            # Store in cache
            if len(cache) >= maxsize:
                # Simple removal of oldest entry
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]

            cache[key] = (result, now)
            return result

        # Add cache info method
        def cache_info():
            return {
                "hits": hits,
                "misses": misses,
                "size": len(cache),
                "maxsize": maxsize,
                "hit_ratio": hits / (hits + misses) if (hits + misses) > 0 else 0
            }

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache.clear
        return wrapper

    return decorator


# ============================================================================
# REDIS-BASED CACHING
# ============================================================================

class RedisCache:
    """Redis-based caching layer for distributed systems."""

    def __init__(self, client: Optional[Any] = None):
        self.client = client

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Redis HIT: {key}")
                return json.loads(value)
            logger.debug(f"Redis MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache with TTL."""
        if not self.client:
            return False

        try:
            json_value = json.dumps(value, default=str)
            self.client.setex(key, ttl, json_value)
            logger.debug(f"Redis SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    def delete(self, key: str) -> None:
        """Delete key from Redis cache."""
        if not self.client:
            return

        try:
            self.client.delete(key)
            logger.debug(f"Redis DELETE: {key}")
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return 0


def redis_cache(ttl: int = 3600):
    """
    Decorator for Redis caching.
    Caches function results in Redis with TTL.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not redis_client:
                # Fallback to direct execution if Redis unavailable
                return func(*args, **kwargs)

            # Create cache key from function name and args
            key = f"{func.__module__}:{func.__name__}:{args}:{kwargs}"
            key_hash = hashlib.md5(key.encode()).hexdigest()

            # Try to get from cache
            cache = RedisCache(redis_client)
            cached_result = cache.get(key_hash)
            if cached_result is not None:
                return cached_result

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(key_hash, result, ttl)
            return result

        return wrapper

    return decorator


# ============================================================================
# REAL-WORLD USE CASES
# ============================================================================

class RecommendationEngine:
    """Recommendation system with caching."""

    def __init__(self):
        self.redis_cache = RedisCache(redis_client)
        self.stats = CacheStats()

    @redis_cache(ttl=3600)
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get personalized recommendations for a user.
        Cache expensive ML computation.
        """
        logger.info(f"Computing recommendations for user {user_id}...")
        time.sleep(0.5)  # Simulate ML computation

        # Example recommendations
        recommendations = [
            {"product_id": f"PROD-{i}", "score": 0.95 - i*0.05}
            for i in range(1, limit + 1)
        ]
        return recommendations

    @timed_lru_cache(maxsize=1000, ttl_seconds=600)
    def get_trending_items(self, category: str) -> List[Dict]:
        """
        Get trending items in category.
        Cache for 10 minutes.
        """
        logger.info(f"Computing trending items for {category}...")
        time.sleep(0.3)  # Simulate database query

        items = [
            {"item_id": i, "trend_score": 100 - i*5}
            for i in range(1, 11)
        ]
        return items

    @lru_cache(maxsize=512)
    def get_product_details(self, product_id: str) -> Dict:
        """Get product details with LRU cache."""
        logger.info(f"Fetching details for {product_id}...")
        time.sleep(0.1)

        return {
            "id": product_id,
            "name": f"Product {product_id}",
            "price": 99.99,
            "description": "High-quality product"
        }


class MLPredictionService:
    """ML prediction service with caching."""

    def __init__(self):
        self.model_cache = {}

    @redis_cache(ttl=7200)
    def predict_user_churn(self, user_id: int) -> Dict[str, float]:
        """
        Predict user churn probability.
        Cache ML model predictions.
        """
        logger.info(f"Computing churn prediction for user {user_id}...")
        time.sleep(0.2)  # Simulate model inference

        return {
            "user_id": user_id,
            "churn_probability": 0.35,
            "confidence": 0.92,
            "timestamp": datetime.utcnow().isoformat()
        }

    @lru_cache(maxsize=256)
    def embedding_lookup(self, item_id: str) -> Tuple[float, ...]:
        """
        Get pre-computed embeddings for items.
        Common in recommendation systems.
        """
        logger.info(f"Loading embedding for {item_id}...")
        # Simulate loading 768-dimensional embedding
        return tuple([0.5] * 768)


# ============================================================================
# CACHE INVALIDATION STRATEGIES
# ============================================================================

class CacheInvalidationManager:
    """Manage cache invalidation in distributed systems."""

    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache

    def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate all cache entries for a user."""
        # Clear all keys matching user pattern
        deleted = self.cache.clear_pattern(f"*user:{user_id}*")
        logger.info(f"Invalidated {deleted} cache entries for user {user_id}")

    def invalidate_category_cache(self, category: str) -> None:
        """Invalidate category-related cache."""
        deleted = self.cache.clear_pattern(f"*category:{category}*")
        logger.info(f"Invalidated {deleted} cache entries for category {category}")

    def invalidate_all_recommendations(self) -> None:
        """Invalidate all recommendation caches."""
        deleted = self.cache.clear_pattern("*recommendations*")
        logger.info(f"Invalidated all recommendation caches ({deleted} entries)")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def demonstrate_caching():
    """Demonstrate caching strategies."""

    logger.info("\n" + "="*80)
    logger.info("Caching Strategies - LRU Cache & Redis Demonstration")
    logger.info("="*80 + "\n")

    # ---- 1. FIBONACCI BENCHMARKING ----
    logger.info("[1] Fibonacci - Cache vs No Cache Benchmark")
    logger.info("-" * 80)

    test_values = [25, 30, 35]
    for n in test_values:
        time_no_cache, time_with_cache, speedup = FibonacciCalculator.benchmark_fibonacci(n)

        logger.info(f"\nFibonacci({n}):")
        if time_no_cache != float('inf'):
            logger.info(f"  Without cache: {time_no_cache*1000:.2f}ms")
        else:
            logger.info(f"  Without cache: too slow (skipped)")
        logger.info(f"  With cache: {time_with_cache*1000:.2f}ms")
        logger.info(f"  Speedup: {speedup}x" if speedup != "∞" else f"  Speedup: infinite")

    # ---- 2. CUSTOM TTL CACHE ----
    logger.info("\n[2] Custom TTL Cache Demonstration")
    logger.info("-" * 80)

    @timed_lru_cache(maxsize=100, ttl_seconds=2)
    def expensive_computation(x: int) -> int:
        """Simulate expensive computation."""
        logger.info(f"  Computing for x={x}...")
        time.sleep(0.1)
        return x ** 2

    logger.info("First call (computes):")
    result1 = expensive_computation(5)
    logger.info(f"  Result: {result1}")

    logger.info("Second call (cached):")
    result2 = expensive_computation(5)
    logger.info(f"  Result: {result2} (from cache)")

    logger.info("Cache info:", expensive_computation.cache_info())

    # ---- 3. RECOMMENDATION ENGINE ----
    logger.info("\n[3] Recommendation Engine with Caching")
    logger.info("-" * 80)

    rec_engine = RecommendationEngine()

    logger.info("Getting recommendations for user 123 (first time):")
    with PerformanceTimer("First call") as timer:
        recs = rec_engine.get_user_recommendations(123, limit=5)
    logger.info(f"  Time: {timer.elapsed*1000:.2f}ms")
    logger.info(f"  Recommendations: {len(recs)} items")

    logger.info("Getting recommendations for user 123 (cached):")
    with PerformanceTimer("Second call") as timer:
        recs = rec_engine.get_user_recommendations(123, limit=5)
    logger.info(f"  Time: {timer.elapsed*1000:.2f}ms")

    # ---- 4. ML PREDICTION SERVICE ----
    logger.info("\n[4] ML Prediction Service")
    logger.info("-" * 80)

    ml_service = MLPredictionService()

    logger.info("First prediction (computes model):")
    with PerformanceTimer("First prediction") as timer:
        pred1 = ml_service.predict_user_churn(100)
    logger.info(f"  Time: {timer.elapsed*1000:.2f}ms")
    logger.info(f"  Churn Probability: {pred1['churn_probability']:.2%}")

    logger.info("Second prediction (cached):")
    if redis_client:
        with PerformanceTimer("Second prediction") as timer:
            pred2 = ml_service.predict_user_churn(100)
        logger.info(f"  Time: {timer.elapsed*1000:.2f}ms")
    else:
        logger.info("  (Redis not available)")

    # ---- 5. CACHE INVALIDATION ----
    logger.info("\n[5] Cache Invalidation Strategy")
    logger.info("-" * 80)

    if redis_client:
        cache = RedisCache(redis_client)
        invalidation_manager = CacheInvalidationManager(cache)

        logger.info("Setting sample cache entries...")
        cache.set("user:123:recommendations", ["item1", "item2", "item3"])
        cache.set("user:123:profile", {"name": "John", "score": 85})
        cache.set("category:electronics:trending", ["phone", "laptop"])

        logger.info("Invalidating user 123 cache...")
        invalidation_manager.invalidate_user_cache(123)

        logger.info("Cache entries after invalidation:")
        logger.info(f"  User recommendations: {cache.get('user:123:recommendations')}")
    else:
        logger.info("Redis not available for invalidation demo")

    logger.info("\n" + "="*80)
    logger.info("✓ Caching demonstration completed")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    demonstrate_caching()
