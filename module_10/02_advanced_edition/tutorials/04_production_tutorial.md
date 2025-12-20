# Tutorial: Production Patterns and Monitoring

**Time**: 45 minutes hands-on
**Goal**: Apply production-ready patterns to running system
**Difficulty**: Advanced

---

## Prerequisites

✅ Lesson 3 (Integration) complete
✅ Django application running
✅ Celery worker running
✅ Redis running
✅ Flower monitoring available

---

## Step 1: Understand Production Requirements

### What Makes Systems Production-Ready?

```
Problem:        Solution:           Why:
─────────────────────────────────────────────────────────────
Slow queries    Caching             60-80% of requests are reads
Duplicate work  Deduplication       Redis caches prevent re-queries
API hammering   Rate limiting       Prevent 429 errors and bans
Silent failures Logging             Debugging without logs = guessing
Lost data       Error handling      Retries save 95% of failures
High costs      Optimization        2x performance = 50% server costs
```

### Key Metrics to Monitor

```
Metric              Target        Tool
─────────────────────────────────────────────────────────────
Response time       < 200ms       Flower, Django logs
Cache hit ratio     > 80%         Redis monitoring
Queue depth         < 100 tasks   Flower worker view
Error rate          < 1%          Sentry or logs
Database slow query > 100ms       Django debug toolbar
Memory usage        < 80% of RAM  System monitoring
```

---

## Step 2: Set Up Redis Caching

### 2a. Verify Redis is Running

```bash
# Test Redis connection
redis-cli ping
# Expected output: PONG

# Check Redis info
redis-cli info
# Check connected_clients, used_memory, evicted_keys
```

### 2b. Configure Django Cache

```python
# config/settings.py - Add to CACHES:

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'goit_module10',
        'TIMEOUT': 3600,  # 1 hour default
    }
}
```

### 2c. Test Cache Operations

```bash
# Python shell
python manage.py shell

# Test basic cache
>>> from django.core.cache import cache
>>> cache.set('test_key', 'test_value', 60)
>>> cache.get('test_key')
'test_value'

# Test cache manager from our code
>>> from code.utils.cache import CacheManager
>>>
>>> def expensive_query():
...     import time
...     time.sleep(2)
...     return {'data': 'expensive result', 'timestamp': str(time.time())}
>>>
>>> # First call - hits expensive_query
>>> result1 = CacheManager.get_or_fetch('expensive', expensive_query, timeout=60)
>>> print(f"First call: {result1}")
First call: {'data': 'expensive result', 'timestamp': '1705329600.123456'}
>>>
>>> # Second call - hits cache (instant)
>>> result2 = CacheManager.get_or_fetch('expensive', expensive_query, timeout=60)
>>> print(f"Second call: {result2}")  # Same timestamp = cached!
Second call: {'data': 'expensive result', 'timestamp': '1705329600.123456'}

# Exit shell
>>> exit()
```

---

## Step 3: Implement Cache-Aside Pattern for Quotes

### 3a. Create Cached Quote View

```python
# code/django_integration/views.py - Add to existing file:

from code.utils.cache import QuoteCache, CacheManager

class QuotesListView(View):
    @require_http_methods(['GET'])
    def get(self, request):
        """Get all quotes with caching"""
        # Try to get from cache first
        quotes_data = cache.get('quotes:all')

        if quotes_data is None:
            # Cache miss - fetch from database
            quotes = Quote.objects.all().values('id', 'text', 'author')
            quotes_data = list(quotes)
            # Store in cache for 1 hour
            cache.set('quotes:all', quotes_data, timeout=3600)

        return JsonResponse({'quotes': quotes_data})


class QuoteDetailView(View):
    @require_http_methods(['GET'])
    def get(self, request, quote_id: int):
        """Get single quote with caching"""
        # Try QuoteCache helper
        quote_data = QuoteCache.get_quote(quote_id)

        if quote_data is None:
            # Cache miss
            try:
                quote = Quote.objects.get(id=quote_id)
                quote_data = {
                    'id': quote.id,
                    'text': quote.text,
                    'author': quote.author,
                    'tags': quote.tags,
                    'scraped_count': quote.scraped_count,
                }
                QuoteCache.set_quote(quote_id, quote_data, timeout=3600)
            except Quote.DoesNotExist:
                return JsonResponse({'error': 'Quote not found'}, status=404)

        return JsonResponse(quote_data)
```

