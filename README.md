# 🐍 Python Web - Модуль 6: Реляційні бази даних та Асинхронне програмування

**Версія**: 2.0.0
**Статус**: Production Ready
**Рівні**: Basic + Advanced

---

## 🚀 Швидкий Старт

```bash
# 1. Запустити PostgreSQL
docker-compose up -d

# 2. Перевірити підключення
docker-compose exec postgres psql -U admin -d learning_db -c "SELECT COUNT(*) FROM customers;"

# 3. Запустити приклади
python async_examples/01_async_basics.py
```

**Детальна інструкція**: [docs/START_HERE.md](docs/START_HERE.md)

---

## 📚 Документація

### Основні Документи
- 📖 [START_HERE.md](docs/START_HERE.md) - **Почніть тут!** Швидкий старт для новачків
- 📘 [Базовий Модуль](docs/README.md) - Повний план заняття та опис
- 🚀 [Advanced Модулі](docs/ADVANCED_README.md) - Production patterns для Senior DS/DE
- ⚡ [QUICKSTART.md](docs/QUICKSTART.md) - Покрокова інструкція запуску

### Довідники
- 🎓 [LESSON_PLAN.md](docs/LESSON_PLAN.md) - Сценарій заняття на 3-4 години
- 📝 [SUMMARY.md](docs/SUMMARY.md) - Підсумковий конспект всього матеріалу
- ⌨️ [CHEATSHEET.md](docs/CHEATSHEET.md) - Швидкий довідник команд
- 📂 [INDEX.md](docs/INDEX.md) - Індекс всіх файлів проєкту

### Про Проєкт
- 📊 [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) - Детальний огляд проєкту

