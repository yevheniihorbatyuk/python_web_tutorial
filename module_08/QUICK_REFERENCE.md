# Module 8: Quick Reference Guide

## File Structure

```
module_08/
├── 01_sqlalchemy_advanced.py      # ORM with User-Address-City-Country
├── 02_mongodb_advanced.py          # Document storage with aggregation
├── 03_caching_strategies.py        # LRU cache + Redis caching
├── 04_rabbitmq_messaging.py        # Producer/consumer async processing
├── 05_realworld_data_science.py    # Integrated data science system
├── COMPREHENSIVE_GUIDE.md          # Full documentation
├── IMPLEMENTATION_SUMMARY.md       # What was built
├── QUICK_REFERENCE.md             # This file
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Service containers
├── .env.example                   # Environment configuration
└── README.md                      # Getting started
```

---

## 1️⃣ SQLAlchemy Advanced (01_sqlalchemy_advanced.py)

### Key Classes:
```python
User → Address → City → Country (hierarchy)

UserRepository:
  .find_users_by_country("Ukraine")
  .find_users_by_city("Kyiv")
  .get_users_with_addresses()
  .get_user_statistics()
  .get_users_ranked_by_activity()

CountryRepository:
  .get_all_countries_with_cities()
  .get_country_statistics()

DataScienceAnalytics:
  .get_user_distribution_by_country()
  .get_user_metrics_by_registration_cohort()
  .identify_high_value_users()
```

### Core Patterns:
- **N+1 Prevention**: `joinedload(User.address).joinedload(Address.city)`
- **Aggregations**: `func.count()`, `func.avg()`, `func.max()`
- **Transactions**: `session.begin_nested()` with rollback
- **Query Building**: Filter, order_by, limit, offset

### Real-World Use Cases:
- Geographic user analysis
- Cohort-based retention analysis
- High-value user identification
- Regional expansion planning

---

## 2️⃣ MongoDB Advanced (02_mongodb_advanced.py)

### Data Models:
```python
Event Document:
{
  "user_id": 123,
  "event_type": "user_purchase",
  "timestamp": ISODate(),
  "metadata": { "price": 99.99, "category": "electronics" },
  "geo": { "country": "Ukraine", "coordinates": [lon, lat] }
}

User Profile:
{
  "username": "data_scientist",
  "email": "user@example.com",
  "profile": { "interests": [...], "expertise_level": "senior" },
  "metrics": { "engagement_score": 8.5 },
  "subscriptions": [...]
}
```

### Key Methods:
```python
UserManager:
  .insert_user(user_data)
  .find_users_by_interest("data-science")
  .bulk_insert_users(users_list)
  .update_user_metrics(user_id, metrics)

EventTracker:
  .log_event(event_data)
  .get_event_distribution()          # $group aggregation
  .get_user_activity_metrics()       # Complex pipeline
  .get_purchase_analytics()          # Business intelligence

GeoLocationManager:
  .find_events_near_location(lon, lat, max_distance)

DataProcessor:
  .calculate_cohort_metrics()
  .export_data_for_analysis()
```

### Aggregation Pipelines:
```python
# Event distribution
[
  { "$group": { "_id": "$event_type", "count": { "$sum": 1 } } },
  { "$sort": { "count": -1 } }
]

# User activity metrics
[
  { "$match": { "timestamp": { "$gte": start, "$lte": end } } },
  { "$group": { "_id": "$user_id", "event_count": { "$sum": 1 } } },
  { "$sort": { "event_count": -1 } },
  { "$limit": 10 }
]
```

### Indexes:
```python
# Unique indexes
collection.create_index([("username", 1)], unique=True)

# Compound indexes
collection.create_index([("user_id", 1), ("timestamp", -1)])

# Geospatial indexes
collection.create_index([("geo.coordinates", "2dsphere")])
```

### Real-World Use Cases:
- Event tracking systems
- IoT sensor data
- User behavior analytics
- Time-series storage
- User-generated content

---

## 3️⃣ Caching Strategies (03_caching_strategies.py)

### Tier 1: In-Process (@lru_cache)
```python
@lru_cache(maxsize=128)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Results:
# fib(30): 179ms → 0.02ms (11,000x faster!)
```

### Tier 2: Distributed (Redis)
```python
@redis_cache(ttl=3600)
def get_user_recommendations(user_id):
    # 1 hour TTL
    return compute_recommendations(user_id)
```

### Tier 3: Application Logic (Custom TTL)
```python
@timed_lru_cache(maxsize=1000, ttl_seconds=600)
def get_trending_items(category):
    # 10 minute TTL with auto-expiration
    return compute_trending(category)
```

### Manual Redis Cache:
```python
redis_cache = RedisCache(redis_client)

# Get cached value
value = redis_cache.get("user:123:profile")

# Set with TTL
redis_cache.set("user:123:profile", user_profile, ttl=3600)

# Delete
redis_cache.delete("user:123:profile")

# Clear by pattern
redis_cache.clear_pattern("user:123:*")
```