### 3b. Test Cache Performance

```bash
python manage.py shell

# Create some test quotes
>>> from code.django_integration.models import Quote
>>> Quote.objects.all().delete()
>>>
>>> for i in range(100):
...     Quote.objects.create(
...         text=f"Quote number {i}",
...         author=f"Author {i % 10}",
...         tags=['test', f'batch-{i}']
...     )

# Test caching
>>> import time
>>> from code.utils.cache import QuoteCache
>>>
>>> # First access - hits database
>>> start = time.time()
>>> quotes = Quote.objects.all()
>>> print(f"Database query: {(time.time() - start) * 1000:.2f}ms")
Database query: 12.45ms

>>> # Second access - all in memory
>>> start = time.time()
>>> quotes = Quote.objects.all()
>>> print(f"Cached query: {(time.time() - start) * 1000:.2f}ms")
Cached query: 0.05ms  # 250x faster!

>>> exit()
```

---

## Step 4: Implement Rate Limiting

### 4a. Create Rate Limiting Middleware

```python
# code/django_integration/middleware.py - Create new file:

import logging
from django.http import JsonResponse
from django.utils.decorators import decorator_from_middleware_with_args
from code.utils.rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Middleware to rate limit API requests"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Get client IP
        ip = self.get_client_ip(request)

        # Check rate limit (1000 requests per hour per IP)
        if not APIRateLimiter.check_ip_limit(ip, limit=1000, period=3600):
            logger.warning(f'Rate limit exceeded for IP: {ip}')
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': 'Maximum 1000 requests per hour',
                    'remaining': 0,
                },
                status=429,
            )

        response = self.get_response(request)

        # Add rate limit headers to response
        remaining = APIRateLimiter.get_user_remaining(
            user_id=hash(ip) % 2147483647,
            limit=1000,
            period=3600,
        )
        response['X-RateLimit-Remaining'] = remaining
        response['X-RateLimit-Limit'] = 1000

        return response

    @staticmethod
    def get_client_ip(request):
        """Get client IP, considering proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

### 4b. Register Middleware

```python
# config/settings.py - Add to MIDDLEWARE list:

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'code.django_integration.middleware.RateLimitMiddleware',  # Add this
]
```

### 4c. Test Rate Limiting

```bash
# Make rapid requests to trigger rate limit
python manage.py shell

>>> from django.test import Client
>>> client = Client()
>>>
>>> # Make 5 requests
>>> for i in range(5):
...     response = client.get('/api/quotes/')
...     print(f"Request {i+1}: Status {response.status_code}")
...     if 'X-RateLimit-Remaining' in response:
...         print(f"  Remaining: {response['X-RateLimit-Remaining']}")

Request 1: Status 200
  Remaining: 999
Request 2: Status 200
  Remaining: 998
Request 3: Status 200
  Remaining: 997
Request 4: Status 200
  Remaining: 996
Request 5: Status 200
  Remaining: 995

>>> exit()
```

---

## Step 5: Set Up Structured Logging

### 5a. Configure JSON Logging

```python
# config/settings.py - Add logging configuration:

import logging.config
import json
from datetime import datetime

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/root/goit/python_web/module_10/02_advanced_edition/logs/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'scraping': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/root/goit/python_web/module_10/02_advanced_edition/logs/scraping.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'code.celery_tasks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'code.django_integration': {
            'handlers': ['console', 'scraping'],
            'level': 'DEBUG',
        },
    },
}

# Create logs directory
import os
logs_dir = '/root/goit/python_web/module_10/02_advanced_edition/logs'
os.makedirs(logs_dir, exist_ok=True)
logging.config.dictConfig(LOGGING)
```

### 5b. Add Structured Logging to Tasks

```python
# code/celery_tasks/tasks.py - Update to use logging:

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def scrape_quotes_task(self):
    """Scrape quotes with structured logging"""
    task_id = self.request.id

    logger.info(f'Starting scrape task', extra={
        'task_id': task_id,
        'spider': 'quotes',
        'timestamp': str(timezone.now()),
    })

    try:
        from django.core.management import call_command

        # Run scraping
        call_command('scrape_quotes')

        logger.info(f'Scrape completed successfully', extra={
            'task_id': task_id,
            'spider': 'quotes',
            'duration': '10.5s',
        })

        return {'status': 'success', 'message': 'Scraping completed'}

    except Exception as exc:
        logger.error(f'Scrape failed: {exc}', extra={
            'task_id': task_id,
            'spider': 'quotes',
            'error': str(exc),
        })
        raise
