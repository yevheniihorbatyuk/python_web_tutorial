# Concurrency в Python: Потоки, Процеси, GIL

---

## Три моделі конкурентності

```
threading      → один процес, багато потоків, СПІЛЬНА пам'ять
multiprocessing → багато процесів, ОКРЕМА пам'ять (обхід GIL)
asyncio        → один потік, кооперативна багатозадачність (coroutines)
```

---

## GIL — Global Interpreter Lock

**Що це:** М'ютекс у CPython, який забезпечує що тільки ОДИН потік виконує Python байткод в певний момент.

**Навіщо існує:** Спрощує управління пам'яттю (reference counting). Без GIL CPython треба було б синхронізувати кожну операцію з об'єктами.

**Наслідки:**

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1   # read + write = НЕ атомарна операція!

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)  # Очікуємо 2_000_000, але буде менше!
                # Потоки перемикаються між read і write
```

**GIL звільняється під час I/O:**

```python
# Цей код ДІЙСНО паралельний з потоками
# Поки потік чекає відповіді від сервера — GIL вільний
import requests, threading

def fetch(url):
    return requests.get(url).status_code  # GIL звільняється тут

# Два запити "паралельно" (насправді — перемежовано на рівні I/O)
```

---

## threading

### Thread

```python
import threading
import time

def worker(name: str, delay: float) -> None:
    print(f"[{name}] старт")
    time.sleep(delay)   # I/O-like: GIL звільняється
    print(f"[{name}] фіниш")

t1 = threading.Thread(target=worker, args=("A", 1.0))
t2 = threading.Thread(target=worker, args=("B", 0.5))

t1.start()
t2.start()
t1.join()   # чекаємо завершення
t2.join()
# B фінішує першим (0.5s < 1.0s)
```

### Lock — базовий м'ютекс

```python
lock = threading.Lock()
counter = 0

def safe_increment():
    global counter
    with lock:          # тільки один потік за раз
        counter += 1    # тепер атомарно
```

### RLock — реентерабельний Lock

```python
rlock = threading.RLock()

def outer():
    with rlock:
        inner()     # якщо тут звичайний Lock — DEADLOCK!

def inner():
    with rlock:     # той самий потік може захопити повторно
        print("inner")

# RLock рахує кількість захоплень — звільняється тільки після рівної кількості release()
```

### Deadlock

```python
# КЛАСИЧНИЙ DEADLOCK — обидва потоки чекають один одного
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:
        time.sleep(0.1)   # потік B встигає захопити lock_b
        with lock_b:       # чекає lock_b → deadlock!
            print("thread1 done")

def thread2():
    with lock_b:
        time.sleep(0.1)   # потік A встигає захопити lock_a
        with lock_a:       # чекає lock_a → deadlock!
            print("thread2 done")
```

**Рішення:**
1. Завжди захоплювати замки в одному порядку
2. `threading.Lock()` з timeout: `lock.acquire(timeout=1.0)`
3. Перепроектувати щоб уникнути множинних замків

---

## multiprocessing

Кожен процес — окремий інтерпретатор Python зі своїм GIL.

```python
from concurrent.futures import ProcessPoolExecutor
import math

def cpu_heavy(n: int) -> int:
    return sum(range(n))

numbers = [10_000_000] * 4  # 4 важкі задачі

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(cpu_heavy, numbers))

# На 4-ядерному CPU це буде ~4x швидше ніж послідовно
```

**Обмеження:**
- Процеси не можуть напряму ділити пам'ять → `multiprocessing.Queue`, `Manager`
- Запуск процесу дорожчий ніж потоку (~50-100ms vs ~1ms)
- Серіалізація даних між процесами (pickle) має overhead

---

## concurrent.futures — єдиний API

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# I/O-bound: ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_url, urls))

# CPU-bound: ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(compute_heavy, tasks))
```

Однаковий API — легко переключатись між потоками і процесами.

---

## asyncio vs threading

```
asyncio                          threading
──────────────────────────────   ──────────────────────────────
Кооперативна (явне await)        Превентивна (ОС перемикає)
Один потік                       Кілька потоків
Без Race Condition                Race Condition можлива
Легше налагоджувати               Складніше (неявний порядок)
Кращий performance для I/O       Ок для I/O, погано для CPU
Потрібна async-бібліотека        Синхронні бібліотеки OK
```

**У web-розробці (module_06+): asyncio майже завжди правильний вибір.**
