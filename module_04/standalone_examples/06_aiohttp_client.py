"""
Модуль 04.6: aiohttp — async HTTP клієнт
==========================================

Що вивчається:
  1. aiohttp.ClientSession — async аналог requests
  2. asyncio.gather() — паралельні запити без очікування кожного окремо
  3. Порівняння: sync vs async час (реальний speedup для I/O-bound)
  4. Обробка помилок: timeout, з'єднання відхилено, HTTP статус
  5. Публічне API без ключів для демонстрації

Потрібно: pip install aiohttp
Запуск:   python 06_aiohttp_client.py

Примітка: потрібен інтернет.
"""

import asyncio
import time
from typing import Any
from urllib.request import urlopen

try:
    import aiohttp
except ImportError:
    print("Встановіть aiohttp: pip install aiohttp")
    raise

# Публічні API без ключів (стабільні та безкоштовні)
URLS = [
    "https://httpbin.org/get",
    "https://httpbin.org/delay/1",      # 1 секунда затримки — сервер
    "https://httpbin.org/status/200",
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/users/1",
]

TIMEOUT_SECONDS = 10


# ─── 1. Синхронні запити (для порівняння) ─────────────────────────────────────

def fetch_sync(urls: list[str]) -> list[dict[str, Any]]:
    """Запити по черзі — кожен чекає завершення попереднього."""
    results = []
    for url in urls:
        try:
            with urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
                size = len(resp.read())
                results.append({"url": url, "status": resp.status, "bytes": size})
        except Exception as exc:
            results.append({"url": url, "error": str(exc)})
    return results


def run_sync(urls: list[str]) -> tuple[list[dict[str, Any]], float]:
    print("\n=== 1. Синхронні запити (послідовно) ===")

    start = time.perf_counter()
    results = fetch_sync(urls)
    elapsed = time.perf_counter() - start

    for r in results:
        if "error" in r:
            print(f"  ✗ {r['url'][:50]:<50} → {r['error']}")
        else:
            print(f"  ✓ {r['url'][:50]:<50} {r['status']} ({r['bytes']} bytes)")
    print(f"  Час: {elapsed:.2f}s")
    return results, elapsed


# ─── 2. Async запит до одного URL ─────────────────────────────────────────────

async def fetch_one(
    session: "aiohttp.ClientSession",
    url: str,
) -> dict[str, Any]:
    """
    Один async запит.
    await — точка де event loop може виконувати інші задачі.
    """
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    try:
        async with session.get(url, timeout=timeout) as resp:
            body = await resp.read()
            return {"url": url, "status": resp.status, "bytes": len(body)}
    except aiohttp.ClientConnectorError as exc:
        return {"url": url, "error": f"ConnectionError: {exc}"}
    except asyncio.TimeoutError:
        return {"url": url, "error": f"Timeout after {TIMEOUT_SECONDS}s"}
    except Exception as exc:
        return {"url": url, "error": str(exc)}


# ─── 3. Паралельні async запити ───────────────────────────────────────────────

async def fetch_all(urls: list[str]) -> tuple[list[dict[str, Any]], float]:
    """
    asyncio.gather() запускає всі корутини "одночасно".
    Насправді — event loop перемикається між ними при кожному await.
    Один потік, але I/O виконується паралельно.
    """
    print("\n=== 2. Async запити (asyncio.gather) ===")

    start = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        # Створюємо корутини — ще не запущені
        tasks = [fetch_one(session, url) for url in urls]
        # Запускаємо всі одночасно
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    for r in results:
        if "error" in r:
            print(f"  ✗ {r['url'][:50]:<50} → {r['error']}")
        else:
            print(f"  ✓ {r['url'][:50]:<50} {r['status']} ({r['bytes']} bytes)")
    print(f"  Час: {elapsed:.2f}s")
    return list(results), elapsed


# ─── 4. Обробка помилок детально ──────────────────────────────────────────────

async def demo_error_handling() -> None:
    print("\n=== 3. Обробка помилок ===")

    problematic_urls = [
        "https://httpbin.org/status/404",     # Not Found — не помилка мережі
        "https://httpbin.org/status/500",     # Server Error
        "https://httpbin.org/delay/30",       # Timeout (наш limit = 10s)
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in problematic_urls]
        results = await asyncio.gather(*tasks)

    for r in results:
        short_url = r["url"].split("httpbin.org")[1]
        if "error" in r:
            print(f"  ✗ {short_url:<20} → {r['error']}")
        else:
            # HTTP 404/500 — не виняток, просто статус
            print(f"  ✓ {short_url:<20} → HTTP {r['status']} (отримали, але це помилка)")


# ─── 5. asyncio.gather vs asyncio.create_task ────────────────────────────────

async def demo_create_task() -> None:
    """
    create_task() — альтернатива gather() для більшого контролю.
    Задача запускається одразу (не чекає await).
    """
    print("\n=== 4. create_task() — запуск без очікування ===")

    results: list[str] = []

    async def slow_task(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        msg = f"{name} завершив за {delay}s"
        results.append(msg)
        return msg

    # Задачі запускаються паралельно вже тут
    task_a = asyncio.create_task(slow_task("A", 0.3))
    task_b = asyncio.create_task(slow_task("B", 0.1))
    task_c = asyncio.create_task(slow_task("C", 0.2))

    start = time.perf_counter()
    await task_a  # чекаємо кожну явно
    await task_b
    await task_c
    elapsed = time.perf_counter() - start

    for r in results:   # порядок за ЗАВЕРШЕННЯМ
        print(f"  {r}")
    print(f"  Загальний час: {elapsed:.2f}s (не 0.6s)")


# ─── 6. Порівняльна таблиця ───────────────────────────────────────────────────

def print_comparison(sync_time: float, async_time: float, n: int) -> None:
    print("\n=== Підсумок: sync vs async ===")
    speedup = sync_time / async_time if async_time > 0 else 0

    print(f"  {'Підхід':<30} {'Час':>8}")
    print(f"  {'-'*40}")
    print(f"  {'Sync (послідовно)':<30} {sync_time:>7.2f}s")
    print(f"  {'Async (asyncio.gather)':<30} {async_time:>7.2f}s")
    print(f"  {'Прискорення':<30} {speedup:>7.1f}x")
    print()
    print("  asyncio — один потік, не паралелізм у CPU-сенсі,")
    print("  але I/O виконується паралельно через event loop.")
    print()
    print("  Коли aiohttp краще за requests:")
    print("  → багато одночасних запитів (crawler, API aggregation)")
    print("  → FastAPI/aiohttp сервер (весь стек async)")
    print()
    print("  Коли requests простіший:")
    print("  → один-два запити у скрипті")
    print("  → синхронний контекст (CLI, Django views)")


# ─── Запуск ──────────────────────────────────────────────────────────────────

async def main() -> None:
    _, sync_time = run_sync(URLS)
    _, async_time = await fetch_all(URLS)
    await demo_error_handling()
    await demo_create_task()
    print_comparison(sync_time, async_time, len(URLS))


if __name__ == "__main__":
    print("Демонстрація: aiohttp async HTTP клієнт")
    print(f"URLs: {len(URLS)} запитів (один з них має штучну затримку 1s)")
    asyncio.run(main())
