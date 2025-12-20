"""Rate limiting utilities using Redis"""

import time
import logging
from typing import Optional
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiting"""

    def __init__(self, key: str, max_requests: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            key: Unique identifier for limit
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        self.key = key
        self.max_requests = max_requests
        self.time_window = time_window

    def is_allowed(self) -> bool:
        """
        Check if request is allowed.

        Returns:
            True if within limit, False if exceeded
        """
        current = cache.get(self.key, 0)

        if current >= self.max_requests:
            logger.warning(f'Rate limit exceeded for: {self.key}')
            return False

        # Increment counter
        cache.incr(self.key)

        # Set expiration on first request
        if current == 0:
            cache.expire(self.key, self.time_window)

        return True

    def get_remaining(self) -> int:
        """Get remaining requests"""
        current = cache.get(self.key, 0)
        return max(0, self.max_requests - current)

    def reset(self) -> None:
        """Reset counter"""
        cache.delete(self.key)


class SlidingWindowLimiter:
    """Sliding window rate limiting (more accurate)"""

    def __init__(self, key: str, max_requests: int, time_window: int):
        """
        Initialize sliding window limiter.

        Args:
            key: Unique identifier
            max_requests: Maximum requests
            time_window: Time window in seconds
        """
        self.key = key
        self.max_requests = max_requests
        self.time_window = time_window

    def is_allowed(self) -> bool:
        """Check if request is allowed with sliding window"""
        now = time.time()
        window_start = now - self.time_window

        # Get all requests in time window
        requests = cache.get(self.key, [])
        requests = [r for r in requests if r > window_start]

        if len(requests) >= self.max_requests:
            logger.warning(f'Sliding window limit exceeded: {self.key}')
            return False

        # Add current request
        requests.append(now)
        cache.set(self.key, requests, self.time_window)

        return True

    def get_remaining(self) -> int:
        """Get remaining requests"""
        now = time.time()
        window_start = now - self.time_window

        requests = cache.get(self.key, [])
        requests = [r for r in requests if r > window_start]

        return max(0, self.max_requests - len(requests))


class LeakyBucketLimiter:
    """Leaky bucket rate limiting (smooth distribution)"""

    def __init__(self, key: str, capacity: int, leak_rate: float):
        """
        Initialize leaky bucket limiter.

        Args:
            key: Unique identifier
            capacity: Bucket capacity
            leak_rate: Leak rate (items per second)
        """
        self.key = key
        self.capacity = capacity
        self.leak_rate = leak_rate

    def is_allowed(self) -> bool:
        """Check if request is allowed with leaky bucket"""
        state = cache.get(self.key, {
            'water': 0,
            'last_update': time.time()
        })

        # Leak water from bucket
        now = time.time()
        time_passed = now - state.get('last_update', now)
        state['water'] = max(0, state['water'] - time_passed * self.leak_rate)
        state['last_update'] = now

        # Check capacity
        if state['water'] >= self.capacity:
            logger.warning(f'Leaky bucket full: {self.key}')
            return False

        # Add request
        state['water'] += 1
        cache.set(self.key, state, timeout=self.capacity)

        return True


class DomainRateLimiter:
    """Rate limit per domain for web scraping"""

    def __init__(self, min_delay: float = 1.0):
        """
        Initialize domain rate limiter.

        Args:
            min_delay: Minimum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.last_request_time = {}

    def wait_if_needed(self, domain: str) -> None:
        """Wait if domain was accessed too recently"""
        if domain in self.last_request_time:
            time_since_last = time.time() - self.last_request_time[domain]
            if time_since_last < self.min_delay:
                sleep_time = self.min_delay - time_since_last
                logger.debug(f'Rate limiting {domain}: sleeping {sleep_time:.2f}s')
                time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()


class APIRateLimiter:
    """Rate limit API endpoints"""

    @staticmethod
    def check_user_limit(user_id: int, limit: int = 100, period: int = 3600) -> bool:
        """Check if user exceeded API limit"""
        key = f'api:user:{user_id}'
        limiter = RateLimiter(key, limit, period)
        return limiter.is_allowed()

    @staticmethod
    def check_ip_limit(ip_address: str, limit: int = 1000, period: int = 3600) -> bool:
        """Check if IP exceeded API limit"""
        key = f'api:ip:{ip_address}'
        limiter = RateLimiter(key, limit, period)
        return limiter.is_allowed()

    @staticmethod
    def get_user_remaining(user_id: int, limit: int = 100, period: int = 3600) -> int:
        """Get remaining requests for user"""
        key = f'api:user:{user_id}'
        limiter = RateLimiter(key, limit, period)
        return limiter.get_remaining()


# Usage examples (documentation)
"""
# Token Bucket (simple)
limiter = RateLimiter('api_requests', max_requests=100, time_window=60)
if limiter.is_allowed():
    # Process request
else:
    # Return 429 Too Many Requests

# Sliding Window (accurate)
limiter = SlidingWindowLimiter('scraper:example.com', 10, 60)
if not limiter.is_allowed():
    # Blocked by rate limit

# Leaky Bucket (smooth)
limiter = LeakyBucketLimiter('queue:processing', 10, 1.0)
if limiter.is_allowed():
    # Process task

# Domain rate limiting (for Scrapy)
domain_limiter = DomainRateLimiter(min_delay=2.0)
domain_limiter.wait_if_needed('example.com')  # Enforce 2s delay

# API rate limiting
if not APIRateLimiter.check_user_limit(user_id=123):
    # User exceeded limit, return 429

remaining = APIRateLimiter.get_user_remaining(user_id=123)
# Remaining request count can be returned in API headers

# Middleware usage
class RateLimitMiddleware:
    def __call__(self, request):
        ip = request.META['REMOTE_ADDR']
        if not APIRateLimiter.check_ip_limit(ip):
            return JsonResponse({'error': 'Rate limited'}, status=429)
        return self.get_response(request)
"""
