"""
Advanced Async Patterns in FastAPI

Master asynchronous programming:
- Async/await fundamentals
- Concurrent database operations
- Event loop management
- Common async gotchas
"""

import asyncio
import time
from typing import List
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# ============================================================================
# 1. ASYNC/AWAIT BASICS
# ============================================================================

async def fetch_data(url: str, delay: float) -> dict:
    """Simulate async I/O operation (e.g., HTTP request)."""
    print(f"⏳ Fetching {url}...")
    await asyncio.sleep(delay)  # Simulate I/O delay
    print(f"✅ Done fetching {url}")
    return {"url": url, "data": "response"}

async def async_example_1():
    """Single async operation."""
    print("\n=== Example 1: Single Async Operation ===")
    result = await fetch_data("http://api.example.com/1", 2)
    print(f"Result: {result}")

async def async_example_2():
    """Running multiple operations concurrently with gather."""
    print("\n=== Example 2: Concurrent Operations with gather ===")

    # Sequential (slow: 2 + 2 + 2 = 6 seconds)
    print("\n⏱️ Sequential:")
    start = time.time()
    r1 = await fetch_data("http://api1.example.com", 2)
    r2 = await fetch_data("http://api2.example.com", 2)
    r3 = await fetch_data("http://api3.example.com", 2)
    print(f"⏱️ Sequential took {time.time() - start:.1f}s")

    # Concurrent (fast: ~2 seconds because they run in parallel)
    print("\n⏱️ Concurrent with gather:")
    start = time.time()
    results = await asyncio.gather(
        fetch_data("http://api1.example.com", 2),
        fetch_data("http://api2.example.com", 2),
        fetch_data("http://api3.example.com", 2)
    )
    print(f"⏱️ Concurrent took {time.time() - start:.1f}s")
    print(f"Results: {results}")

# ============================================================================
# 2. CONCURRENT DATABASE OPERATIONS
# ============================================================================

# SQLAlchemy async setup
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def slow_database_query(query_id: int, delay: float = 1):
    """Simulate a slow database query."""
    print(f"⏳ Query {query_id} starting...")
    await asyncio.sleep(delay)
    print(f"✅ Query {query_id} completed")
    return {"id": query_id, "result": "data"}

async def concurrent_db_example():
    """Run multiple database queries concurrently."""
    print("\n=== Concurrent Database Queries ===")

    # Bad: Sequential queries (slow)
    print("\n❌ Sequential (slow):")
    start = time.time()
    r1 = await slow_database_query(1, 1)
    r2 = await slow_database_query(2, 1)
    r3 = await slow_database_query(3, 1)
    print(f"Sequential took {time.time() - start:.1f}s")

    # Good: Concurrent queries (fast)
    print("\n✅ Concurrent (fast):")
    start = time.time()
    results = await asyncio.gather(
        slow_database_query(1, 1),
        slow_database_query(2, 1),
        slow_database_query(3, 1)
    )
    print(f"Concurrent took {time.time() - start:.1f}s")
    print(f"Results: {results}")

# ============================================================================
# 3. ERROR HANDLING IN ASYNC CODE
# ============================================================================

async def failing_operation(op_id: int):
    """Operation that might fail."""
    await asyncio.sleep(1)
    if op_id == 2:
        raise ValueError(f"Operation {op_id} failed!")
    return {"id": op_id, "status": "success"}

async def error_handling_example():
    """Handle errors in concurrent operations."""
    print("\n=== Error Handling in Async Code ===")

    # Option 1: Catch exception from gather
    print("\n1️⃣ Using return_exceptions=True:")
    results = await asyncio.gather(
        failing_operation(1),
        failing_operation(2),
        failing_operation(3),
        return_exceptions=True  # Don't raise, return exceptions
    )
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"   Operation {i}: ERROR - {result}")
        else:
            print(f"   Operation {i}: {result}")

    # Option 2: Handle exceptions individually
    print("\n2️⃣ Using try/except:")
    tasks = [
        failing_operation(1),
        failing_operation(2),
        failing_operation(3)
    ]
    for i, task in enumerate(tasks, 1):
        try:
            result = await task
            print(f"   Operation {i}: {result}")
        except Exception as e:
            print(f"   Operation {i}: ERROR - {e}")

# ============================================================================
# 4. STREAMING RESPONSES
# ============================================================================

async def data_generator():
    """Generate data stream asynchronously."""
    for i in range(1, 4):
        await asyncio.sleep(0.5)
        yield f"data chunk {i}\n"