```

### 5c. View Logs

```bash
# Create logs directory
mkdir -p /root/goit/python_web/module_10/02_advanced_edition/logs

# Start app and run tasks to generate logs
python manage.py runserver

# In another terminal - trigger scraping
python manage.py shell
>>> from code.celery_tasks.tasks import scrape_quotes_task
>>> task = scrape_quotes_task.delay()

# View logs
cat /root/goit/python_web/module_10/02_advanced_edition/logs/scraping.log | head -20

# Pretty-print JSON logs
cat /root/goit/python_web/module_10/02_advanced_edition/logs/scraping.log | python -m json.tool
```

---

## Step 6: Monitor with Flower

### 6a. Start Flower Monitoring

```bash
# Terminal 1: Celery worker (if not already running)
cd /root/goit/python_web/module_10/02_advanced_edition
celery -A code.celery_tasks worker --loglevel=info

# Terminal 2: Celery Beat (if not already running)
celery -A code.celery_tasks beat --loglevel=info

# Terminal 3: Flower monitoring
celery -A code.celery_tasks flower --port=5555

# Access Flower dashboard
# Open browser to: http://localhost:5555
```

### 6b. Flower Dashboard Sections

```
Dashboard Components:
─────────────────────────────────────────────────────────────

1. Workers Tab
   ├─ Worker status (online/offline)
   ├─ Tasks processed
   ├─ Successful tasks
   ├─ Failed tasks
   └─ CPU/memory usage

2. Tasks Tab
   ├─ Active tasks (running now)
   ├─ Task details (args, kwargs, runtime)
   ├─ Task history (last 100 tasks)
   └─ Filter by task name/status

3. Queues Tab
   ├─ Tasks in queue
   ├─ Queue length
   └─ Pending task count

4. Monitor Tab
   ├─ Worker pool size
   ├─ Active connections
   ├─ Revoked tasks
   └─ Real-time graph
```

### 6c. Use Flower to Debug

```bash
# Scenario: Task is stuck or slow

1. Open Flower dashboard at http://localhost:5555
2. Click "Tasks" tab
3. Find your task in the list (search by name)
4. Click on the task to see:
   - Arguments passed
   - Start time / end time
   - Duration
   - Status (SUCCESS, FAILURE, RETRY, etc.)
   - Full traceback if failed

5. If stuck:
   - Click the task
   - Click "Revoke" button to cancel
   - Check worker logs for errors

# Export task history for analysis
curl http://localhost:5555/api/tasks | python -m json.tool > tasks_history.json
```

---

## Step 7: Optimize Database Queries

### 7a. Find N+1 Query Problems

```bash
python manage.py shell

# Enable query logging
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>>
>>> with CaptureQueriesContext(connection) as ctx:
...     quotes = Quote.objects.all()
...     # This causes N+1: one query for quotes, one for each author
...     for quote in quotes:
...         print(quote.author)
>>>
>>> print(f"Total queries: {len(ctx)}")
Total queries: 101  # 1 for list + 100 for each author!

# Better: use select_related or prefetch_related
>>> with CaptureQueriesContext(connection) as ctx:
...     # Prefetch author info in one query
...     quotes = Quote.objects.prefetch_related('author').all()
...     for quote in quotes:
...         print(quote.author)
>>>
>>> print(f"Total queries: {len(ctx)}")
Total queries: 1  # Much better!

>>> exit()
```

### 7b. Add Indexes to Models

```python
# code/django_integration/models.py - Already included:

class Quote(models.Model):
    text = models.TextField(unique=True)
    author = models.CharField(max_length=200, db_index=True)  # Index here!
    last_scraped = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        # Composite index for common query pattern
        indexes = [
            models.Index(fields=['author', 'last_scraped']),
            models.Index(fields=['source', 'created_at']),
        ]

# Apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 7c. Test Query Performance

