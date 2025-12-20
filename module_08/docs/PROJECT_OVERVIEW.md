# PROJECT OVERVIEW

**Мета**: навчити комбінувати SQL/NoSQL, кеші та черги у прикладних DS/DE сценаріях (гео-каталог користувачів).

## Архітектура (логічно)
- **Postgres** — source of truth для користувачів, адрес, міст, країн.
- **SQLAlchemy** — ORM шар для CRUD та вибірок.
- **RabbitMQ** — транспорт подій `user.created`/`user.updated`.
- **MongoDB** — денормалізоване читання (каталоги, агрегації, пошук).
- **Redis / lru_cache** — швидкий кеш для гарячих запитів.

## Потік даних
1. `seed_data.py` створює схему та насіння у Postgres.
2. `producer.py` читає зміну користувача (імітація) і шле подію в RabbitMQ.
3. `consumer.py` забирає подію, робить upsert у Mongo, інвалідирує кеш.
4. Користувачі читають дані з Mongo або кеша (читання дешевше, ніж JOIN-ити Postgres).

## Директории
- `sqlalchemy_examples/` — ORM код, що працює з Postgres.
- `mongodb_examples/` — PyMongo/Motor сценарії.
- `caching/` — приклад кешування (in-process + Redis fallback).
- `messaging_rabbitmq/` — producer/consumer для подій користувачів.
- `docs/` — сценарії, конспекти та advanced поради.

## Коли використовувати
- Pet/PoC: достатньо `lru_cache` + Mongo без черги.
- Малий прод: додаємо RabbitMQ для асинхронних інтеграцій і Redis для кешу.
- Зростання: заміна RabbitMQ на Kafka, Mongo шардинг, Alembic міграції, Prometheus метрики.

## Мінімальні вимоги
- Docker з docker-compose
- Python 3.11+
- 2 CPU / 4 GB RAM для комфортної роботи з усіма сервісами
