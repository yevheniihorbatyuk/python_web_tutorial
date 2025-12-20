from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import Callable, Optional

import redis


@lru_cache(maxsize=256)
def fib_cached(n: int) -> int:
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def fib_plain(n: int) -> int:
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


def benchmark(fn: Callable[[int], int], n: int) -> float:
    started = time.perf_counter()
    fn(n)
    return time.perf_counter() - started


def redis_cache_example(key: str, compute: Callable[[], str]) -> str:
    """Cache-aside через Redis, graceful fallback якщо сервіс недоступний."""
    try:
        client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", "6379")))
        cached: Optional[bytes] = client.get(key)
        if cached:
            return cached.decode()
        value = compute()
        client.setex(key, 60, value)  # TTL 60s
        return value
    except Exception:
        return compute()


def main() -> None:
    target = 36
    cold_plain = benchmark(fib_plain, target)
    cold_cached = benchmark(fib_cached, target)
    warm_cached = benchmark(fib_cached, target)

    print(f"fib_plain({target}) cold:  {cold_plain:.4f}s")
    print(f"fib_cached({target}) cold: {cold_cached:.4f}s")
    print(f"fib_cached({target}) warm: {warm_cached:.6f}s (L1 hit)")

    # Демонстрація cache-aside через Redis
    def expensive_geo_lookup() -> str:
        time.sleep(0.2)  # імітація повільного I/O
        return "Kyiv, Lviv, Odesa"

    result = redis_cache_example("cities:UA", expensive_geo_lookup)
    print("Cities from cache-aside:", result)


if __name__ == "__main__":
    main()
