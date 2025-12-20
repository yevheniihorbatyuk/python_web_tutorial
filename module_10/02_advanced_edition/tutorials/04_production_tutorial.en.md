# Tutorial: Production Patterns and Monitoring

**Goal**: Apply production-ready patterns like caching and rate limiting to your integrated scraping application.

---

## Step 1: Implementing Caching

We will add caching to a Django view that serves scraped data.

1.  **Configure Django for Redis caching.** Open your `settings.py` and add the `CACHES` setting:
    ```python
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1", # Use a different DB than Celery
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
    ```
    You may need to install `django-redis`: `pip install django-redis`.

2.  **Create a cached view.** In `django_integration/views.py`, create a view to serve quotes that uses the cache-aside pattern.
    ```python
    from django.core.cache import cache
    from django.http import JsonResponse
    from .models import Quote

    def cached_quote_list(request):
        cache_key = "all_quotes"
        quotes = cache.get(cache_key)
        
        if quotes is None:
            # Cache miss: fetch from DB, then set cache
            quotes = list(Quote.objects.values('text', 'author__name'))
            cache.set(cache_key, quotes, timeout=60 * 15) # Cache for 15 minutes
            print("Cache miss - fetched from DB.")
        else:
            print("Cache hit!")
            
        return JsonResponse(quotes, safe=False)
    ```

3.  **Add a URL** for this view and test it. Hit the endpoint multiple times; you should see "Cache miss" only on the first request.

---

## Step 2: Implementing Rate Limiting

We'll create a simple rate limiter using Redis to protect an API endpoint.

1.  **Create a rate limiter utility** in `code/utils/rate_limiter.py`.
    ```python
    import redis
    from datetime import timedelta

    client = redis.Redis(host='localhost', port=6379, db=2)

    def is_rate_limited(key: str, limit: int, period: timedelta):
        """
        Returns True if the key is rate-limited, False otherwise.
        """
        if client.setnx(key, limit):
            client.expire(key, int(period.total_seconds()))
        
        bucket_val = client.get(key)
        if bucket_val and int(bucket_val) > 0:
            client.decrby(key, 1)
            return False
        
        return True
    ```

2.  **Apply the rate limiter in a view.**
    ```python
    from .utils.rate_limiter import is_rate_limited
    from datetime import timedelta

    def protected_view(request):
        # Limit to 10 requests per minute per IP
        ip_address = request.META.get('REMOTE_ADDR')
        key = f"rate_limit:{ip_address}"
        
        if is_rate_limited(key, limit=10, period=timedelta(minutes=1)):
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
        return JsonResponse({'message': 'Success'})
    ```

---

## Step 3: Setting Up Structured Logging

We will configure Django to output logs in JSON format.

1.  **Install `python-json-logger`**:
    ```bash
    pip install python-json-logger
    ```
2.  **Configure `LOGGING` in `settings.py`**:
    ```python
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'my_app': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
    ```

3.  **Use the logger with extra context**:
    ```python
    import logging
    logger = logging.getLogger(__name__)

    def my_view(request):
        logger.info("User accessed the page.", extra={
            'user_id': request.user.id,
            'path': request.path,
        })
        # ...
    ```
    When you run your server, you will now see logs formatted as JSON objects.
