"""
Модуль 04.2: Мультипроцесність
================================

Що вивчається:
  1. ProcessPoolExecutor — пул процесів для CPU-bound задач
  2. map() vs submit() — два стилі розподілу роботи
  3. Результати через Future — неблокуючий збір
  4. Порівняння: послідовно vs паралельно (реальний speedup)
  5. Коли НЕ варто використовувати процеси (overhead vs задача)

Запуск: python 02_multiprocessing.py
"""

import math
import time
from concurrent.futures import ProcessPoolExecutor, as_completed


# ─── Спільна задача для порівняння ────────────────────────────────────────────

def heavy_computation(n: int) -> int:
    """
    CPU-bound задача: сума цифр n!
    Навмисно проста, але потребує реального CPU часу.
    """
    result = math.factorial(n)
    return sum(int(d) for d in str(result))


# ─── 1. Послідовне виконання (для порівняння) ─────────────────────────────────

def run_sequential(numbers: list[int]) -> tuple[list[int], float]:
    print("\n=== 1. Послідовне виконання ===")

    start = time.perf_counter()
    results = [heavy_computation(n) for n in numbers]
    elapsed = time.perf_counter() - start

    print(f"  Задачі: {numbers}")
    print(f"  Час:    {elapsed:.3f}s")
    return results, elapsed


# ─── 2. ProcessPoolExecutor.map() — найпростіший спосіб ──────────────────────

def run_pool_map(numbers: list[int]) -> tuple[list[int], float]:
    """
    map() — аналог вбудованого map(), але паралельно.
    Повертає результати в тому САМОМУ порядку що й вхідні дані.
    """
    print("\n=== 2. ProcessPoolExecutor.map() ===")

    start = time.perf_counter()
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(heavy_computation, numbers))
    elapsed = time.perf_counter() - start

    print(f"  Задачі: {numbers}")
    print(f"  Час:    {elapsed:.3f}s")
    print("  Порядок результатів: ЗБЕРЕЖЕНО (map гарантує)")
    return results, elapsed


# ─── 3. ProcessPoolExecutor.submit() — гнучкий контроль ──────────────────────

def run_pool_submit(numbers: list[int]) -> tuple[list[int], float]:
    """
    submit() — надсилає кожну задачу окремо, повертає Future.
    as_completed() → повертає результати по мірі готовності (порядок не гарантовано).
    """
    print("\n=== 3. ProcessPoolExecutor.submit() + as_completed() ===")

    start = time.perf_counter()
    results = []

    with ProcessPoolExecutor() as executor:
        # Словник Future → вхідне значення для трасування
        future_to_n = {executor.submit(heavy_computation, n): n for n in numbers}

        for future in as_completed(future_to_n):
            n = future_to_n[future]
            result = future.result()
            results.append(result)
            print(f"  factorial({n:,}) digit sum = {result}  ← завершено")

    elapsed = time.perf_counter() - start
    print(f"  Час: {elapsed:.3f}s")
    print("  Порядок: за часом ЗАВЕРШЕННЯ (не вхідним порядком)")
    return results, elapsed


# ─── 4. Явне задання кількості воркерів ──────────────────────────────────────

def run_custom_workers(numbers: list[int], max_workers: int) -> None:
    """
    max_workers: за замовчуванням = кількість CPU ядер.
    Явно задавати варто коли:
      - маєте I/O (можна більше ніж CPU)
      - обмежена RAM (менше ніж CPU)
    """
    import os

    cpu_count = os.cpu_count() or 1
    print(f"\n=== 4. Власні воркери (max_workers={max_workers}, CPU ядер={cpu_count}) ===")

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(heavy_computation, numbers))
    elapsed = time.perf_counter() - start

    print(f"  Час: {elapsed:.3f}s")
    print(f"  Результати: {results[:3]}{'...' if len(results) > 3 else ''}")


# ─── 5. Порівняльна таблиця ───────────────────────────────────────────────────

def print_comparison(sequential_time: float, parallel_time: float, n_jobs: int) -> None:
    print("\n=== 5. Порівняння ===")

    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    overhead = max(0, parallel_time - sequential_time / n_jobs)

    print(f"  {'Показник':<30} {'Значення':>10}")
    print(f"  {'-'*42}")
    print(f"  {'Послідовний час':<30} {sequential_time:>9.3f}s")
    print(f"  {'Паралельний час':<30} {parallel_time:>9.3f}s")
    print(f"  {'Прискорення (speedup)':<30} {speedup:>9.2f}x")
    print(f"  {'Overhead (spawn + IPC)':<30} {overhead:>9.3f}s")
    print()
    print("  Висновок: ProcessPoolExecutor окупається лише для задач ≥ ~0.1s/unit")
    print("  Для дрібних задач (мс) — overhead перевищує виграш")


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Задачі: factorial(n) для великих n — потребує CPU
    NUMBERS = [20_000, 22_000, 18_000, 25_000]

    seq_results, seq_time = run_sequential(NUMBERS)
    par_results, par_time = run_pool_map(NUMBERS)

    # Перевіряємо що результати однакові
    assert seq_results == par_results, "Результати відрізняються!"
    print("\n  ✓ map() повернув ті самі результати що й послідовний код")

    run_pool_submit(NUMBERS)
    run_custom_workers(NUMBERS, max_workers=2)
    print_comparison(seq_time, par_time, len(NUMBERS))

    print("\n=== Підсумок ===")
    print("  executor.map(fn, items)  → простіший, зберігає порядок")
    print("  executor.submit(fn, arg) → гнучкий, as_completed() для real-time")
    print("  ProcessPool ≠ ThreadPool: кожен процес — окремий Python інтерпретатор")
    print("  Аргументи передаються через pickle → мають бути серіалізовні")
    print("  Для I/O-bound → ThreadPoolExecutor (модуль 01)")
    print("  Для CPU-bound → ProcessPoolExecutor (цей файл)")