### Performance Benchmarks:
| Function | Without Cache | With @lru_cache | Speedup |
|----------|---------------|-----------------|---------|
| Fibonacci(25) | 16.44ms | 0.01ms | 1,271x |
| Fibonacci(30) | 179.19ms | 0.02ms | 11,456x |
| Fibonacci(35) | Timeout | 0.01ms | ∞ |

### Best Practice Rules:
```
Use @lru_cache if:
  ✓ Pure function (no side effects)
  ✓ Deterministic (same input = same output)
  ✓ Small result size
  ✗ Shared across processes

Use Redis if:
  ✓ Need distributed caching
  ✓ Large caches (1000s of items)
  ✓ Multi-process/server environment
  ✗ Tiny datasets
  ✗ No network overhead tolerance

Use application logic if:
  ✓ Custom eviction policy needed
  ✓ Complex invalidation logic
  ✓ Domain-specific caching
```

---

## 4️⃣ RabbitMQ Messaging (04_rabbitmq_messaging.py)

### Message Types:
```python
UserDataMessage:
  {"username": "...", "email": "..."}

NotificationMessage:
  {"recipient": "...", "subject": "...", "content": "..."}

AnalyticsMessage:
  {"event_type": "...", "user_id": "...", "properties": {...}}
```

### Producer:
```python
producer = Producer()

# Publish user data
producer.publish_user_data_event("john_doe", "john@example.com")

# Publish notification
producer.publish_notification("user@example.com", "Welcome!", "Hello!")

# Publish analytics
producer.publish_analytics_event("user_signup", user_id=123, extra={...})
```

### Consumer Pattern:
```python
class MyConsumer(Consumer):
    def message_callback(self, message):
        # Process message
        # Return True if successful
        # Return False if should retry
        pass

consumer = MyConsumer()
consumer.start_consuming()
```

### Exchange Types:
```
Direct Exchange (data_processing):
  Producer → routing_key="user.data" → Queue → Consumer

Topic Exchange (notifications):
  Producer → routing_key="notification.email" → Queue → Consumer

Fanout Exchange (analytics):
  Producer → All queues broadcast
```

### Error Handling:
```
Message Processing:
  1st attempt: Immediate
  2nd attempt: Wait 2^1 = 2 seconds
  3rd attempt: Wait 2^2 = 4 seconds
  Failed: Send to Dead Letter Queue (DLQ)
```

### Real-World Scenarios:
```
User Signup:
  Producer (API) → publish_user_data_event()
     → UserDataConsumer (validation, enrichment)
     → MongoDB (store events)
     → RabbitMQ (queue recommendations)
     → RecommendationConsumer (calculate)
     → Redis (cache results)
     → API (return to user)
```

---

## 5️⃣ Real-World Data Science (05_realworld_data_science.py)

### User Segments:
```python
DORMANT   = no activity for 90+ days → Re-engagement campaigns
ACTIVE    = regular users → Personalized recommendations
VIP       = high spending → Premium features/support
AT_RISK   = churn signals → Retention offers
```

### Prediction Types:
```python
CHURN = probability user will leave (0-100%)
LIFETIME_VALUE = total revenue expected ($)
NEXT_PURCHASE = estimated days until next buy
RECOMMENDATION = products user might like
```

### AnalyticsEngine:
```python
engine = AnalyticsEngine()
profile = engine.calculate_user_profile(user_data)

# Returns:
# {
#   "segment": "active",
#   "engagement": 65.5,
#   "churn_risk": 0.21,
#   "ltv_prediction": 1500.00
# }
```

### MLModelManager:
```python
ml = MLModelManager()

churn = ml.predict("churn", user_id=123)
# Returns: { "value": 0.35, "confidence": 0.85 }

ltv = ml.predict("lifetime_value", user_id=123)
# Returns: { "value": 5000.00, "confidence": 0.80 }
```

### RecommendationEngine:
```python
engine = RecommendationEngine()
recs = engine.get_recommendations(user_id=123)

# Returns: [
#   { "product_id": "P1", "relevance": 0.90 },
#   { "product_id": "P2", "relevance": 0.85 },
#   { "product_id": "P3", "relevance": 0.80 }
# ]
```

### InsightsGenerator:
```python
insights = InsightsGenerator()
report = insights.generate_segment_report(profiles)

# Segment-specific insights:
# - Dormant: "X users inactive, recommend re-engagement"
# - Active: "Y users active, personalize recommendations"
# - VIP: "Z premium users, offer exclusive perks"
# - At-risk: "W users at risk, send retention offers"
```

---

## 🔄 Integration Pattern

