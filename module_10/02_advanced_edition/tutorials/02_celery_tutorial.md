# Tutorial: Getting Started with Celery Task Queues

**Time**: 45 minutes hands-on
**Goal**: Build and run your first async tasks
**Difficulty**: Intermediate

---

## Prerequisites

✅ Lesson 1 (Scrapy) complete
✅ Celery installed (`pip install celery`)
✅ Redis running (`docker-compose up redis`)
✅ Understand basic Python async/await concepts

---

## Step 1: Understand Task Queue Architecture

### The Problem We're Solving

```
WITHOUT Celery:
User clicks "Start Scrape" → Server blocks (5 minutes) → User waits → Response

WITH Celery:
User clicks "Start Scrape" → Task queued (instant) → User continues
                         → Background worker executes
                         → Result stored when done
```

### Components

```
Django View (submits task)
    ↓ task.delay()
Redis Broker (stores task)
    ↓ worker picks up
Celery Worker (executes)
    ↓ stores result
Redis Backend (result storage)
    ↓ task.get()
Django View (retrieves result)
```

---

## Step 2: Review Code Structure

Navigate to code:

```bash
cd /root/goit/python_web/module_10/02_advanced_edition/code/celery_tasks

ls -la
# Should show:
# __init__.py
# config.py      - Celery configuration
# tasks.py       - Task definitions
```

### config.py (Brief Overview)

```python
from celery import Celery

app = Celery('goit_module10')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### tasks.py (Brief Overview)

```python
from celery import shared_task

@shared_task
def example_task():
    return 'Task completed'
```

---

## Step 3: Start Celery Worker

### Terminal 1: Start Worker

```bash
cd /root/goit/python_web/module_10/02_advanced_edition

celery -A code.celery_tasks worker --loglevel=info
```

### Expected Output

```
celery@hostname v5.3.4 (modulename)
[config]
.> app:         celery_tasks
.> transport:   redis://localhost:6379/0
.> results:     redis://localhost:6379/1
.> concurrency: 8 (prefork)

[tasks]
  . celery_tasks.tasks.example_task
  . celery_tasks.tasks.long_task
  . celery_tasks.tasks.process_data
  . celery_tasks.tasks.resilient_task

[2024-01-15 10:30:00,123: INFO/MainProcess] Ready to accept tasks
```

**Success**: Worker is running and listening for tasks!

---

## Step 4: Submit Your First Task

### Terminal 2: Python Shell

```bash
# Navigate to module
cd /root/goit/python_web/module_10/02_advanced_edition

# Start Python
python3
```

### Execute Commands

```python
# Import
from code.celery_tasks.tasks import example_task

# Submit task (returns immediately)
result = example_task.delay()

# Get task ID
print(f'Task ID: {result.id}')
# Output: Task ID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p

# Check status
print(f'Status: {result.status}')
# Output: Status: PENDING (or SUCCESS if finished)

# Get result (waits max 30 seconds)
value = result.get(timeout=30)
print(f'Result: {value}')
# Output: Result: Task completed
```

### Check Worker Terminal

In Terminal 1, you should see:

```
[2024-01-15 10:30:15,456: INFO/Worker-1] Task example_task[1a2b3c...] received
[2024-01-15 10:30:15,457: INFO/Worker-1] Task example_task[1a2b3c...] started
[2024-01-15 10:30:15,458: INFO/Worker-1] Task example_task[1a2b3c...] succeeded
```

---

## Step 5: Try Long-Running Task

### Submit Task with Progress

```python
from code.celery_tasks.tasks import long_task

# Submit task that sleeps for 5 seconds
task = long_task.delay(5)

print(f'Task submitted: {task.id}')
# Output: Task submitted: abc123def456

# Check progress while running
import time
while not task.ready():
    info = task.info
    print(f'Progress: {info.get("percent", 0):.1f}%')
    time.sleep(1)

# Get final result
result = task.get()
print(f'Result: {result}')
# Output: Result: Slept for 5 seconds
```

### Expected Output (in Real Time)

```
Progress: 20.0%
Progress: 40.0%
Progress: 60.0%
Progress: 80.0%
Progress: 100.0%
Result: Slept for 5 seconds
```

---

## Step 6: Handle Task Failures

### Task That Might Fail

```python
from code.celery_tasks.tasks import resilient_task

# This task will fail (has "error" in URL)
task = resilient_task.delay('https://example.com/error')

# Wait for result (with retries)
try:
    result = task.get(timeout=30)
except Exception as e:
    print(f'Task failed: {e}')
    print(f'Status: {task.status}')
```

### What Happens

1. Task executes
2. Fails (ValueError)
3. Automatically retries (exponential backoff)
4. Retries: 1s, 2s, 4s, 8s, 16s
5. If still fails after max retries, raises exception

---

## Step 7: Batch Processing

### Process Multiple Items

```python
from code.celery_tasks.tasks import batch_process

# Submit batch job
items = ['apple', 'banana', 'cherry', 'date', 'elderberry']
task = batch_process.delay(items)

# Monitor progress
import time
while not task.ready():
    info = task.info
    if isinstance(info, dict):
        processed = info.get('processed', 0)
        total = info.get('total', 0)
        print(f'Progress: {processed}/{total} items')
    time.sleep(1)

# Get results
result = task.get()
print(f'Final result: {result}')
# Output: Final result: {'total': 5, 'processed': 5, 'failed': 0, ...}
```

---

## Step 8: Monitor with Flower (Optional)

### Terminal 3: Start Flower

```bash
# Install Flower (if not installed)
pip install flower

