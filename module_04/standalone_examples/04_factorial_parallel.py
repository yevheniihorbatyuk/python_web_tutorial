"""
Модуль 04.4: Факторіал — threads vs processes
===============================================

Що вивчається:
  1. Реальна задача (factorial) порівнюється трьома підходами
  2. Чому threading не прискорює CPU-bound задачу (GIL)
  3. Чому multiprocessing дає реальний speedup
  4. Overhead на spawn процесів: коли задача занадто мала — процеси повільніші
  5. Поріг: при якому розмірі задача "окупає" процес

Запуск: python 04_factorial_parallel.py
"""

import math
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


# ─── Задача: факторіал великого числа ─────────────────────────────────────────

def digit_sum_of_factorial(n: int) -> int:
    """Сума цифр n! — важка для CPU, нічого не передається по мережі."""
    result = math.factorial(n)
    return sum(int(d) for d in str(result))


# ─── Вимірювання одного підходу ───────────────────────────────────────────────

def measure(label: str, numbers: list[int], use: str) -> float:
    """
    use: "sequential" | "threads" | "processes"
    Повертає час виконання (секунди).
    """
    start = time.perf_counter()

    if use == "sequential":
        results = [digit_sum_of_factorial(n) for n in numbers]

    elif use == "threads":
        results = [None] * len(numbers)

        def worker(idx: int, n: int) -> None:
            results[idx] = digit_sum_of_factorial(n)

        threads = [threading.Thread(target=worker, args=(i, n)) for i, n in enumerate(numbers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    elif use == "processes":
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(digit_sum_of_factorial, numbers))

    elapsed = time.perf_counter() - start
    print(f"  {label:<35} → {elapsed:.3f}s   результат[0]={results[0]}")
    return elapsed


# ─── Тест 1: великі числа (процеси мають переваги) ───────────────────────────

def benchmark_large(n: int = 30_000, repeats: int = 4) -> None:
    print(f"\n=== Великі числа: factorial({n:,}) × {repeats} ===")
    print("  (розмір задачі перевищує overhead на spawn процесів)\n")

    numbers = [n] * repeats

    t_seq = measure("Послідовно", numbers, "sequential")
    t_thr = measure("Потоки (ThreadPoolExecutor)", numbers, "threads")
    t_pro = measure("Процеси (ProcessPoolExecutor)", numbers, "processes")

    print(f"\n  Прискорення потоків:  {t_seq / t_thr:.2f}x  (очікували >> 1, маємо ≈ 1)")
    print(f"  Прискорення процесів: {t_seq / t_pro:.2f}x  (справжній паралелізм)")


# ─── Тест 2: дрібні числа (overhead перевищує виграш) ────────────────────────

def benchmark_small(n: int = 500, repeats: int = 20) -> None:
    print(f"\n=== Дрібні числа: factorial({n}) × {repeats} ===")
    print("  (overhead на spawn процесів може перевищити виграш)\n")

    numbers = [n] * repeats

    t_seq = measure("Послідовно", numbers, "sequential")
    t_pro = measure("Процеси (ProcessPoolExecutor)", numbers, "processes")

    if t_pro > t_seq:
        overhead = t_pro - t_seq
        print(f"\n  Процеси ПОВІЛЬНІШІ на {overhead:.3f}s — overhead перевищив виграш!")
        print("  При малих задачах spawn нового процесу дорожчий за саму роботу.")
    else:
        print(f"\n  Прискорення: {t_seq / t_pro:.2f}x")


# ─── Тест 3: ThreadPoolExecutor — правильне використання (I/O-bound) ─────────

def benchmark_io_bound(delay: float = 0.3, repeats: int = 6) -> None:
    """
    ThreadPoolExecutor показує реальний speedup тільки для I/O-задач,
    де GIL звільняється (sleep симулює мережевий запит).
    """
    print(f"\n=== I/O-bound: sleep({delay}s) × {repeats} ===")
    print("  (ThreadPoolExecutor тут доречний — GIL звільняється)\n")

    def io_task(i: int) -> str:
        time.sleep(delay)
        return f"done-{i}"

    numbers = list(range(repeats))

    # Послідовно
    start = time.perf_counter()
    [io_task(i) for i in numbers]
    t_seq = time.perf_counter() - start
    print(f"  {'Послідовно':<35} → {t_seq:.3f}s")

    # Потоки
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=repeats) as executor:
        list(executor.map(io_task, numbers))
    t_thr = time.perf_counter() - start
    print(f"  {'ThreadPoolExecutor':<35} → {t_thr:.3f}s")

    print(f"\n  Прискорення: {t_seq / t_thr:.1f}x  ← ось де потоки дійсно корисні!")


# ─── Підсумкова таблиця рекомендацій ─────────────────────────────────────────

def print_recommendations() -> None:
    print("\n=== Рекомендації ===")
    print("""
  ┌──────────────────┬──────────────────────┬───────────────────────────┐
  │ Тип задачі       │ Підхід               │ Чому                      │
  ├──────────────────┼──────────────────────┼───────────────────────────┤
  │ I/O-bound        │ asyncio              │ один потік, event loop    │
  │ I/O-bound        │ ThreadPoolExecutor   │ GIL знімається при I/O   │
  │ CPU-bound        │ ProcessPoolExecutor  │ окремий GIL на процес     │
  │ Мала CPU-задача  │ Послідовно           │ overhead перевищує виграш │
  │ Велика CPU-задача│ ProcessPoolExecutor  │ реальний speedup          │
  └──────────────────┴──────────────────────┴───────────────────────────┘

  Поріг: задача > ~0.05s/unit → ProcessPool окупається
         задача < ~0.01s/unit → послідовно швидше через overhead""")


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    benchmark_large(n=30_000, repeats=4)
    benchmark_small(n=100, repeats=20)
    benchmark_io_bound(delay=0.3, repeats=6)
    print_recommendations()
