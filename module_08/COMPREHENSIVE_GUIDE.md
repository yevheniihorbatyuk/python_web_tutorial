# Module 8: Advanced Databases & Async Processing - Comprehensive Guide

*For Senior Data Science Engineers*

## Overview

This module covers enterprise-grade patterns for building scalable data systems:

- **SQLAlchemy ORM**: Complex relationships, performance optimization, transactions
- **MongoDB**: Flexible document storage, aggregation pipelines, time-series data
- **Redis**: Distributed caching, session storage, real-time features
- **RabbitMQ**: Async task processing, event streaming, microservices
- **Real-World Integration**: Complete data science system combining all technologies

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│         Client Applications / Web Services                   │
└────────┬──────────────────────────────────────┬──────────────┘
         │                                      │
         ▼                                      ▼
  ┌──────────────┐                    ┌──────────────────┐
  │  API Layer   │                    │  Background Jobs │
  │  (Sync)      │                    │  (Async)         │
  └──────┬───────┘                    └────────┬─────────┘
         │                                    │
         ├────────────┬──────────┬────────────┤
         │            │          │            │
         ▼            ▼          ▼            ▼
    ┌─────────────────────────────────────────────────┐
    │            RabbitMQ Message Broker              │
    │  (Async task queue, event streaming)            │
    └─────────────────────────────────────────────────┘
         │            │          │            │
         ▼            ▼          ▼            ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
    │PostgreSQL│ │MongoDB  │ │  Redis   │ │ File /   │
    │(ORM)    │ │(NoSQL)  │ │(Cache)   │ │ Object   │
    │         │ │         │ │          │ │ Storage  │
    │Structured│ │Flexible │ │Fast      │ │          │
    │Relational│ │Document │ │In-Memory │ │Archive   │
    └─────────┘ └─────────┘ └──────────┘ └──────────┘
```

## Module Files

### 01_sqlalchemy_advanced.py
**Focus**: Structured data with complex relationships

```python
# User → Address → City → Country hierarchy
# Use cases:
# - Geographic analysis
# - User location-based features
# - International expansion analysis
```

**Key Patterns**:
- Repository pattern for clean data access
- Eager loading vs lazy loading (N+1 query prevention)
- Aggregation queries for analytics
- Transaction management

**Real-world Applications**:
- E-commerce: User profiles with multiple addresses
- SaaS: Multi-tenant data isolation
- Analytics: User segmentation by geography

### 02_mongodb_advanced.py
**Focus**: Flexible, document-oriented storage

```python
# Ideal for:
# - Event/log storage (time-series)
# - User-generated content
# - Semi-structured data
# - Rapid schema evolution
```

**Key Patterns**:
- Document design for different access patterns
- Aggregation pipeline (MongoDB's group/join equivalent)
- Indexing strategies (single field, compound, geospatial)
- Batch processing and bulk operations

**Real-world Applications**:
- Analytics: Event tracking systems
- IoT: Time-series sensor data
- Social: User-generated content
- Recommendations: User behavior tracking

### 03_caching_strategies.py
**Focus**: Performance optimization through caching

```python
# Three-tier caching strategy:
# 1. @lru_cache - In-process (fast, limited to single process)
# 2. Redis - Distributed (cross-process, network I/O)
# 3. Application logic - Custom TTL and invalidation
```

**Key Patterns**:
- LRU (Least Recently Used) eviction for bounded memory
- TTL (Time To Live) for data freshness
- Cache invalidation strategies
- Performance benchmarking

**Real-world Applications**:
- ML predictions: Cache model outputs
- Recommendations: Cache user profiles and scores
- Analytics: Cache aggregated metrics
- Fibonacci-like recursive problems: Cache intermediate results

### 04_rabbitmq_messaging.py
**Focus**: Asynchronous task processing

```python
# Message flow:
# Producer → RabbitMQ Exchange → Queue → Consumer → Processing
#
# Exchange types:
# - Direct: Routing by exact key match
# - Topic: Routing by pattern matching
# - Fanout: Broadcast to all queues
# - Headers: Routing by message headers
```

**Key Patterns**:
- Producer-consumer decoupling
- Message retry with exponential backoff
- Dead-letter queues (DLQ) for failed messages
- Priority queues for urgent tasks

**Real-world Applications**:
- User onboarding: Data validation, enrichment
- Notifications: Email, SMS async sending
- Analytics: Event processing pipeline
- Data pipelines: ETL/ELT operations

### 05_realworld_data_science.py
**Focus**: Integrated data science system

```python
# Complete pipeline:
# Data → Storage → Analytics → Predictions → Recommendations → Actions
#
# User Segments:
# - DORMANT: No activity for 90+ days → Re-engagement campaigns
# - ACTIVE: Regular users → Personalized recommendations
# - VIP: High-value users → Premium features
# - AT_RISK: Showing churn signals → Retention offers
```

**Key Components**:
- User profiling and segmentation
- Churn prediction
- Lifetime value (LTV) modeling
- Personalized recommendations
- Actionable business insights

## Best Practices

### 1. Database Selection

```
Use PostgreSQL (SQLAlchemy) when:
✓ Data has clear structure
✓ Need ACID transactions
✓ Complex joins across tables
✓ Referential integrity is critical
✗ Schema changes frequently
✗ Need massive horizontal scaling
✗ Semi-structured data

