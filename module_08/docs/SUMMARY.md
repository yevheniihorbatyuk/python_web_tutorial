# SUMMARY

- SQLAlchemy 2.0 Core/ORM — один код для Postgres із strong typing та relationships.
- Моделі Country → City → Address → User: каскадні зв'язки, soft-delete прапорець.
- CRUD і запити: вибрати всі міста країни; вибрати всіх користувачів з конкретної країни.
- MongoDB: PyMongo для sync скриптів, Motor для async сервісів; агрегації `$match`, `$group`, `$lookup`.
- Atlas/Compass — швидкий UI для перевірки схем та індексів.
- Кешування: `functools.lru_cache` для CPU-bound; Redis для шардингу кеша між сервісами.
- RabbitMQ: producer відправляє події `user.created`, consumer зберігає в Mongo з manual ack.
- Ідемпотентність consumer: upsert по `external_id`, щоб дублікати не ламали дані.

**Next steps:** підняти Alembic, додати Prometheus метрики, зробити CDC з Postgres у Mongo через чергу.
