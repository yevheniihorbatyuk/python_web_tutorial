# Tutorial: Getting Started with Celery Task Queues

**Goal**: Build and run your first asynchronous tasks with Celery and Redis.

---

## Prerequisites

- Celery and Redis installed (`pip install celery redis`).
- A running Redis server. You can start one easily with Docker: `docker run -d -p 6379:6379 redis`.

---

## Step 1: Define a Celery App and a Task

1.  **Create a `tasks.py` file.** This is where you'll define your Celery application and your tasks.

    ```python
    from celery import Celery
    import time

    # 1. Create a Celery instance
    # The first argument is the name of the current module.
    # The `broker` argument specifies the URL of the message broker (Redis).
    # The `backend` argument specifies the URL of the result backend.
    app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

    # 2. Define a task
    @app.task
    def long_running_task(seconds):
        """A simple task that simulates a long operation by sleeping."""
        print(f"Task started: sleeping for {seconds} seconds.")
        time.sleep(seconds)
        print("Task finished.")
        return f"Slept for {seconds} seconds."
    ```

---

## Step 2: Start a Celery Worker

Open a new terminal, navigate to the directory containing `tasks.py`, and start a worker.

```bash
celery -A tasks worker --loglevel=info
```
- `-A tasks`: Specifies the application instance to use (the `app` object in `tasks.py`).
- `worker`: The command to start a worker process.
- `--loglevel=info`: Sets the logging level.

You should see the worker start up and report that it's ready to accept tasks.

---

## Step 3: Submit a Task

Now, let's give the worker a job to do.

1.  **Open another terminal** and start a Python shell.
    ```bash
    python
    ```
2.  **Import your task and run it asynchronously** using the `.delay()` method.

    ```python
    from tasks import long_running_task

    # This sends the task to the message broker.
    # It returns an AsyncResult object immediately.
    result = long_running_task.delay(5)

    print(f"Task submitted with ID: {result.id}")
    ```
    - `.delay()` is a shortcut for `.apply_async()`. It sends the task to the queue and returns control to you right away.

---

## Step 4: Check the Task's Status and Result

In the same Python shell, you can check the state of your task.

```python
# Check if the task is finished
>>> result.ready()
False

# Check the status
>>> result.status
'PENDING' # Or 'STARTED' if the worker has picked it up

# Wait for the task to complete and get the result
# This will block until the result is available.
>>> final_result = result.get(timeout=10)
>>> print(final_result)
'Slept for 5 seconds.'

# Now the task is ready
>>> result.ready()
True

>>> result.status
'SUCCESS'
```

While you are waiting for the result, you can observe the logs in your Celery worker's terminal to see it pick up and execute the task.