Use MongoDB when:
✓ Schema evolves rapidly
✓ Document-level transactions sufficient
✓ Large volume of time-series data
✓ Nested/hierarchical data natural
✓ Horizontal scaling required
✗ Complex multi-document joins
✗ Need strict consistency
✗ Small document field counts (few attributes)

Use Redis when:
✓ Sub-millisecond latency required
✓ Data fits in memory
✓ Caching layer needed
✓ Session storage
✓ Real-time leaderboards/counts
✗ Persistent storage requirements
✗ Large datasets
✗ Complex queries
```

### 2. Performance Optimization

```python
# ❌ BAD: N+1 Query Problem
users = session.query(User).all()
for user in users:
    print(user.address.city.name)  # Separate query per user!

# ✅ GOOD: Eager Loading
users = session.query(User).options(
    joinedload(User.address).joinedload(Address.city)
).all()
for user in users:
    print(user.address.city.name)  # No additional queries!
```

### 3. Caching Strategy

```python
# Three-tier approach:

# Tier 1: Application-level (functions/methods)
@lru_cache(maxsize=128)
def get_user_recommendations(user_id: int):
    # Fast in-process cache
    pass

# Tier 2: Redis distributed cache
@redis_cache(ttl=3600)
def get_trending_products():
    # Shared across processes/servers
    pass

# Tier 3: Database cache (query results)
# Materialized views, summary tables
```

### 4. Error Handling & Resilience

```python
# Message Processing with Retries
def process_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return process(message)
        except TemporaryError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                send_to_dlq(message)  # Dead letter queue
                raise

# Connection Pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

### 5. Monitoring & Logging

```python
# Structured Logging
logger.info(
    "User processed",
    extra={
        "user_id": 123,
        "duration_ms": 45,
        "status": "success"
    }
)

# Metrics Collection
@measure_time
@track_errors
def expensive_operation():
    pass

# Query Monitoring
from sqlalchemy import event
@event.listens_for(Engine, "before_cursor_execute")
def log_query(conn, cursor, statement, parameters, context, executemany):
    logger.debug(f"Query: {statement}, Params: {parameters}")
```

## Real-World Scenarios

### Scenario 1: User Onboarding Pipeline

```
User Signs Up
    ↓
Send Welcome Email (async) → RabbitMQ Producer
    ↓
User Data Processing Task → RabbitMQ Queue
    ↓
Consumer:
  1. Validate user data
  2. Enrich with location info
  3. Calculate initial features
  4. Store in PostgreSQL + MongoDB
    ↓
Trigger Analytics Event
    ↓
Cache user profile in Redis
    ↓
Queue recommendation calculation
```

### Scenario 2: Real-Time Analytics

```
User Events (clicks, purchases, etc.)
    ↓
Event Producer → RabbitMQ Topic Exchange
    ↓
┌─────────────────┬──────────────────┬──────────────────┐
│                 │                  │                  │
▼                 ▼                  ▼                  ▼
Analytics     Real-time         Historical      Alert
Consumer      Metrics            Analytics      System
│                 │                  │              │
└────────────────┬──────────────────┬──────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
  Redis                    MongoDB
  (counters,               (raw events,
   leaderboards)           aggregations)
```

### Scenario 3: Personalization Engine

```
User Profile Request
    ↓
Check Redis Cache ──Yes──→ Return Cached Profile
    │
   No
    ↓
Load from PostgreSQL
    ↓
Calculate Features from Events (MongoDB)
    ↓
Get ML Predictions from Redis
    │(if cached)
    ├──→ Use cached predictions
    │
   No
    ├──→ Queue prediction task to RabbitMQ
    ├──→ Return immediate results
    │
Cache in Redis (TTL=1 hour)
    ↓
Generate Personalized Recommendations
    ↓
Return to User
```

## Performance Checklist