# ============================================================================
# 5. TIMEOUTS AND CANCELLATION
# ============================================================================

async def long_operation(duration: float = 5):
    """Long running operation."""
    print(f"Starting long operation for {duration}s...")
    await asyncio.sleep(duration)
    print("Long operation completed")

async def timeout_example():
    """Handle operation timeouts."""
    print("\n=== Timeouts ===")

    # Operation that completes within timeout
    print("\n✅ Operation completes in time:")
    try:
        result = await asyncio.wait_for(long_operation(2), timeout=5)
    except asyncio.TimeoutError:
        print("Operation timed out!")

    # Operation that exceeds timeout
    print("\n❌ Operation exceeds timeout:")
    try:
        result = await asyncio.wait_for(long_operation(5), timeout=2)
    except asyncio.TimeoutError:
        print("Operation timed out (as expected)!")

# ============================================================================
# 6. FASTAPI ASYNC ROUTES
# ============================================================================

app = FastAPI(title="Advanced Async Patterns")

class Item(BaseModel):
    id: int
    name: str

@app.get("/items/")
async def list_items():
    """
    Async endpoint that fetches from multiple sources concurrently.
    """
    results = await asyncio.gather(
        fetch_data("db://items", 0.5),
        fetch_data("cache://items", 0.3),
        fetch_data("search://items", 0.7)
    )
    return {"items": results}

@app.get("/slow/{item_id}")
async def get_slow_item(item_id: int):
    """
    Endpoint with timeout protection.
    """
    try:
        # If this operation takes longer than 5 seconds, cancel it
        result = await asyncio.wait_for(
            slow_database_query(item_id, 2),
            timeout=5
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Operation timed out")

@app.get("/stream/")
async def stream_data():
    """
    Stream data asynchronously.
    """
    async def generate():
        for i in range(5):
            await asyncio.sleep(0.1)
            yield f"data: {i}\n"

    return generate()

# ============================================================================
# 7. BACKGROUND TASKS (FIRE AND FORGET)
# ============================================================================

async def background_task(task_id: int, duration: float):
    """Background task that runs independently."""
    print(f"🔄 Background task {task_id} started")
    await asyncio.sleep(duration)
    print(f"✅ Background task {task_id} completed")

@app.post("/trigger-task/")
async def trigger_task():
    """
    Create a background task without waiting for it.
    WARNING: Task will be lost if app restarts!
    For production, use Celery or similar.
    """
    # Create task but don't await
    asyncio.create_task(background_task(1, 2))

    return {"message": "Task triggered", "status": "background"}

# ============================================================================
# 8. COMMON ASYNC GOTCHAS
# ============================================================================

async def gotcha_examples():
    """Common mistakes and how to fix them."""
    print("\n=== Common Async Gotchas ===")

    # Gotcha 1: Blocking call in async function
    print("\n⚠️ Gotcha 1: Blocking I/O in async code")
    print("   ❌ WRONG: time.sleep(1)  # Blocks entire event loop")
    print("   ✅ RIGHT: await asyncio.sleep(1)  # Non-blocking")

    # Gotcha 2: Not awaiting coroutines
    print("\n⚠️ Gotcha 2: Forgetting to await")
    print("   ❌ WRONG: result = fetch_data(...)  # Returns coroutine, not data")
    print("   ✅ RIGHT: result = await fetch_data(...)")

    # Gotcha 3: Creating unnecessary tasks
    print("\n⚠️ Gotcha 3: Creating tasks for single operations")
    print("   ❌ WRONG: await asyncio.create_task(fetch_data(...))")
    print("   ✅ RIGHT: await fetch_data(...)")

    # Gotcha 4: Resource leaks
    print("\n⚠️ Gotcha 4: Not closing connections")
    print("   ❌ WRONG: engine = create_async_engine(...)")
    print("   ✅ RIGHT: async with engine.connect() as conn: ...")

# ============================================================================
# EXAMPLES TO RUN
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("ADVANCED ASYNC PATTERNS")
    print("="*60)

    # Run examples
    asyncio.run(async_example_1())
    asyncio.run(async_example_2())
    asyncio.run(concurrent_db_example())
    asyncio.run(error_handling_example())
    asyncio.run(timeout_example())
    asyncio.run(gotcha_examples())

    print("\n" + "="*60)
    print("To see FastAPI async routes in action, run:")
    print("  uvicorn async_patterns:app --reload")
    print("Then visit: http://localhost:8000/docs")
    print("="*60)
