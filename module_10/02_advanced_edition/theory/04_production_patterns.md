# Lesson 4: Production Patterns for Scalability & Reliability

**Goal**: Learn patterns that make systems production-ready
**Time**: 25 minutes reading
**Prerequisites**: Lessons 1-3 complete

---

## What Makes Production-Ready?

Systems need more than just "working" code:

- ✅ **Fast**: Cache frequently accessed data
- ✅ **Polite**: Rate limit to not overwhelm targets
- ✅ **Observable**: Structured logging for debugging
- ✅ **Reliable**: Error monitoring and recovery
- ✅ **Scalable**: Optimized queries handling millions
- ✅ **Monitored**: Performance tracking continuously

---

## Pattern 1: Redis Caching

Caching eliminates redundant work.

### Cache-Aside Pattern (Lazy Loading)

```
1. Client requests data
   ↓
2. Check Redis cache
   ├─ Hit? Return cached data
   └─ Miss? Continue to step 3
   ↓
3. Query database (expensive)
   ↓
4. Store in Redis for future requests
   ↓
5. Return to client
```

### Implementation

```python
from django.core.cache import cache

def get_quote(quote_id):
    # Check cache first
    cache_key = f'quote:{quote_id}'
    quote = cache.get(cache_key)

    if quote is None:
        # Cache miss: fetch from DB
        quote = Quote.objects.get(id=quote_id)
        # Store for 1 hour
        cache.set(cache_key, quote, timeout=3600)

    return quote
```

### Performance Impact

- **Without cache**: Every request = database query (10-100ms)
- **With cache**: First request = database (10ms), subsequent = cache (1ms)
- **Result**: 10-100x faster for frequently accessed data

---

## Pattern 2: Rate Limiting

Limit requests to be polite to target servers.

### Token Bucket Algorithm

```
Bucket capacity: 100 requests
Leak rate: 10 requests/minute

Each request:
1. Remove 1 token from bucket
2. If bucket empty, request rejected
3. Bucket refills automatically at leak rate
```

### Implementation

```python
from django.core.cache import cache

class RateLimiter:
    def __init__(self, key, max_requests, time_window):
        self.key = key
        self.max_requests = max_requests
        self.time_window = time_window

    def is_allowed(self):
        current = cache.get(self.key, 0)

        if current >= self.max_requests:
            return False

        cache.incr(self.key)
        if current == 0:
            cache.expire(self.key, self.time_window)

        return True

# Usage
limiter = RateLimiter('api_requests', max_requests=100, time_window=60)
if limiter.is_allowed():
    # Process request
else:
    # Return 429 Too Many Requests
```

### Why It Matters

- **Without rate limiting**: Scrapy can hammer server, get blocked
- **With rate limiting**: Spreads requests, appears like normal browser
- **Result**: Can scrape more data before getting blocked

---

## Pattern 3: Structured Logging

Structured logging enables debugging and monitoring.

### Unstructured (Bad)

```python
logger.info('Scraping page')
logger.info('Found 50 quotes')
logger.error('Failed to scrape')

# Problems:
# - Can't filter by spider
# - Can't parse "50" as number
# - Can't correlate events
```

### Structured (Good)

```python
import json
import logging

logger.info('Page scraped', extra={
    'spider': 'quotes',
    'url': 'https://quotes.toscrape.com/page/2',
    'items_count': 50,
    'duration_seconds': 1.2,
})

# Output: {"spider": "quotes", "url": "...", "items_count": 50}
# Benefits:
# - Can parse programmatically
# - Can filter: spider='quotes'
# - Can aggregate: sum(items_count)
# - Can alert: if duration > threshold
```

### Implementation

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add custom fields
        if hasattr(record, 'spider'):
            log_data['spider'] = record.spider
        if hasattr(record, 'items_count'):
            log_data['items_count'] = record.items_count

        return json.dumps(log_data)

# Usage
logger.info(
    'Scraping complete',
    extra={'spider': 'quotes', 'items_count': 50}
)
```

---

## Pattern 4: Error Monitoring

Monitor and recover from failures.

### Automatic Retries

```python
@shared_task(bind=True, autoretry_for=(ConnectionError,))
def resilient_scrape(self):
    try:
        result = scrape_website()
        return result
    except ConnectionError as e:
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
        countdown = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=countdown)
```

### Circuit Breaker Pattern

Stop making requests when target is down:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failures = 0
        self.failure_threshold = failure_threshold
        self.is_open = False

    def call(self, func):
        if self.is_open:
            raise Exception('Circuit breaker is open')

        try:
            result = func()
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.is_open = True
            raise

# Usage
breaker = CircuitBreaker()
try:
    result = breaker.call(fetch_from_website)
except:
    # Use cached data instead
    result = cache.get('last_known_data')
```

