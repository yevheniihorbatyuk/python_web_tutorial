# 🚀 ПОЧНІТЬ ТУТ

Модуль 8: SQLAlchemy ORM + NoSQL (MongoDB), кешування та черги RabbitMQ.

## ⚡ 5-хвилинний старт
1. `cp .env.example .env`
2. Запустіть інфраструктуру (можна локально або через Docker):
   ```bash
   docker-compose up -d
   ```
3. Встановіть залежності: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
4. Створіть схему Postgres і тестові дані: `python sqlalchemy_examples/seed_data.py`
5. Запустіть швидкі демо:
   ```bash
   python sqlalchemy_examples/crud.py --demo
   python mongodb_examples/01_pymongo_basics.py
   python caching/caching_fibonacci.py
   ```

## Що читати далі
- `README.md` — огляд модуля та структура.
- `docs/QUICKSTART.md` — докладні команди запуску.
- `docs/LESSON_PLAN.md` — сценарій заняття на 3–4 години.
- `docs/ADVANCED_README.md` — продвинуті завдання для Senior DS/DE.

## Результат після модуля
- ORM-моделі та запити через SQLAlchemy 2.0.
- CRUD та аналітика в MongoDB (PyMongo + Motor).
- Кешування (lru_cache/Redis) для дорогих функцій.
- Event-driven потік: RabbitMQ producer → consumer → Mongo.

Якщо інфраструктура не потрібна, запустіть скрипти з localhost (див. змінні у `.env`).