### 📜 Історія Змін
- [Update #1: Initial Release](docs/updates/01_initial_release.md) - v1.0.0 (25 Жовтня 2025)
- [Update #2: Advanced Modules](docs/updates/02_advanced_modules.md) - v2.0.0 (26 Жовтня 2025)

---

## 🎯 Два Рівні Навчання

### 📘 Базовий Рівень (для всіх)
**Тривалість**: 3-4 години

**Що вивчимо**:
- ✅ Event Loop та async/await
- ✅ Паралельні HTTP запити з aiohttp
- ✅ SQL: SELECT, JOIN, GROUP BY, SUBQUERY
- ✅ Python + PostgreSQL з psycopg2
- ✅ Jupyter для аналізу даних

**Модулі**:
- `async_examples/` - Асинхронне програмування
- `python_db/` - Робота з PostgreSQL
- `sql_examples/04_sql_examples.sql` - SQL приклади

### 🚀 Advanced Рівень (для Senior DS/DE)
**Тривалість**: +2-3 години

**Що вивчимо**:
- 🔥 Production ETL Pipeline з metrics
- 🏗️ Architectural Patterns (Repository, DI, Factory)
- 🤖 ML Feature Store pattern
- 📊 Advanced SQL (Cohort, Funnel, Time-series)
- 📈 Real-world DS/DE practices

**Модулі**:
- `advanced_examples/etl/` - Production ETL
- `advanced_examples/patterns/` - Clean Architecture
- `advanced_examples/ml_pipeline/` - ML Infrastructure
- `sql_examples/05_advanced_analytics.sql` - Advanced SQL

---

## 📁 Структура Проєкту

```
python_web/
├── 📚 docs/                           # Вся документація
│   ├── README.md                      # План базового модуля
│   ├── ADVANCED_README.md             # Advanced модулі
│   ├── START_HERE.md                  # Почніть тут!
│   └── updates/                       # Історія змін
│
├── 🐍 async_examples/                 # Асинхронне програмування
│   ├── 01_async_basics.py             # Event Loop основи
│   ├── 02_async_http_client.py        # HTTP з aiohttp
│   └── 03_websockets_demo.py          # WebSockets
│
├── 🚀 advanced_examples/              # Production patterns
│   ├── etl/                           # ETL Pipeline
│   ├── patterns/                      # Architectural Patterns
│   └── ml_pipeline/                   # ML Infrastructure
│
├── 🗄️ python_db/                      # Python + PostgreSQL
│   ├── 05_db_connection.py            # CRUD операції
│   └── 06_jupyter_db_operations.py    # Jupyter аналіз
│
├── 💾 sql_examples/                   # SQL запити
│   ├── 04_sql_examples.sql            # Базові приклади
│   └── 05_advanced_analytics.sql      # Advanced аналітика
│
├── 📊 data/                           # SQL дані
│   ├── init.sql                       # Структура БД
│   └── sample_data.sql                # Тестові дані
│
├── 🛠️ utils/                          # Утиліти
│   ├── helpers.py                     # DB helpers
│   └── __init__.py
│
└── 🐳 Docker                          # Інфраструктура
    ├── docker-compose.yml
    ├── Dockerfile
    └── .env.example
```

---

## 🎓 Навчальна Траєкторія

### Крок 1: Базовий Модуль (обов'язково)
```bash
# 1. Event Loop
python async_examples/01_async_basics.py

# 2. HTTP запити
python async_examples/02_async_http_client.py

# 3. Python + DB
python python_db/05_db_connection.py

# 4. SQL приклади
psql -U admin -d learning_db -f sql_examples/04_sql_examples.sql
```

### Крок 2: Advanced Модулі (опціонально)
```bash
# 1. Production ETL
python advanced_examples/etl/01_async_etl_pipeline.py

# 2. Architectural Patterns
python advanced_examples/patterns/02_repository_pattern.py

# 3. Feature Store
python advanced_examples/ml_pipeline/03_feature_store.py

# 4. Advanced SQL
psql -U admin -d learning_db -f sql_examples/05_advanced_analytics.sql
```

---

## 💻 Технології

### Backend
- Python 3.11+
- PostgreSQL 15
- Docker & Docker Compose

### Libraries
- `asyncio` - асинхронність
- `aiohttp` - async HTTP
- `psycopg2` - PostgreSQL адаптер
- `pandas` - аналіз даних
- `jupyter` - інтерактивний аналіз

### Tools
- Docker для ізоляції
- Git для версіонування
- pytest для тестів (advanced)

---

## 🎯 Для Кого?

### 👨‍🎓 Студенти
- Вивчіть async programming
- Опануйте SQL від basic до advanced
- Зрозумійте як працювати з БД в Python
- Додайте проєкт в portfolio

### 👨‍🏫 Викладачі
- Готовий матеріал на 3-4 години
- Детальний сценарій заняття
- Практичні завдання
- Два рівні складності

### 👨‍💼 Senior DS/DE
- Production patterns
- ML infrastructure
- Advanced SQL аналітика
- Real-world examples

---

## 🔧 Встановлення

### Вимоги
- Docker Desktop
- Python 3.10+
- Git (опціонально)

### Крок за кроком
```bash
# 1. Clone або download проєкт
git clone <repository-url>
cd python_web

# 2. Створити .env
cp .env.example .env

# 3. Запустити PostgreSQL
docker-compose up -d

# 4. Встановити Python залежності
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 5. Перевірити
python async_examples/01_async_basics.py
```

---

## 📊 Статистика

| Метрика | Значення |
|---------|----------|
| Python файлів | 8 |
| SQL файлів | 2 |
| Документації | 11 файлів |
| Рядків коду | ~4100 |
| Patterns | 8+ |
| Таблиць БД | 7 |
| Тестових записів | 100+ |

---

## 🌟 Особливості

### ✨ Базовий Модуль
- Від простого до складного
- Кольоровий вивід
- Real-world дані (e-commerce)
- Jupyter notebooks
- Docker для ізоляції

### 🚀 Advanced Модулі
- Production-ready patterns
- ML infrastructure
- Clean Architecture
- Type safety
- Testable code
- Metrics collection

---

## 🤝 Contribution

Хочете покращити проєкт?

```bash
# 1. Fork проєкт
# 2. Створіть feature branch
git checkout -b feature/amazing-feature

# 3. Commit зміни
git commit -m "Add amazing feature"

# 4. Push
git push origin feature/amazing-feature

# 5. Створіть Pull Request
```

---

## 📝 License

Educational project for GoIT Python Course

---

## 🙏 Подяки

- GoIT Team
- Python Community
- PostgreSQL Contributors

---

## 📧 Контакти

**Питання?** Відкривайте Issues або пишіть викладачу

---

## 🔗 Корисні Посилання

### Документація
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [aiohttp](https://docs.aiohttp.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [psycopg2](https://www.psycopg.org/docs/)

### Практика
- [DataLemur SQL](https://datalemur.com/)
- [LeetCode Database](https://leetcode.com/problemset/database/)
- [SQLZoo](https://sqlzoo.net/)

### Блоги
- [Real Python](https://realpython.com/)
- [Towards Data Science](https://towardsdatascience.com/)

---

**🎉 Готово до навчання!**

**Наступний крок**: Відкрийте [docs/START_HERE.md](docs/START_HERE.md)