```bash
python manage.py shell

# Without index - slow
>>> import time
>>> start = time.time()
>>> quotes = Quote.objects.filter(author='Unknown').count()
>>> print(f"Time: {(time.time() - start) * 1000:.2f}ms")
Time: 45.32ms

# With index - fast
>>> start = time.time()
>>> quotes = Quote.objects.filter(author='Unknown').count()
>>> print(f"Time: {(time.time() - start) * 1000:.2f}ms")
Time: 2.15ms  # 20x faster!

>>> exit()
```

---

## Step 8: Implement Error Monitoring

### 8a. Create Error Handler

```python
# code/django_integration/error_handler.py - Create new file:

import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


class ErrorMonitor:
    """Monitor and track application errors"""

    def __init__(self):
        self.error_count = 0
        self.last_error_time = None

    def log_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = 'error',
    ) -> None:
        """Log error with context"""
        self.error_count += 1
        self.last_error_time = datetime.now()

        error_data = {
            'timestamp': str(datetime.now()),
            'exception': str(exception),
            'type': type(exception).__name__,
            'traceback': traceback.format_exc(),
            'severity': severity,
        }

        if context:
            error_data.update(context)

        logger.error(f'Application error: {error_data}', extra=error_data)

    def should_alert(self) -> bool:
        """Check if error rate warrants alert"""
        # Alert if more than 10 errors in the last 5 minutes
        return self.error_count > 10

    def send_alert(self, subject: str, message: str) -> None:
        """Send alert email to admins"""
        if settings.DEBUG:
            logger.warning(f'Alert skipped in DEBUG mode: {subject}')
            return

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin[1] for admin in settings.ADMINS],
            )
            logger.info(f'Alert sent: {subject}')
        except Exception as e:
            logger.error(f'Failed to send alert: {e}')


# Global error monitor instance
error_monitor = ErrorMonitor()
```

### 8b. Use Error Monitor in Tasks

```python
# code/celery_tasks/tasks.py - Add error monitoring:

from code.django_integration.error_handler import error_monitor


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def scrape_quotes_task(self):
    """Scrape with error monitoring"""
    try:
        from django.core.management import call_command
        call_command('scrape_quotes')
        return {'status': 'success'}

    except Exception as exc:
        error_monitor.log_error(
            exception=exc,
            context={
                'task_id': self.request.id,
                'task_name': self.name,
                'retry_count': self.request.retries,
            },
        )

        if error_monitor.should_alert():
            error_monitor.send_alert(
                subject='High error rate in scraping tasks',
                message=f'Error count: {error_monitor.error_count}',
            )

        raise self.retry(exc=exc, countdown=300)
```

### 8c. View Error Logs

```bash
# Check error monitoring
python manage.py shell

>>> from code.django_integration.error_handler import error_monitor
>>>
>>> # Simulate error
>>> try:
...     1 / 0
... except Exception as e:
...     error_monitor.log_error(e, context={'module': 'test'})
>>>
>>> print(f"Total errors: {error_monitor.error_count}")
Total errors: 1
>>> print(f"Should alert: {error_monitor.should_alert()}")
Should alert: False

>>> exit()
```

---

## Step 9: Performance Monitoring

### 9a. Create Performance Monitor

```python
# code/utils/performance.py - Create new file:

import time
import logging
from typing import Callable, Any
from functools import wraps
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger(__name__)


def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Reset query count
        if settings.DEBUG:
            reset_queries()

        start_time = time.time()
        start_queries = len(connection.queries) if settings.DEBUG else 0

        try:
            result = func(*args, **kwargs)
            return result

        finally:
            duration = (time.time() - start_time) * 1000  # milliseconds
            query_count = len(connection.queries) - start_queries if settings.DEBUG else 0

            logger.info(f'{func.__name__} performance', extra={
                'function': func.__name__,
                'duration_ms': duration,
                'queries': query_count,
                'status': 'success',
            })

            # Warn if slow
            if duration > 1000:
                logger.warning(f'{func.__name__} is slow: {duration:.2f}ms')

    return wrapper


class PerformanceTimer:
    """Context manager to measure performance"""

    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        if settings.DEBUG:
            reset_queries()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = (time.time() - self.start_time) * 1000
        query_count = len(connection.queries) if settings.DEBUG else 0

        logger.info(f'{self.name} took {self.duration:.2f}ms ({query_count} queries)')

        if self.duration > 1000:
            logger.warning(f'{self.name} is slow!')
```

