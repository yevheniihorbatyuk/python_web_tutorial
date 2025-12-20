"""Redis caching utilities"""

import json
import logging
from typing import Any, Optional, Callable
from datetime import timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage caching with different strategies"""

    # Cache-Aside Pattern
    @staticmethod
    def get_or_fetch(
        key: str,
        fetch_func: Callable[[], Any],
        timeout: int = 3600,
    ) -> Any:
        """
        Get from cache, or fetch and cache if missing.

        Args:
            key: Cache key
            fetch_func: Function to call if cache miss
            timeout: Cache TTL in seconds

        Returns:
            Cached or fetched value
        """
        # Check cache first
        value = cache.get(key)

        if value is None:
            logger.debug(f'Cache miss: {key}')
            # Fetch from source
            value = fetch_func()
            # Store in cache
            cache.set(key, value, timeout=timeout)
            logger.debug(f'Cached: {key}')
        else:
            logger.debug(f'Cache hit: {key}')

        return value

    # Write-Through Pattern
    @staticmethod
    def set_and_cache(key: str, value: Any, timeout: int = 3600) -> None:
        """
        Cache value with timestamp.

        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache TTL in seconds
        """
        cache.set(key, value, timeout=timeout)
        logger.info(f'Cached: {key}')

    # Invalidation
    @staticmethod
    def invalidate(key: str) -> None:
        """Remove from cache"""
        cache.delete(key)
        logger.info(f'Invalidated: {key}')

    @staticmethod
    def invalidate_pattern(pattern: str) -> None:
        """Remove all keys matching pattern"""
        keys = cache.keys(pattern)
        if keys:
            cache.delete_many(keys)
            logger.info(f'Invalidated {len(keys)} keys matching: {pattern}')

    # Batch operations
    @staticmethod
    def get_many(keys: list) -> dict:
        """Get multiple values at once"""
        return cache.get_many(keys)

    @staticmethod
    def set_many(data: dict, timeout: int = 3600) -> None:
        """Set multiple values at once"""
        cache.set_many(data, timeout=timeout)
        logger.info(f'Cached {len(data)} items')

    # TTL
    @staticmethod
    def get_ttl(key: str) -> Optional[int]:
        """Get remaining TTL for key"""
        return cache.ttl(key)


class QuoteCache:
    """Quote-specific caching"""

    PREFIX = 'quote'

    @classmethod
    def get_quote(cls, quote_id: int) -> Optional[dict]:
        """Get quote from cache"""
        key = f'{cls.PREFIX}:{quote_id}'
        return cache.get(key)

    @classmethod
    def set_quote(cls, quote_id: int, quote: dict, timeout: int = 3600) -> None:
        """Cache quote"""
        key = f'{cls.PREFIX}:{quote_id}'
        cache.set(key, quote, timeout=timeout)

    @classmethod
    def get_popular_quotes(cls, limit: int = 10) -> Optional[list]:
        """Get popular quotes from cache"""
        key = f'{cls.PREFIX}:popular:{limit}'
        return cache.get(key)

    @classmethod
    def set_popular_quotes(cls, quotes: list, limit: int = 10, timeout: int = 3600) -> None:
        """Cache popular quotes"""
        key = f'{cls.PREFIX}:popular:{limit}'
        cache.set(key, quotes, timeout=timeout)

    @classmethod
    def invalidate_quote(cls, quote_id: int) -> None:
        """Remove quote from cache"""
        key = f'{cls.PREFIX}:{quote_id}'
        cache.delete(key)
        # Also invalidate popular quotes list
        cache.delete_many([k for k in cache.keys(f'{cls.PREFIX}:popular:*')])


class BookCache:
    """Book-specific caching"""

    PREFIX = 'book'

    @classmethod
    def get_book(cls, book_id: int) -> Optional[dict]:
        """Get book from cache"""
        key = f'{cls.PREFIX}:{book_id}'
        return cache.get(key)

    @classmethod
    def set_book(cls, book_id: int, book: dict, timeout: int = 3600) -> None:
        """Cache book"""
        key = f'{cls.PREFIX}:{book_id}'
        cache.set(key, book, timeout=timeout)

    @classmethod
    def get_by_category(cls, category: str, limit: int = 20) -> Optional[list]:
        """Get books by category from cache"""
        key = f'{cls.PREFIX}:category:{category}:{limit}'
        return cache.get(key)

    @classmethod
    def set_by_category(cls, category: str, books: list, limit: int = 20, timeout: int = 3600) -> None:
        """Cache books by category"""
        key = f'{cls.PREFIX}:category:{category}:{limit}'
        cache.set(key, books, timeout=timeout)

    @classmethod
    def invalidate_category(cls, category: str) -> None:
        """Remove category from cache"""
        cache.delete_many([k for k in cache.keys(f'{cls.PREFIX}:category:{category}:*')])


# Usage examples (documentation)
"""
# Cache-Aside Pattern
def get_quote(quote_id):
    def fetch():
        return Quote.objects.get(id=quote_id)

    quote = CacheManager.get_or_fetch(
        f'quote:{quote_id}',
        fetch,
        timeout=3600
    )
    return quote


# Write-Through Pattern
def update_quote(quote_id, data):
    quote = Quote.objects.get(id=quote_id)
    quote.text = data['text']
    quote.save()

    CacheManager.set_and_cache(
        f'quote:{quote_id}',
        quote,
        timeout=3600
    )


# Quote-specific
quote = QuoteCache.get_quote(1)
if not quote:
    quote = Quote.objects.get(id=1)
    QuoteCache.set_quote(1, quote)


# Batch
quotes = cache.get_many(['quote:1', 'quote:2', 'quote:3'])
"""
