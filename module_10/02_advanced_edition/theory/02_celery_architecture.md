# Lesson 2: Celery + Redis Task Queue Architecture

**Goal**: Understand how to process long-running tasks asynchronously
**Time**: 30 minutes reading
**Prerequisites**: Lesson 1 (Scrapy) complete

---

## The Problem: Blocking Operations

In web applications, some operations take time:
- Sending emails (1-30 seconds)
- Processing images (5-60 seconds)
- Web scraping (minutes to hours)
- Database backups (variable)

If these run during an HTTP request, the user waits. This is bad for UX.

```
User clicks "Scrape"
  ↓
Server: scrapy.crawl() runs (takes 5 minutes)
  ↓ (User waits the whole time)
Server: Response returned
  ↓
User finally gets response
```

**Solution**: Run these tasks in the background, return immediately.

```
User clicks "Scrape"
  ↓
Server: Submit task to queue (instant)
  ↓
Server: Return task ID immediately
  ↓ (User sees progress bar)
User continues using app while work happens in background
  ↓
Background worker: Executes task
  ↓
Result stored in database/cache
  ↓
User checks status, gets result
```

---

## Celery: Task Queue Framework

Celery is a distributed task queue for asynchronous job processing.

### Components

```
┌─────────────────────────────────────────────────────────┐
│  Django Web Application                                  │
│  Views submit tasks: scraping_task.delay(url)           │
└──────────────────────────┬────────────────────────────┘
                           │ enqueue
                           ↓
┌──────────────────────────────────────────────────────────┐
│  Redis Broker (Message Queue)                            │
│  Stores tasks waiting to be processed                    │
│  Queue: [Task1, Task2, Task3, ...]                       │
└──────────────────────────┬────────────────────────────┘
                           │ dequeue
                           ↓
┌──────────────────────────────────────────────────────────┐
│  Celery Worker (Background Process)                      │
│  Continuously listens to queue                           │
│  Executes tasks one by one                              │
└──────────────────────────┬────────────────────────────┘
                           │ store result
                           ↓
┌──────────────────────────────────────────────────────────┐
│  Redis Backend (Result Storage)                          │
│  Stores task results after completion                    │
│  result:task-id-1 = {status: 'SUCCESS', result: ...}    │
└──────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### 1. **Broker** (Message Queue)
- Redis stores tasks waiting to execute
- FIFO (First-In, First-Out) processing
- Multiple queues for different priorities
- Survives worker/server crashes (persistent)

### 2. **Worker** (Executor)
- Background process that executes tasks
- Multiple workers can run in parallel
- Each worker processes one task at a time
- Can be on same machine or different servers

### 3. **Backend** (Result Store)
- Redis stores task results after completion
- Includes: execution status, result value, errors
- TTL (time-to-live) to prevent indefinite storage

### 4. **Task** (Unit of Work)
- Python function decorated with `@shared_task`
- Can accept arguments
- Returns result or raises exception
- Assigned unique task_id for tracking

---

## Task Lifecycle

```
1. TASK DEFINED
   @shared_task
   def scrape_task(url):
       return scrape(url)

2. TASK SUBMITTED (from Django view)
   task = scrape_task.delay('https://...')
   # Returns immediately with task_id

3. TASK QUEUED
   Redis stores: {task_id, function, args, kwargs}

4. WORKER PICKS UP
   Worker dequeues task from Redis
   Executes: scrape(url)

5. TASK RUNNING
   Long operation happens in background
   Web server stays responsive

6. RESULT STORED
   Redis: result:task-id = {status: 'SUCCESS', result: ...}

7. CLIENT RETRIEVES
   task.get()  # Polls redis until result ready
   # Returns result

8. CLEANUP
   Redis auto-deletes after TTL expires
```

---

## Task States

A task goes through states as it executes:

| State | Meaning |
|-------|---------|
| PENDING | Task submitted but not picked up yet |
| RECEIVED | Worker acknowledged task |
| STARTED | Worker began execution |
| PROGRESS | Custom progress update (optional) |
| SUCCESS | Completed successfully, result stored |
| FAILURE | Exception raised, error stored |
| RETRY | Will retry after delay |
| REVOKED | Task canceled by user |

---

## Configuration

Celery uses two main settings:

### Broker
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
```
- Redis host/port
- Database number (0-15)
- Stores task queue

### Backend
```python
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
```
- Redis host/port
- Different database from broker (to separate concerns)
- Stores task results