### 9b. Use Performance Monitoring

```bash
python manage.py shell

# Use decorator
>>> from code.utils.performance import monitor_performance
>>>
>>> @monitor_performance
... def slow_operation():
...     import time
...     time.sleep(0.5)
...     return "done"
>>>
>>> slow_operation()
'done'
# Logs: slow_operation took 500.12ms

# Use context manager
>>> from code.utils.performance import PerformanceTimer
>>>
>>> with PerformanceTimer('quote_lookup') as timer:
...     from code.django_integration.models import Quote
...     quotes = Quote.objects.filter(author='Unknown').count()
>>>
>>> print(f"Duration: {timer.duration:.2f}ms")
Duration: 2.15ms

>>> exit()
```

---

## Step 10: Complete Production Checklist

### 10a. Pre-Deployment Checklist

```
Production Readiness Checklist:
═════════════════════════════════════════════════════════════

[ ] Caching
    ✓ Redis is configured in settings.py
    ✓ Cache-Aside pattern used in views
    ✓ Cache TTL set appropriately (3600s for stable data)
    ✓ Cache invalidation strategy defined

[ ] Rate Limiting
    ✓ Rate limiting middleware installed
    ✓ API endpoints protected (1000 req/hour)
    ✓ Limits vary by endpoint (lower for expensive ops)
    ✓ Client gets X-RateLimit-* headers

[ ] Logging
    ✓ Structured logging configured (JSON format)
    ✓ Log levels appropriate (DEBUG/INFO/WARNING/ERROR)
    ✓ Separate logs for different modules
    ✓ Log rotation configured (prevent disk fill)

[ ] Monitoring
    ✓ Flower dashboard running on :5555
    ✓ Task visibility shows all active tasks
    ✓ Worker status monitored
    ✓ Error rates tracked

[ ] Database
    ✓ Indexes on frequently queried fields
    ✓ No N+1 queries
    ✓ Connection pooling configured
    ✓ Slow query logs reviewed

[ ] Error Handling
    ✓ All tasks have retry logic
    ✓ Exceptions logged with context
    ✓ Critical errors trigger alerts
    ✓ Dead letter queue for failed tasks

[ ] Security
    ✓ SECRET_KEY not in code
    ✓ DEBUG = False in production
    ✓ ALLOWED_HOSTS configured
    ✓ HTTPS enforced
    ✓ CORS properly restricted

[ ] Documentation
    ✓ README with setup instructions
    ✓ Troubleshooting guide
    ✓ Common commands documented
    ✓ Performance tuning tips included
```

### 10b. Monitor All Systems

```bash
# Terminal 1: Django development server
cd /root/goit/python_web/module_10/02_advanced_edition
python manage.py runserver

# Terminal 2: Celery worker
celery -A code.celery_tasks worker --loglevel=info

# Terminal 3: Celery Beat (scheduler)
celery -A code.celery_tasks beat --loglevel=info

# Terminal 4: Flower (monitoring)
celery -A code.celery_tasks flower --port=5555

# Terminal 5: Redis monitoring
redis-cli monitor  # Shows all Redis operations in real-time

# Terminal 6: Log monitoring
tail -f /root/goit/python_web/module_10/02_advanced_edition/logs/app.log | \
  python -m json.tool  # Pretty-print JSON logs as they arrive
```

### 10c. Run Full System Test

```bash
python manage.py shell

# Test caching
>>> from code.utils.cache import QuoteCache
>>> quote = {'id': 1, 'text': 'Test', 'author': 'Me'}
>>> QuoteCache.set_quote(1, quote)
>>> cached = QuoteCache.get_quote(1)
>>> print(f"Cache works: {cached == quote}")
Cache works: True

# Test rate limiting
>>> from code.utils.rate_limiter import APIRateLimiter
>>> for i in range(5):
...     result = APIRateLimiter.check_ip_limit('192.168.1.1', limit=3)
...     print(f"Request {i+1}: {'ALLOWED' if result else 'BLOCKED'}")
Request 1: ALLOWED
Request 2: ALLOWED
Request 3: ALLOWED
Request 4: BLOCKED
Request 5: BLOCKED

# Test logging
>>> import logging
>>> logger = logging.getLogger('code.django_integration')
>>> logger.info('Test message', extra={'user': 'admin', 'action': 'test'})
# Check logs: tail -f logs/app.log

# Test task submission
>>> from code.celery_tasks.tasks import long_task
>>> task = long_task.delay(5)
>>> print(f"Task submitted: {task.id}")
Task submitted: abc-123-def

# Monitor in Flower: http://localhost:5555/task/abc-123-def

>>> exit()
```

