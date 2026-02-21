# Module 04 — Standalone Examples

Self-contained scripts. Кожен запускається незалежно.

---

## Файли

| # | Файл | Тема | Запуск |
|---|------|------|--------|
| 01 | [01_threads_and_locks.py](01_threads_and_locks.py) | Thread, Lock, RLock, deadlock | `python 01_threads_and_locks.py` |
| 02 | [02_multiprocessing.py](02_multiprocessing.py) | ProcessPoolExecutor: map() vs submit() | `python 02_multiprocessing.py` |
| 03 | [03_gil_explained.py](03_gil_explained.py) | GIL benchmark: потоки ≈ однопоточний для CPU | `python 03_gil_explained.py` |
| 04 | [04_factorial_parallel.py](04_factorial_parallel.py) | Threads vs Processes: реальна порівняльна таблиця | `python 04_factorial_parallel.py` |
| 05 | [05_rest_server.py](05_rest_server.py) | BaseHTTPRequestHandler: GET/POST без фреймворків | `python 05_rest_server.py` |
| 06 | [06_aiohttp_client.py](06_aiohttp_client.py) | aiohttp + asyncio.gather: sync vs async timing | `python 06_aiohttp_client.py` |

---

## Швидкий старт

```bash
# Потоки і замки (не потребує пакетів)
python 01_threads_and_locks.py

# Мультипроцесність (не потребує пакетів)
python 02_multiprocessing.py

# GIL benchmark (не потребує пакетів)
python 03_gil_explained.py

# Порівняння threads vs processes (не потребує пакетів)
python 04_factorial_parallel.py

# REST сервер (не потребує пакетів, запускається окремо)
python 05_rest_server.py
# → тестування в другому терміналі:
curl http://localhost:8080/hello
curl http://localhost:8080/contacts -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "email": "alice@example.com"}'

# Async HTTP (потрібен інтернет + aiohttp)
pip install aiohttp
python 06_aiohttp_client.py
```

---

## Залежності між файлами

```
01 (threads) ←── концепція Lock використовується у 05 (сервер)
03 (GIL)     ←── пояснює чому 04 (factorial) показує slowdown з потоками
05 (server)  ←── те що FastAPI робить автоматично (Module 12)
06 (aiohttp) ←── async-підхід, розвинутий у Module 06 (asyncio)
```

---

## Ключові висновки

| Задача | Правильний інструмент |
|--------|-----------------------|
| I/O-bound (мережа, файли) | `threading` або `asyncio` |
| CPU-bound (математика, обробка) | `multiprocessing` |
| Багато одночасних HTTP запитів | `aiohttp` + `asyncio.gather()` |
| HTTP сервер без фреймворку | `BaseHTTPRequestHandler` |
| HTTP сервер у production | FastAPI (Module 12) |