### Additional Settings
```python
CELERY_TASK_SERIALIZER = 'json'           # JSON format
CELERY_ACCEPT_CONTENT = ['json']          # Accept JSON
CELERY_TIMEZONE = 'UTC'                   # Use UTC time
CELERY_ENABLE_UTC = True                  # Enable UTC
CELERY_TASK_TRACK_STARTED = True          # Track when task starts
CELERY_TASK_TIME_LIMIT = 3600             # Kill after 1 hour
CELERY_TASK_SOFT_TIME_LIMIT = 3300        # Warn after 55 min
```

---

## Simple Example

```python
# tasks.py
from celery import shared_task
import time

@shared_task
def long_running_task(seconds):
    """Sleep for N seconds to simulate work"""
    time.sleep(seconds)
    return f'Slept for {seconds} seconds'


# views.py
from django.http import JsonResponse
from django.views import View
from .tasks import long_running_task

class StartTaskView(View):
    def post(self, request):
        # Submit task (returns immediately)
        task = long_running_task.delay(10)

        return JsonResponse({
            'task_id': task.id,
            'status': 'submitted'
        })


class TaskStatusView(View):
    def get(self, request, task_id):
        from celery.result import AsyncResult

        task = AsyncResult(task_id)

        return JsonResponse({
            'task_id': task_id,
            'status': task.status,
            'result': task.result if task.ready() else None
        })
```

### Usage Flow

```bash
# Terminal 1: Start Celery worker
celery -A config worker --loglevel=info

# Terminal 2: Django server
python manage.py runserver

# Browser: POST to /api/start_task
# Response: {task_id: 'abc-123-def-456', status: 'submitted'}

# Browser: GET /api/task/abc-123-def-456/status
# Response (while running): {status: 'STARTED', result: null}
# Response (after 10s): {status: 'SUCCESS', result: 'Slept for 10 seconds'}
```

---

## Retry Logic

Celery can automatically retry failed tasks:

```python
@shared_task(bind=True, autoretry_for=(Exception,))
def resilient_task(self):
    try:
        result = call_unreliable_api()
        return result
    except APIError as exc:
        # Retry with exponential backoff
        # 1s, 2s, 4s, 8s, 16s...
        countdown = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=countdown)
```

---

## Monitoring

### Flower (Web Dashboard)

```bash
pip install flower

# Start Flower
celery -A config flower

# Access http://localhost:5555
# See:
# - Active tasks
# - Worker status
# - Task history
# - Queue sizes
```

### Command Line

```bash
# Check active workers
celery -A config inspect active

# Check what each worker is doing
celery -A config inspect active_queues

# Get task status
celery -A config inspect reserved
```

---

## When to Use Celery

### ✅ Good Use Cases
- Email sending (takes time)
- Image processing (CPU intensive)
- Web scraping (I/O intensive, long-running)
- Report generation (data aggregation)
- Database backups (resource intensive)
- API calls to external services (network delays)

### ❌ Not Needed
- Simple database queries (milliseconds)
- Calculations (instant)
- Cache lookups (microseconds)
- Authentication checks (instant)

---

## Celery vs Django Signals

| Feature | Celery | Django Signals |
|---------|--------|----------------|
| **Async** | Yes | No |
| **Distributed** | Yes | No |
| **Retries** | Built-in | Manual |
| **Scheduling** | Yes | No |
| **Monitoring** | Flower | None |
| **Persistence** | Yes | No |
| **Use Case** | Long tasks | Post-save hooks |

---

## Architecture Comparison

### Without Celery (Blocking)
```
Request → Do Work → Response (user waits)
```

### With Celery (Non-blocking)
```
Request → Queue Job → Response (instant)
                ↓
           [Worker Process]
           Do Work → Store Result

User → Poll Status → Get Result
```

---

## Official Resources

- **Celery Documentation**: https://docs.celeryproject.io/
- **Celery Best Practices**: https://docs.celeryproject.io/en/stable/userguide/
- **Flower Docs**: https://flower.readthedocs.io/

---

## Next Steps

1. **Read this document** (you're reading it) ✓
2. **Follow**: [02_celery_tutorial.md](../tutorials/02_celery_tutorial.md)
3. **Code**: Implement tasks in `code/celery_tasks/`
4. **Experiment**: Run your own async task

Then move to **Lesson 3: Scrapy + Django Integration**
