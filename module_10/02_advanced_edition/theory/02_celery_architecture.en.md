# Lesson 2: Celery + Redis Task Queue Architecture

**Goal**: Understand how to process long-running tasks asynchronously.

---

## The Problem: Blocking Operations

In web applications, some operations take a long time (e.g., sending emails, web scraping, processing images). If these run during a user's web request, the user has to wait, which leads to a poor experience.

**The Solution**: Run these long tasks in the background. The web application can immediately return a response to the user, while a separate process handles the heavy work.

---

## Celery: A Task Queue Framework

Celery is a distributed task queue that specializes in processing asynchronous jobs.

### Core Components

1.  **Web Application (Producer)**: Submits a job (a "task") to the queue.
2.  **Broker (Message Queue)**: A middleman (like **Redis**) that stores the queue of tasks waiting to be processed.
3.  **Celery Worker (Consumer)**: A separate background process that continuously picks up tasks from the broker and executes them.
4.  **Result Backend**: A place (often also **Redis**) where the worker stores the results of the tasks.

```
Django App ───► Redis Broker ───► Celery Worker
    ▲                 │                  │
    └─────────────────┴── Redis Backend ◄┘
```

---

## Key Concepts

- **Task**: A Python function, usually decorated with `@shared_task`, that represents a unit of work.
- **Broker**: Stores tasks. Redis is a popular choice because it's fast and in-memory.
- **Worker**: Executes tasks. You can run multiple workers to process tasks in parallel.
- **Backend**: Stores the state and result of a task, allowing your web app to check on its progress.

### Task Lifecycle

1.  **Submit**: Your Django view calls `my_task.delay(arg1)`. The task is sent to the broker.
2.  **Queue**: The broker holds the task until a worker is free.
3.  **Execute**: A worker picks up the task and runs the Python function.
4.  **Store Result**: Upon completion, the worker stores the return value or any error in the result backend.

### Task States

A task progresses through several states:
- `PENDING`: Waiting in the queue.
- `STARTED`: A worker has started executing it.
- `SUCCESS`: Completed successfully.
- `FAILURE`: An error occurred.
- `RETRY`: The task failed and will be retried.

---
## Additional Resources

- **Celery Documentation**: https://docs.celeryproject.io/
- **Flower (Celery Monitoring Tool)**: https://flower.readthedocs.io/
- **Introduction to Redis**: https://redis.io/docs/about/
