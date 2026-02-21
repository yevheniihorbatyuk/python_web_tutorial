# Module 04 — Learning Path

4 кроки від "що таке потік" до "мій перший REST API сервер".

---

## Крок 1: Потоки, Lock та Deadlock

**Файл:** `standalone_examples/01_threads_and_locks.py`

```bash
python 01_threads_and_locks.py
```

**Що вивчається:**
- `threading.Thread` — запуск коду паралельно (або майже паралельно через GIL)
- Race condition — два потоки змінюють одну змінну, результат непередбачуваний
- `threading.Lock` — м'ютекс, тільки один потік за раз
- Deadlock — два потоки чекають один одного назавжди
- `threading.RLock` (Reentrant Lock) — один потік може захопити кілька разів

**Ключове питання:** Чому Lock не захищає від deadlock?
→ Lock = "один потік". Якщо потік A тримає Lock1 і чекає Lock2,
  а потік B тримає Lock2 і чекає Lock1 — обидва чекають вічно.
  RLock дозволяє одному потоку захопити замок повторно (для вкладених функцій).

---

## Крок 2: Multiprocessing та GIL

**Файли:**
- `standalone_examples/02_multiprocessing.py`
- `standalone_examples/03_gil_explained.py`
- `standalone_examples/04_factorial_parallel.py`

```bash
python 03_gil_explained.py   # спочатку розібратись з GIL
python 04_factorial_parallel.py   # потім порівняти підходи
```

**Що вивчається:**
- GIL (Global Interpreter Lock) — CPython дозволяє один потік за раз для Python-коду
- Потоки ефективні для I/O-bound (читання файлу, HTTP-запит) — GIL звільняється під час очікування
- Потоки НЕ ефективні для CPU-bound (обчислення) — GIL тримається весь час
- `multiprocessing.Pool` / `ProcessPoolExecutor` — справжній паралелізм для CPU-задач
- `concurrent.futures` — єдиний API для потоків і процесів

**Ключове питання:** Коли процеси, коли потоки, коли asyncio?

| Задача | Рекомендація |
|--------|-------------|
| Завантаження файлів, HTTP-запити | `asyncio` / `aiohttp` |
| Багато одночасних I/O-операцій | `asyncio` |
| CPU-важкі обчислення | `multiprocessing` |
| Легкі фонові задачі | `threading` |

---

## Крок 3: REST сервер без фреймворку

**Файл:** `standalone_examples/05_rest_server.py`

```bash
python 05_rest_server.py
# Сервер запущено на http://localhost:8080
```

Тестування в іншому терміналі:
```bash
curl http://localhost:8080/
curl http://localhost:8080/hello
curl -X POST http://localhost:8080/echo \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello World"}'
```

**Що вивчається:**
- `http.server.BaseHTTPRequestHandler` — обробник HTTP-запитів у stdlib
- Що знаходиться "під капотом" FastAPI та Django
- HTTP метод (GET/POST), шлях (path), заголовки (headers), тіло (body)
- Статус коди: 200 OK, 404 Not Found, 405 Method Not Allowed

**Чому це важливо перед FastAPI (Module 12)?**
→ FastAPI автоматизує все що ми тут пишемо вручну:
  парсинг запитів, маршрутизацію, серіалізацію JSON, статус коди.
  Коли щось не так у FastAPI — ви розумієте що відбувається на рівні HTTP.

---

## Крок 4: Async HTTP з aiohttp

**Файл:** `standalone_examples/06_aiohttp_client.py`

```bash
pip install aiohttp
python 06_aiohttp_client.py
```

**Що вивчається:**
- `aiohttp.ClientSession` — асинхронний HTTP-клієнт
- `asyncio.gather()` — запуск кількох корутин "одночасно"
- Порівняння: синхронний fetch (послідовно) vs asyncio (паралельно по I/O)
- WebSocket echo demo (без зовнішнього сервера)

**Зв'язок з Module 06:**
`module_06/async_examples/02_async_http_client.py` — той самий aiohttp
але з більшим акцентом на ETL-патерни та реальні дані.

---

## Підсумок: Коли що використовувати

```
              Вид задачі
                  │
         CPU-bound│  I/O-bound
                  │
    Одна операція │  ──────────── threading або просто await
                  │
    Багато задач  │  ──────────── asyncio.gather() / asyncio.Queue
                  │
    Важкі обчисл. │  ──────────── multiprocessing.Pool
                  │

Правило: asyncio першочергово для web.
         multiprocessing для числодробилок.
         threading рідко — тільки якщо немає asyncio-версії бібліотеки.
```
