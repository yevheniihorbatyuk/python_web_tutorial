# 🧭 Python Web - Модуль 8: SQLAlchemy, NoSQL, Cache, RabbitMQ

**Фокус**: ORM з SQLAlchemy 2.0, документні БД (MongoDB), кешування (lru_cache/Redis) та черги RabbitMQ з прикладними кейсами для DS/DE.

---

## 🚀 Швидкий старт

```bash
cd module_08
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Підняти інфраструктуру
# docker-compose up -d

# 1) Створити схему Postgres через SQLAlchemy
python sqlalchemy_examples/seed_data.py

# 2) CRUD і запити
python sqlalchemy_examples/crud.py --demo

# 3) MongoDB приклад (PyMongo)
python mongodb_examples/01_pymongo_basics.py

# 4) Асинхронний Mongo (Motor)
python mongodb_examples/02_motor_async.py

# 5) Кешування Fibonacci
python caching/caching_fibonacci.py

# 6) RabbitMQ producer/consumer
python messaging_rabbitmq/producer.py &
python messaging_rabbitmq/consumer.py
```

Деталі та сценарій: `docs/START_HERE.md` → `docs/README.md` → `docs/ADVANCED_README.md`.

---

## 🎯 Два рівні

### Базовий (2.5–3 години)
- SQLAlchemy 2.0 ORM: моделі User → Address → City → Country, CRUD, фільтрація.
- MongoDB 101: Atlas/Compass, PyMongo CRUD та агрегації для гео-запитів.
- lru_cache та Redis як кеш над «дорогими» запитами.
- RabbitMQ: базовий producer/consumer, гарантія доставки, підтвердження.

### Advanced (для Senior DS/DE, +2 години)
- Event-driven data ingestion: черга → async consumer → Mongo/Redis fan-out.
- Lean ETL: CDC з Postgres у Mongo (change table capture без Debezium).
- Продуктивність: індекси в Mongo, sharding-підготовка, idempotent споживач.
- Спостережуваність: structured logging + метрики часу відповіді кеша.

---

## 📁 Структура

```
module_08/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── Dockerfile
├── docs/
│   ├── START_HERE.md
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── LESSON_PLAN.md
│   ├── SUMMARY.md
│   ├── ADVANCED_README.md
│   ├── PROJECT_OVERVIEW.md
│   └── CHEATSHEET.md
│
├── sqlalchemy_examples/
│   ├── database.py
│   ├── models.py
│   ├── crud.py
│   └── seed_data.py
│
├── mongodb_examples/
│   ├── 01_pymongo_basics.py
│   └── 02_motor_async.py
│
├── caching/
│   └── caching_fibonacci.py
│
└── messaging_rabbitmq/
    ├── producer.py
    └── consumer.py
```

---

## 🛠 Технології
- Python 3.11+
- SQLAlchemy 2.0, PostgreSQL
- MongoDB (PyMongo + Motor)
- RabbitMQ (pika)
- Redis / functools.lru_cache

---

## 🧭 Навчальна траєкторія
1. Пройти `docs/START_HERE.md` і підняти інфраструктуру.
2. Розібрати ORM-моделі та CRUD (`sqlalchemy_examples/`).
3. Перейти до Mongo прикладів: порівняти embedding vs references.
4. Додати кешування повільних запитів.
5. Запустити producer/consumer й зберегти події у Mongo.
6. Опціонально: виконати advanced завдання з `docs/ADVANCED_README.md`.

---

Кодові приклади збалансовані між простотою та production-практиками, щоб їх можна було «витягнути» у реальні DS/DE пайплайни.