---

## Pattern 5: Database Optimization

Prevent database from becoming bottleneck.

### Problem: N+1 Queries

```python
# BAD: 1 query + N queries
quotes = Quote.objects.all()  # 1 query
for quote in quotes:  # For 1000 quotes
    print(quote.author.name)  # 1000 queries!
# Total: 1001 queries

# GOOD: 1 query with JOIN
quotes = Quote.objects.select_related('author')
for quote in quotes:
    print(quote.author.name)  # No additional queries
# Total: 1 query
```

### Indexes

```python
class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_index=True)
    last_scraped = models.DateTimeField(db_index=True)

    class Meta:
        # Composite index for common queries
        indexes = [
            models.Index(fields=['author', 'last_scraped']),
        ]

# Now this query is instant:
Quote.objects.filter(author=author, last_scraped__gte=cutoff)
```

### Bulk Operations

```python
# BAD: Individual saves
for quote in quotes:
    quote.save()  # Database write per item

# GOOD: Bulk update
Quote.objects.bulk_update(quotes, ['last_scraped'], batch_size=1000)

# BAD: Individual creates
for data in items:
    Quote.objects.create(**data)

# GOOD: Bulk create
Quote.objects.bulk_create([Quote(**d) for d in items], batch_size=1000)
```

---

## Pattern 6: Performance Monitoring

Track system performance to identify bottlenecks.

### Response Time Tracking

```python
import time
import logging

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        self.logger.info(
            'Request completed',
            extra={
                'path': request.path,
                'method': request.method,
                'duration_ms': duration * 1000,
            }
        )

        return response
```

### Query Counting

```python
from django.test.utils import override_settings
from django.db import connection, reset_queries

@override_settings(DEBUG=True)
def optimized_view(request):
    reset_queries()

    # ... view logic ...

    query_count = len(connection.queries)
    if query_count > 20:  # Alert threshold
        logger.warning(f'High query count: {query_count}')
```

---

## Complete Production System

```
User Request
  ↓
[Rate Limit Check] ← Polite to targets
  ├─ Allowed? Continue
  └─ Too many? Return 429
  ↓
[Cache Check] ← Fast responses
  ├─ Hit? Return cached data
  └─ Miss? Continue to database
  ↓
[Database Query] ← Optimized
  ├─ select_related() (no N+1)
  ├─ Indexed (fast lookup)
  └─ Bulk operations (efficient)
  ↓
[Store in Cache] ← For next request
  ├─ TTL: 1 hour
  └─ Key: user:123:profile
  ↓
[Log Request] ← Observable
  ├─ Structured JSON
  ├─ Timestamp
  ├─ Duration
  └─ User ID
  ↓
[Monitor Performance] ← Track trends
  ├─ Response time
  ├─ Error rate
  └─ Cache hit rate
  ↓
[Return Response]
```

---

## Expected Performance

With production patterns, you can achieve:

| Metric | Without | With |
|--------|---------|------|
| **Response Time** | 100-500ms | 5-50ms (cached) |
| **Concurrent Users** | 100 | 10,000+ |
| **Database Queries** | 1000/sec | 100/sec (cached) |
| **Error Rate** | 5-10% | 0.1% (retries) |

---

## Monitoring Tools

### APM (Application Performance Monitoring)
- New Relic
- DataDog
- Sentry (errors)

### Caching Observability
- Redis monitoring tools
- Cache hit/miss ratios

### Log Aggregation
- ELK (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch

---

## Best Practices Summary

1. **Cache Aggressively** - 99% of reads can be cached
2. **Rate Limit** - Don't abuse target servers
3. **Log Structurally** - Enable programmatic analysis
4. **Monitor Everything** - You can't improve what you don't measure
5. **Fail Gracefully** - Retries, fallbacks, circuit breakers
6. **Optimize Queries** - No N+1, use indexes
7. **Use Bulk Ops** - Don't save one by one
8. **Monitor Performance** - Track trends over time

---

## Official Resources

- **Redis Caching**: https://redis.io/topics/lru-cache
- **Rate Limiting**: https://en.wikipedia.org/wiki/Token_bucket
- **Structured Logging**: https://www.kartar.net/2015/12/structured-logging/
- **Django Optimization**: https://docs.djangoproject.com/en/stable/topics/db/optimization/
- **Celery Monitoring**: https://docs.celeryproject.io/en/stable/userguide/monitoring/

---

## Next Steps

1. **Read this document** (you're reading it) ✓
2. **Follow**: [04_production_tutorial.md](../tutorials/04_production_tutorial.md)
3. **Code**: Implement patterns in `code/utils/`
4. **Test**: Measure improvements

Congratulations! You've completed all Advanced Edition lessons. 🎉
