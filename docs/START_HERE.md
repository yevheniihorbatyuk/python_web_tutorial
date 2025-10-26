# 🚀 ПОЧНІТЬ ТУТ!

## Модуль 6: Реляційні бази даних та Асинхронне програмування

---

## ⚡ Швидкий Старт (5 хвилин)

### Крок 1: Підготувати середовище

```bash
cd python_web_tutorial
cp .env.example .env

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]

docker-compose up -d
python -m python_web_tutorial.tools.bootstrap_data
```

### Крок 2: Перевірити підключення

```bash
docker-compose exec postgres psql -U admin -d learning_db

# В psql:
\dt                              # Показати таблиці
SELECT COUNT(*) FROM customers;  # Перевірити дані
\q                               # Вийти
```

### Крок 3: Запустити приклади

```bash
# Async основи
python python_web_tutorial/async_examples/01_async_basics.py

# HTTP запити
python python_web_tutorial/async_examples/02_async_http_client.py

# Робота з БД
python python_web_tutorial/python_db/05_db_connection.py

# Jupyter (опціонально)
jupyter notebook python_web_tutorial/python_db/06_jupyter_db_operations.py
```

---

## 📖 Що Читати?

### Для Студентів:

1. **README.md** - Загальний опис та план заняття
2. **QUICKSTART.md** - Детальна інструкція запуску
3. **SUMMARY.md** - Весь матеріал у вигляді конспекту
4. **CHEATSHEET.md** - Швидкий довідник команд

### Для Викладачів:

1. **LESSON_PLAN.md** - Детальний сценарій заняття (3-4 години)
2. **PROJECT_OVERVIEW.md** - Повний опис проєкту

### Для Всіх:

**INDEX.md** - Навігація по всіх файлах проєкту

---

## 🎯 Що Вивчимо?

### 1. Асинхронне Програмування (90 хв)
- ✅ Event Loop та async/await
- ✅ Паралельні HTTP запити з aiohttp
- ✅ Прискорення в 5-10x
- 📁 Файли: `async_examples/01*.py`, `02*.py`

### 2. SQL та PostgreSQL (90 хв)
- ✅ SELECT, JOIN, GROUP BY
- ✅ SUBQUERY, Window Functions
- ✅ DataLemur-стиль задачі
- 📁 Файли: `sql_examples/04*.sql`

### 3. Python + PostgreSQL (60 хв)
- ✅ Підключення через psycopg2
- ✅ CRUD операції
- ✅ SQL Injection захист
- ✅ Транзакції
- 📁 Файли: `python_db/05*.py`

### 4. Аналіз Даних (30 хв)
- ✅ pandas + PostgreSQL
- ✅ RFM сегментація
- ✅ Візуалізація
- 📁 Файли: `python_db/06*.py`

---

## 📁 Структура Проєкту

```
python_web_tutorial/
├── 📘 Документація
│   ├── README.md           - Основний опис
│   ├── START_HERE.md       - Цей файл!
│   ├── QUICKSTART.md       - Швидкий старт
│   ├── LESSON_PLAN.md      - Сценарій заняття
│   └── SUMMARY.md          - Конспект
│
├── 🐍 Python Модулі
│   ├── async_examples/     - Async програмування
│   ├── python_db/          - Робота з БД
│   └── utils/              - Допоміжні функції
│
├── 💾 SQL та Дані
│   ├── data/               - SQL скрипти
│   └── sql_examples/       - SQL приклади
│
└── 🐳 Docker
    ├── docker-compose.yml  - Docker конфігурація
    └── Dockerfile          - Python контейнер
```

---

## 🆘 Проблеми?

### PostgreSQL не запускається?

```bash
docker-compose logs postgres
docker-compose restart postgres
```

### Порт зайнятий?

Змініть порт у `.env`:
```
POSTGRES_PORT=5433
```

### Python помилки?

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 💡 Корисні Команди

```bash
# Docker
docker-compose up -d              # Запустити
docker-compose down               # Зупинити
docker-compose ps                 # Статус
docker-compose logs -f postgres   # Логи

# PostgreSQL
docker-compose exec postgres psql -U admin -d learning_db

# Python
python async_examples/01_async_basics.py
python python_db/05_db_connection.py

# Jupyter
jupyter notebook
```

---

## 🎓 Рекомендована Послідовність

1. ✅ Прочитати README.md
2. ✅ Запустити Docker
3. ✅ Запустити async_examples/01_async_basics.py
4. ✅ Запустити async_examples/02_async_http_client.py
5. ✅ Попрацювати з sql_examples/04_sql_examples.sql
6. ✅ Запустити python_db/05_db_connection.py
7. ✅ Відкрити python_db/06_jupyter_db_operations.py в Jupyter
8. ✅ Прочитати SUMMARY.md

---

## 📚 Додаткові Ресурси

- [asyncio документація](https://docs.python.org/3/library/asyncio.html)
- [aiohttp документація](https://docs.aiohttp.org/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [DataLemur SQL Practice](https://datalemur.com/questions)

---

## ✅ Готово!

Тепер ви готові почати навчання! 🎉

**Наступний крок**: Відкрийте [README.md](README.md)

---

**Питання?** Перевірте [QUICKSTART.md](QUICKSTART.md) або [CHEATSHEET.md](CHEATSHEET.md)