```
┌─────────────────┐
│  Client/User    │
└────────┬────────┘
         │
         ▼
    ┌─────────────────────────────────────┐
    │     API Layer (Sync)                │
    │     SQLAlchemy ORM                  │
    │  (PostgreSQL, Redis Cache)          │
    └────────┬────────────────────────────┘
             │
    ┌────────┴────────────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────┐            ┌──────────────────┐
│   Redis     │            │  RabbitMQ        │
│   Cache     │            │  Message Broker  │
└─────────────┘            └────────┬─────────┘
                                    │
    ┌──────────────┬────────────────┼────────────────┐
    │              │                │                │
    ▼              ▼                ▼                ▼
┌────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────┐
│ PostgreSQL │ │  MongoDB    │ │ Recommendation│ │Analytics│
│ (ORM)      │ │  (Events)   │ │ Engine       │ │ Consumer │
└────────────┘ └─────────────┘ └──────────────┘ └──────────┘
    │              │                │                │
    └──────────────┴────────────────┴────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │  Data Science Engine            │
    │  - User Segmentation            │
    │  - Churn Prediction             │
    │  - LTV Modeling                 │
    │  - Personalization              │
    └─────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │  Insights & Recommendations     │
    └─────────────────────────────────┘
             │
             ▼
        User Gets Results
```

---

## 🏃 Quick Start Commands

```bash
# Install dependencies
pip install --break-system-packages -r requirements.txt

# Run individual modules
python3 01_sqlalchemy_advanced.py
python3 02_mongodb_advanced.py
python3 03_caching_strategies.py
python3 04_rabbitmq_messaging.py
python3 05_realworld_data_science.py

# Set up full environment
docker-compose up -d

# Access services
# PostgreSQL: localhost:5432
# MongoDB: localhost:27017
# Redis: localhost:6379
# RabbitMQ Web UI: http://localhost:15672 (guest/guest)
```

---

## 📊 Performance Guidelines

| Operation | Time | Notes |
|-----------|------|-------|
| SQLAlchemy Query (no cache) | 50-100ms | Database I/O |
| SQLAlchemy Query (with eager load) | 50-100ms | Single query, prevent N+1 |
| Redis Query (hit) | 1-5ms | Network + deserialize |
| @lru_cache (hit) | <0.1ms | In-memory, fastest |
| MongoDB aggregation | 100-500ms | Depends on data volume |
| RabbitMQ message (publish) | 5-10ms | Fast queue operation |
| ML Prediction (first) | 200-500ms | Model computation |
| ML Prediction (cached) | <1ms | Redis cache |

---

## 🔐 Security Checklist

- ✅ Use parameterized queries (SQLAlchemy automatic)
- ✅ Validate input before processing
- ✅ Use environment variables for secrets
- ✅ Enable SSL/TLS for all network connections
- ✅ Limit database user permissions
- ✅ Use message encryption for sensitive data
- ✅ Implement rate limiting on APIs
- ✅ Log security events

---

## 📚 When to Use Each Technology

### PostgreSQL + SQLAlchemy
```
Use when:
✓ Structured data with clear schema
✓ ACID transactions required
✓ Complex joins and queries
✓ Referential integrity critical

Examples:
- User accounts
- E-commerce orders
- Financial transactions
- Business records
```

### MongoDB
```
Use when:
✓ Schema evolves frequently
✓ Large volumes of unstructured data
✓ Document-level transactions OK
✓ Horizontal scaling needed

Examples:
- Event logs
- IoT sensor data
- User-generated content
- Time-series data
```

### Redis
```
Use when:
✓ Sub-millisecond latency needed
✓ Data fits in memory
✓ Caching layer wanted
✓ Session storage

Examples:
- Web caches
- Session storage
- Real-time leaderboards
- Rate limiting counters
```

### RabbitMQ
```
Use when:
✓ Need async processing
✓ Services must be decoupled
✓ Reliability and retries important
✓ Scaling consumers independently

Examples:
- Email sending
- Image processing
- Data aggregation
- Event streaming
```

---

## 🎯 Common Patterns

### Pattern 1: Cache-Aside
```python
def get_user(user_id):
    # Check cache first
    user = redis.get(f"user:{user_id}")
    if user:
        return user

    # Cache miss, fetch from DB
    user = db.get_user(user_id)

    # Store in cache
    redis.set(f"user:{user_id}", user, ttl=3600)

    return user
```

### Pattern 2: Write-Through Cache
```python
def update_user(user_id, data):
    # Update DB
    user = db.update_user(user_id, data)

    # Update cache
    redis.set(f"user:{user_id}", user, ttl=3600)

    return user
```

### Pattern 3: Read-Heavy Aggregation
```python
# Store pre-computed results
daily_stats = calculate_stats()  # Expensive operation
redis.set("stats:daily", daily_stats, ttl=86400)  # 24 hours

# Serve from cache
stats = redis.get("stats:daily")
```

### Pattern 4: Message Queue Processing
```
User action → Producer → RabbitMQ Queue → Consumer → Update DB
  (fast)       (instant)      (async)    (background)
```

---

## ⚠️ Common Pitfalls

1. **N+1 Queries**: Always use `joinedload()` for relationships
2. **Cache Invalidation**: Remember to clear cache on updates
3. **Connection Pools**: Configure appropriate pool sizes
4. **Message Loss**: Implement acknowledgment and retries
5. **Unbounded Cache**: Set maximum size and TTL
6. **No Monitoring**: Track cache hits/misses, query times
7. **Blocking Calls**: Use async for I/O-heavy operations

---

**Happy Coding!** 🚀
