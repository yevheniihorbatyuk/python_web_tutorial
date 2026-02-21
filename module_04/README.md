# Module 04: Web Basics

> **Prerequisite:** Module 02. This module covers concurrency and the foundations of Python web servers — concepts used throughout Module 06–14.

---

## What's Covered

| Topic | File | Key Ideas |
|-------|------|-----------|
| Threads + Locks | `01_threads_and_locks.py` | Thread, Lock, RLock, deadlock demo |
| Multiprocessing | `02_multiprocessing.py` | ProcessPoolExecutor, CPU-bound tasks |
| GIL explained | `03_gil_explained.py` | Why threads don't speed up CPU work |
| Factorial comparison | `04_factorial_parallel.py` | threads vs processes benchmark |
| REST server | `05_rest_server.py` | BaseHTTPRequestHandler GET/POST |
| Async HTTP | `06_aiohttp_client.py` | aiohttp + asyncio.gather(), sync vs async |

---

## Quick Start

```bash
cd standalone_examples

python 01_threads_and_locks.py    # deadlock demo + fix
python 02_multiprocessing.py      # process pool
python 03_gil_explained.py        # GIL benchmark
python 04_factorial_parallel.py   # comparison table

# Start REST server (runs until Ctrl+C)
python 05_rest_server.py
# In another terminal:
# curl http://localhost:8080/
# curl http://localhost:8080/hello
# curl -X POST http://localhost:8080/echo -H "Content-Type: application/json" -d '{"msg":"hi"}'

# Async HTTP demo (requires internet)
python 06_aiohttp_client.py
```

---

## Key Concepts

### Threads vs Processes vs Async

| | Threads | Processes | Async |
|-|---------|-----------|-------|
| Parallelism | No (GIL) | Yes | No (single thread) |
| Good for | I/O-bound | CPU-bound | I/O-bound (many) |
| Memory | Shared | Separate | Shared |
| Overhead | Low | High | Very low |
| Used in | Module 06 (asyncio) | Data science | Module 06–14 |

### GIL — Global Interpreter Lock

CPython дозволяє виконувати **тільки один потік одночасно**. Потоки перемикаються між I/O-операціями, тому для I/O-bound вони ефективні. Для CPU-bound — ні.

```python
# I/O-bound: чекаємо мережу → GIL звільняється під час очікування → threads OK
async def fetch_url(url): ...      # asyncio/aiohttp — ще краще

# CPU-bound: рахуємо → GIL не звільняється → threads = послідовно
factorial(100000)                  # → multiprocessing.Pool
```

### BaseHTTPRequestHandler

Найпростіший HTTP-сервер в stdlib, без фреймворків. Корисний щоб зрозуміти:
- Що таке HTTP request/response на низькому рівні
- Як FastAPI (module_12) або Django (module_10) обробляють запити "під капотом"

---

## Connection to Later Modules

| This module | → Used in |
|-------------|----------|
| asyncio, event loop | Module 06 (async SQLAlchemy, aiohttp) |
| HTTP request/response | Module 10 (Django), Module 12 (FastAPI) |
| I/O-bound vs CPU-bound | Module 08 (async DB, async Redis) |
| aiohttp | Module 06 (async_examples/02_async_http_client.py) |