# Start Flower dashboard
celery -A code.celery_tasks flower

# Access http://localhost:5555
```

### What You'll See

- **Tasks**: List of all executed tasks
- **Workers**: Status of worker processes
- **Graphs**: Real-time execution data
- **History**: Past task executions

---

## Step 9: Task Chaining (Pipeline Pattern)

### Execute Tasks Sequentially

```python
from celery import chain
from code.celery_tasks.tasks import extract_data, transform_data, load_data

# Chain: extract → transform → load
pipeline = chain(
    extract_data.s('database'),
    transform_data.s(),
    load_data.s(),
)

# Execute pipeline
task = pipeline.apply_async()

# Get final result
result = task.get()
print(f'Pipeline result: {result}')
# Output: Pipeline result: {'status': 'loaded', 'count': 3}
```

---

## Step 10: Scheduled Tasks (Celery Beat)

### View Beat Schedule

```python
from code.celery_tasks.config import app

# Print schedule
for task_name, task_config in app.conf.beat_schedule.items():
    print(f'{task_name}: {task_config["schedule"]}')
    # Output:
    # example-task-every-10-seconds: <schedule: 10.00 seconds>
    # example-task-daily: <crontab: * 0 * * * (m h d m dow)>
```

### Start Celery Beat (Optional)

```bash
# Terminal 4: Start Beat scheduler
celery -A code.celery_tasks beat --loglevel=info

# Expected output:
# [2024-01-15 10:35:00,000: INFO/MainProcess] Scheduler: Sending due task 'example-task-every-10-seconds'
# [2024-01-15 10:35:10,000: INFO/MainProcess] Scheduler: Sending due task 'example-task-every-10-seconds'
```

---

## Common Tasks

### Submit Task from Django View

```python
# views.py
from django.http import JsonResponse
from code.celery_tasks.tasks import long_task

def start_scraping(request):
    # Submit task
    task = long_task.delay(300)  # 5 minute scrape

    return JsonResponse({
        'task_id': task.id,
        'status': 'submitted'
    })

def check_status(request, task_id):
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    return JsonResponse({
        'status': task.status,
        'result': task.result if task.ready() else None,
        'info': task.info if task.state == 'PROGRESS' else None,
    })
```

### Check Task Status from CLI

```bash
# See what workers are doing
celery -A code.celery_tasks inspect active

# See worker status
celery -A code.celery_tasks inspect stats

# Revoke a task
celery -A code.celery_tasks revoke <task_id>

# Clear all tasks
celery -A code.celery_tasks purge
```

---

## Troubleshooting

### Worker Not Starting

**Problem**: `ImportError: cannot import name 'app'`

**Solution**:
```bash
# Make sure you're in right directory
cd /root/goit/python_web/module_10/02_advanced_edition

# Make sure Redis is running
redis-cli ping
# Output: PONG

# Check Python path
export PYTHONPATH=/root/goit/python_web/module_10/02_advanced_edition:$PYTHONPATH

# Restart worker
celery -A code.celery_tasks worker --loglevel=info
```

### Task Not Executing

**Problem**: Task submitted but not executed

**Solution**:
```bash
# Check if worker is listening
# In worker terminal, you should see:
# [2024-01-15 10:30:00,123: INFO/MainProcess] Ready to accept tasks

# Check Redis connection
redis-cli
> KEYS *
> GET celery-task-meta-<task_id>
```

### Slow Execution

**Problem**: Tasks take too long

**Solution**:
```python
# Check number of workers
celery -A code.celery_tasks inspect active_queues

# Increase concurrency
celery -A code.celery_tasks worker --concurrency=16

# Check Redis
redis-cli
> INFO stats
> DBSIZE
```

---

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Task** | Python function decorated with @shared_task |
| **Broker** | Redis queue storing tasks |
| **Worker** | Process executing tasks |
| **Backend** | Redis storage for results |
| **Task ID** | Unique identifier for tracking |
| **State** | PENDING, RECEIVED, STARTED, SUCCESS, FAILURE |
| **Progress** | Update status with `self.update_state()` |
| **Retry** | Automatic retry on failure with backoff |
| **Chain** | Execute tasks sequentially |
| **Flower** | Web dashboard for monitoring |

---

## Reference Commands

### Submit Tasks
```python
task = my_task.delay(arg1, arg2)           # Async
result = my_task.apply_async(args=[...])   # With options
result = my_task()                         # Sync (blocking)
```

### Get Results
```python
task.get()              # Wait for result (blocks)
task.ready()            # Check if done
task.status             # Current state
task.info               # Progress info
task.result             # Result value
```

### Task Options
```python
@shared_task(
    bind=True,                              # Get task instance
    autoretry_for=(Exception,),            # Auto-retry
    retry_kwargs={'max_retries': 5},       # Max 5 retries
    time_limit=3600,                       # 1 hour hard limit
)
def my_task(self):
    pass
```

---

## Next Steps

1. ✅ You've run your first Celery tasks
2. 📖 Read [Celery Architecture](../theory/02_celery_architecture.md) for deeper understanding
3. 🔧 Modify tasks in `code/celery_tasks/tasks.py`
4. 📚 Move to [Lesson 3: Integration](03_integration_tutorial.md)

---

Congratulations! You understand async task processing now. 🎉
