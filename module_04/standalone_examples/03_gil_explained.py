"""
Модуль 04.3: GIL — Global Interpreter Lock
============================================

Що вивчається:
  1. Що таке GIL і навіщо він існує
  2. Benchmark: потоки + CPU-задача ≈ однопоточний час
  3. Benchmark: процеси + CPU-задача → справжній паралелізм
  4. GIL звільняється при I/O → потоки корисні для мережі/файлів
  5. Висновок: потоки vs процеси — яку задачу маєш

Запуск: python 03_gil_explained.py
"""

import math
import threading
import time
from concurrent.futures import ProcessPoolExecutor


# ─── CPU-bound функція (GIL НЕ звільняється під час роботи) ──────────────────

def cpu_task(n: int) -> int:
    """Чиста математика — GIL утримується весь час."""
    total = 0
    for i in range(1, n + 1):
        total += math.isqrt(i * i + i)  # цілочисельний sqrt
    return total


# ─── 1. Baseline: однопоточне виконання ───────────────────────────────────────

def run_single_thread(n: int, repeats: int) -> float:
    print("\n=== 1. Однопоточне виконання ===")

    start = time.perf_counter()
    for _ in range(repeats):
        cpu_task(n)
    elapsed = time.perf_counter() - start

    print(f"  {repeats} задачі по cpu_task({n:,})")
    print(f"  Час: {elapsed:.3f}s")
    return elapsed


# ─── 2. Потоки з CPU-задачею — демонструємо GIL ──────────────────────────────

def run_threads(n: int, repeats: int) -> float:
    """
    Очікування: паралельно → швидше.
    Реальність: GIL дозволяє тільки одному потоку виконувати Python-байткод
    одночасно → час ≈ однопоточний, ще й з overhead на переключення контексту.
    """
    print("\n=== 2. Потоки (threading.Thread) ===")

    results = [None] * repeats

    def worker(idx: int) -> None:
        results[idx] = cpu_task(n)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(repeats)]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    print(f"  {repeats} потоків, кожен cpu_task({n:,})")
    print(f"  Час: {elapsed:.3f}s")
    print("  ← очікували прискорення, але GIL блокує паралельне виконання")
    return elapsed


# ─── 3. Процеси з CPU-задачею — справжній паралелізм ─────────────────────────

def run_processes(n: int, repeats: int) -> float:
    """
    Кожен процес має ВЛАСНИЙ Python інтерпретатор і власний GIL.
    → паралельне виконання на різних CPU ядрах → реальний speedup.
    """
    print("\n=== 3. Процеси (ProcessPoolExecutor) ===")

    start = time.perf_counter()
    with ProcessPoolExecutor() as executor:
        list(executor.map(cpu_task, [n] * repeats))
    elapsed = time.perf_counter() - start

    print(f"  {repeats} процесів, кожен cpu_task({n:,})")
    print(f"  Час: {elapsed:.3f}s")
    print("  ← кожен процес = окремий GIL → справжній паралелізм")
    return elapsed


# ─── 4. Потоки з I/O — тут GIL звільняється ──────────────────────────────────

def run_threads_io(delay: float, repeats: int) -> float:
    """
    time.sleep() звільняє GIL → потоки справді паралельні під час I/O.
    Це пояснює чому потоки корисні для мережевих запитів, читання файлів.
    """
    print("\n=== 4. Потоки з I/O (sleep симулює мережу) ===")

    threads = [
        threading.Thread(target=time.sleep, args=(delay,))
        for _ in range(repeats)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    sequential_would_be = delay * repeats
    print(f"  {repeats} потоків, кожен спить {delay}s")
    print(f"  Послідовно було б: {sequential_would_be:.1f}s")
    print(f"  Паралельно:        {elapsed:.3f}s")
    print(f"  Прискорення: {sequential_would_be / elapsed:.1f}x  ← GIL звільняється під час sleep")
    return elapsed


# ─── 5. Підсумкова таблиця ────────────────────────────────────────────────────

def print_summary(
    single: float,
    threads_cpu: float,
    processes_cpu: float,
    threads_io: float,
    repeats: int,
    io_delay: float,
) -> None:
    print("\n=== 5. Підсумкова таблиця ===")

    io_sequential = io_delay * repeats

    print(f"\n  {'Підхід':<35} {'Час':>8} {'Vs single':>10}")
    print(f"  {'-'*55}")
    print(f"  {'Однопоточний (baseline)':<35} {single:>7.3f}s {'1.00x':>10}")
    print(f"  {'Потоки + CPU-задача':<35} {threads_cpu:>7.3f}s {single/threads_cpu:>9.2f}x")
    print(f"  {'Процеси + CPU-задача':<35} {processes_cpu:>7.3f}s {single/processes_cpu:>9.2f}x")
    print(f"  {'Потоки + I/O (послідовно б: {:.1f}s)'.format(io_sequential):<35} {threads_io:>7.3f}s {io_sequential/threads_io:>9.2f}x")

    print("""
  Правило вибору:
  ┌─────────────────┬─────────────────────────────────┐
  │ Задача          │ Що обрати                       │
  ├─────────────────┼─────────────────────────────────┤
  │ I/O-bound       │ threading або asyncio           │
  │ CPU-bound       │ multiprocessing                 │
  │ Мішана          │ ProcessPool + async всередині   │
  └─────────────────┴─────────────────────────────────┘""")


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    N = 500_000   # ітерацій у cpu_task
    REPEATS = 4   # кількість паралельних задач
    IO_DELAY = 0.5

    single_time = run_single_thread(N, REPEATS)
    threads_cpu_time = run_threads(N, REPEATS)
    processes_cpu_time = run_processes(N, REPEATS)
    threads_io_time = run_threads_io(IO_DELAY, REPEATS)

    print_summary(
        single_time,
        threads_cpu_time,
        processes_cpu_time,
        threads_io_time,
        REPEATS,
        IO_DELAY,
    )

    print("\n=== GIL: чому він існує ===")
    print("  CPython керує пам'яттю через reference counting.")
    print("  Без GIL: два потоки можуть одночасно змінювати лічильник → corruption.")
    print("  GIL — глобальний замок на весь інтерпретатор: простіше, але обмежує CPU-паралелізм.")
    print("  Python 3.13+ (GIL-free build) — експериментально знімає це обмеження.")