- [ ] Use connection pooling for database connections
- [ ] Enable query result caching with Redis
- [ ] Implement database connection timeouts
- [ ] Use bulk operations for batch inserts
- [ ] Create appropriate database indexes
- [ ] Implement pagination for large result sets
- [ ] Use Redis for frequently accessed data
- [ ] Set up message queue batch processing
- [ ] Monitor slow queries and N+1 problems
- [ ] Use prepared statements/parameterized queries
- [ ] Implement circuit breakers for external services
- [ ] Use async processing for long-running tasks
- [ ] Compress large messages in RabbitMQ
- [ ] Monitor Redis memory usage
- [ ] Implement data archival strategy

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│        Load Balancer / API Gateway              │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Web Server 1 │  │ Web Server 2 │
│ (Gunicorn)   │  │ (Gunicorn)   │
└──────┬───────┘  └────────┬─────┘
       │                   │
       └───────┬───────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐    ┌──────────────┐
│   Worker 1   │    │   Worker 2   │
│(Celery/async)│    │(Celery/async)│
└──────┬───────┘    └────────┬─────┘
       │                     │
       └───────┬─────────────┘
               │
    ┌──────────┴──────────┬──────────┐
    │                     │          │
    ▼                     ▼          ▼
 PostgreSQL          MongoDB      Redis
 (Primary DB)        (Events)     (Cache)
 Replication         Sharding     Cluster
```

## Monitoring & Observability

### Key Metrics

```python
# Database
- Query execution time (p50, p95, p99)
- Connection pool usage
- Slow query log
- Transaction abort rate

# Cache
- Hit ratio
- Eviction rate
- Memory usage

# Message Queue
- Queue depth
- Message latency
- Error rate
- Dead letter queue size

# Application
- Request latency
- Error rate
- Throughput (requests/sec)
```

### Alerts to Set

```
- Database connection pool > 80%
- Redis memory usage > 80%
- RabbitMQ queue depth > 10k messages
- Average query time > 100ms
- Cache hit ratio < 70%
- Message processing error rate > 1%
```

## Testing Strategies

### Unit Tests

```python
# Test business logic independent of databases
def test_user_profile_calculation():
    profile = calculate_user_profile(test_data)
    assert profile.segment == UserSegment.VIP
    assert profile.ltv_prediction > 500
```

### Integration Tests

```python
# Test with real databases (use Docker containers)
@pytest.fixture
def db_session():
    engine = create_engine("postgresql://localhost/test_db")
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    yield session
    session.close()

def test_user_creation(db_session):
    user = User(username="test")
    db_session.add(user)
    db_session.commit()
    assert db_session.query(User).count() == 1
```

### Performance Tests

```python
# Benchmark critical paths
import timeit

def test_recommendation_performance():
    engine = RecommendationEngine()

    time_taken = timeit.timeit(
        lambda: engine.get_recommendations(user_id=123),
        number=1000
    )

    assert time_taken / 1000 < 0.1  # < 100ms per call
```

## Security Considerations

```python
# SQL Injection Prevention (SQLAlchemy does this automatically)
✓ query.filter(User.email == user_email)
✗ f"SELECT * FROM users WHERE email = '{user_email}'"

# NoSQL Injection Prevention
✓ collection.find({"email": user_email})
✗ collection.find({"$where": f"this.email == '{user_email}'"})

# Redis Security
- Use Redis ACL for fine-grained access control
- Enable SSL/TLS for connections
- Use strong passwords
- Isolate Redis to private network

# RabbitMQ Security
- Use strong credentials
- Enable SSL/TLS
- Set user permissions per queue/exchange
- Monitor access logs
```

## Resources

### Documentation
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Redis Documentation](https://redis.io/docs/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)

### Tools
- **pgAdmin**: PostgreSQL management
- **MongoDB Compass**: MongoDB GUI
- **Redis Insight**: Redis monitoring
- **RabbitMQ Management**: Web UI (http://localhost:15672)

## Troubleshooting

### Common Issues

```
Problem: Slow database queries
Solution:
  1. Enable query logging: echo=True
  2. Identify missing indexes
  3. Check query execution plan
  4. Use EXPLAIN ANALYZE in PostgreSQL

Problem: Redis memory bloat
Solution:
  1. Monitor key sizes
  2. Set appropriate TTLs
  3. Implement eviction policies
  4. Use compression for large values

Problem: RabbitMQ queue buildup
Solution:
  1. Scale consumer workers
  2. Check error logs for failures
  3. Optimize message processing
  4. Implement dead-letter queue handling
```

## Conclusion

This module provides a complete toolkit for building enterprise data systems. The integration of:

- **PostgreSQL** for transactional data
- **MongoDB** for operational data
- **Redis** for real-time features
- **RabbitMQ** for async processing

...creates a powerful, scalable architecture suitable for data science and machine learning applications at any scale.

### Next Steps

1. Choose appropriate database(s) for your use case
2. Implement connection pooling and caching
3. Design robust error handling and retries
4. Set up comprehensive monitoring
5. Load test your system
6. Document your architecture

---

**Created for**: Senior Data Science Engineers
**Difficulty**: Advanced
**Estimated Time**: 3-5 days to fully internalize