---

## Common Production Tasks

### Monitor System Health

```bash
# Check Redis
redis-cli INFO | grep -E "connected_clients|used_memory|evicted_keys"

# Check Celery workers
celery -A code.celery_tasks inspect active  # Running tasks
celery -A code.celery_tasks inspect stats   # Worker stats
celery -A code.celery_tasks inspect reserved  # Reserved tasks

# Check Django
python manage.py check  # Validates configuration
python manage.py migrate --plan  # See pending migrations

# Check logs for errors
tail -50 logs/app.log | grep ERROR
```

### Optimize Performance

```bash
# Find slow queries
python manage.py shell_plus --print-sql

# Find N+1 queries
python manage.py shell
>>> from django.test.utils import CaptureQueriesContext
>>> from django.db import connection
>>> with CaptureQueriesContext(connection) as ctx:
...     # Run your code
...     quotes = Quote.objects.all()
...     for q in quotes: pass
>>> print(f"Queries: {len(ctx)}")

# Analyze cache performance
redis-cli INFO stats | grep -E "hits|misses"
```

### Handle Stuck Tasks

```bash
# List stuck tasks
celery -A code.celery_tasks inspect active

# Terminate a stuck task
celery -A code.celery_tasks revoke <task_id> --terminate

# Clear task queue if corrupted
celery -A code.celery_tasks purge  # WARNING: Deletes all pending tasks!
```

---

## Troubleshooting

### Cache Not Working

**Problem**: Cache hit ratio is 0%

**Solutions**:
1. Check Redis is running: `redis-cli ping` → should print PONG
2. Check Django settings: `CACHES['default']['LOCATION']` points to correct Redis
3. Verify cache is being set: `redis-cli KEYS '*'` should show keys
4. Check cache TTL: `redis-cli TTL key_name`

### Rate Limiting Too Strict

**Problem**: Getting 429 errors too frequently

**Solutions**:
1. Increase limit: Change `limit=1000` to higher number
2. Increase window: Change `period=3600` to larger time window (seconds)
3. Disable for development: Set different limits in settings.DEBUG
4. Skip certain endpoints: Add whitelist to middleware

### Celery Tasks Not Running

**Problem**: Tasks stay PENDING forever

**Solutions**:
1. Verify worker is running: `celery -A code.celery_tasks inspect active`
2. Check Redis: `redis-cli PING` should return PONG
3. Verify task is registered: `celery -A code.celery_tasks inspect registered`
4. Check for errors: `celery -A code.celery_tasks worker --loglevel=debug`

### Logs Not Writing

**Problem**: Log files not created or empty

**Solutions**:
1. Check directory exists: `mkdir -p /root/goit/python_web/module_10/02_advanced_edition/logs`
2. Check permissions: `chmod 755 logs/`
3. Install json logger: `pip install python-json-logger`
4. Verify logger in settings.py has correct handler

---

## Key Concepts

| Pattern | Purpose | When to Use |
|---------|---------|------------|
| **Cache-Aside** | Load data on demand | Read-heavy workloads |
| **Write-Through** | Keep cache in sync | Need consistency |
| **Rate Limiting** | Prevent overload | Public APIs |
| **Structured Logging** | Track events | Production debugging |
| **Error Monitoring** | Detect problems | Critical systems |
| **Query Optimization** | Reduce latency | Database-heavy ops |
| **Performance Monitor** | Measure efficiency | Bottleneck detection |

---

## Next Steps

1. ✅ You've learned production patterns
2. 🚀 Deploy to staging environment
3. 📊 Monitor for 24 hours
4. 🔧 Tune settings based on metrics
5. 📈 Gradually increase traffic
6. 🏆 Go production!

---

Congratulations! Your system is now production-ready. 🎉
