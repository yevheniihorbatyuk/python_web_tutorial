"""
Модуль 04.1: Потоки, Lock та Deadlock
========================================

Що вивчається:
  1. threading.Thread — базовий запуск паралельного коду
  2. Race condition — що відбувається без синхронізації
  3. threading.Lock — м'ютекс для безпечного доступу
  4. Deadlock — два потоки чекають один одного
  5. threading.RLock — вирішення проблеми вкладених замків

Запуск: python 01_threads_and_locks.py
"""

import threading
import time


# ─── 1. Базові потоки ─────────────────────────────────────────────────────────

def demo_basic_threads() -> None:
    print("\n=== 1. Базові потоки ===")

    def worker(name: str, delay: float) -> None:
        print(f"  [{name}] починає (затримка {delay}s)")
        time.sleep(delay)   # Симулює I/O-операцію; GIL звільняється тут
        print(f"  [{name}] закінчив")

    t1 = threading.Thread(target=worker, args=("A", 0.3))
    t2 = threading.Thread(target=worker, args=("B", 0.1))
    t3 = threading.Thread(target=worker, args=("C", 0.2))

    start = time.perf_counter()
    t1.start()
    t2.start()
    t3.start()
    t1.join()   # чекаємо завершення
    t2.join()
    t3.join()
    elapsed = time.perf_counter() - start

    print(f"  Загальний час: {elapsed:.2f}s (без потоків було б ~0.6s)")
    print("  B фінішував першим (найменша затримка)")


# ─── 2. Race Condition ────────────────────────────────────────────────────────

def demo_race_condition() -> None:
    print("\n=== 2. Race Condition (без Lock) ===")

    counter = 0

    def unsafe_increment(n: int) -> None:
        nonlocal counter
        for _ in range(n):
            counter += 1   # read + increment + write = НЕ атомарно!

    ITERATIONS = 100_000
    t1 = threading.Thread(target=unsafe_increment, args=(ITERATIONS,))
    t2 = threading.Thread(target=unsafe_increment, args=(ITERATIONS,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    expected = ITERATIONS * 2
    print(f"  Очікували: {expected:,}")
    print(f"  Отримали:  {counter:,}")
    if counter < expected:
        print(f"  Втрачено:  {expected - counter:,} операцій через race condition!")
    else:
        print("  (цього разу пощастило — потоки не перетнулись)")


# ─── 3. Lock — виправлення race condition ────────────────────────────────────

def demo_lock() -> None:
    print("\n=== 3. Lock — безпечний лічильник ===")

    counter = 0
    lock = threading.Lock()

    def safe_increment(n: int) -> None:
        nonlocal counter
        for _ in range(n):
            with lock:        # тільки один потік за раз
                counter += 1  # тепер атомарна секція

    ITERATIONS = 100_000
    t1 = threading.Thread(target=safe_increment, args=(ITERATIONS,))
    t2 = threading.Thread(target=safe_increment, args=(ITERATIONS,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    expected = ITERATIONS * 2
    print(f"  Очікували: {expected:,}")
    print(f"  Отримали:  {counter:,}")
    print(f"  Результат: {'✓ правильно' if counter == expected else '✗ помилка'}")


# ─── 4. Deadlock ──────────────────────────────────────────────────────────────

def demo_deadlock_with_timeout() -> None:
    print("\n=== 4. Deadlock (з timeout щоб не завісити програму) ===")

    lock_a = threading.Lock()
    lock_b = threading.Lock()
    results = []

    def thread1() -> None:
        # Захоплює A, потім намагається захопити B
        if lock_a.acquire(timeout=0.5):
            results.append("T1: захопив A")
            time.sleep(0.1)  # дає час потоку 2 захопити B
            if lock_b.acquire(timeout=0.5):
                results.append("T1: захопив B — виконано!")
                lock_b.release()
            else:
                results.append("T1: не зміг захопити B → deadlock виявлено")
            lock_a.release()

    def thread2() -> None:
        # Захоплює B, потім намагається захопити A (зворотній порядок!)
        if lock_b.acquire(timeout=0.5):
            results.append("T2: захопив B")
            time.sleep(0.1)  # дає час потоку 1 захопити A
            if lock_a.acquire(timeout=0.5):
                results.append("T2: захопив A — виконано!")
                lock_a.release()
            else:
                results.append("T2: не зміг захопити A → deadlock виявлено")
            lock_b.release()

    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for msg in results:
        print(f"  {msg}")

    print("\n  Рішення: завжди захоплювати замки в ОДНОМУ порядку (A → B)")


# ─── 5. RLock — реентерабельний замок ────────────────────────────────────────

def demo_rlock() -> None:
    print("\n=== 5. RLock — вкладені замки ===")

    rlock = threading.RLock()
    regular_lock = threading.Lock()

    def outer_function(use_rlock: bool) -> str:
        lock = rlock if use_rlock else regular_lock
        acquired = lock.acquire(timeout=0.1)
        if not acquired:
            return "DEADLOCK: outer не зміг захопити замок"
        try:
            return inner_function(use_rlock)
        finally:
            lock.release()

    def inner_function(use_rlock: bool) -> str:
        lock = rlock if use_rlock else regular_lock
        acquired = lock.acquire(timeout=0.1)
        if not acquired:
            return "DEADLOCK: inner не зміг захопити замок"
        try:
            return "OK: і outer, і inner виконались"
        finally:
            lock.release()

    print(f"  Звичайний Lock:  {outer_function(use_rlock=False)}")
    print(f"  RLock:           {outer_function(use_rlock=True)}")
    print("\n  RLock дозволяє одному потоку захоплювати замок кілька разів")
    print("  Звичайний Lock: якщо потік вже тримає замок → deadlock при повторній спробі")


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_basic_threads()
    demo_race_condition()
    demo_lock()
    demo_deadlock_with_timeout()
    demo_rlock()

    print("\n=== Підсумок ===")
    print("  threading.Thread  — паралельні потоки (I/O-bound)")
    print("  Lock              — захист від race condition")
    print("  RLock             — Lock для вкладених функцій одного потоку")
    print("  Deadlock          — завжди захоплювати в одному порядку або timeout")
    print("  Для CPU-bound     → дивіться 02_multiprocessing.py та 03_gil_explained.py")
