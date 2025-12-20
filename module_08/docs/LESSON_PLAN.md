# LESSON PLAN (3–4 години)

## 0. Розігрів (5 хв)
- Пояснити ціль: ORM + NoSQL + черги як «клей» для DS/DE пайплайнів.
- Очікуваний результат: готові скрипти та патерни для продовження.

## 1. SQLAlchemy (70 хв)
- (10 хв) ORM vs SQL: коли обираємо ORM, коли — чистий SQL.
- (20 хв) Розбір моделей `models.py`: типи, Index/Unique, relationship.
- (15 хв) CRUD у `crud.py`: параметризовані запити, sessionmaker, контекст.
- (15 хв) Запити й агрегації: міста по країнах, користувачі з України, soft-delete.
- (10 хв) Мінімізуємо downtime: `create_all` + вступ до Alembic.

## 2. MongoDB (50 хв)
- (10 хв) Atlas/Compass демонстрація, чому документна схема.
- (15 хв) PyMongo CRUD + агрегація `$lookup`/`$group` у `01_pymongo_basics.py`.
- (15 хв) Motor async: паралельні операції, latency заміри.
- (10 хв) Вибір драйвера та схема даних (embedding vs references).

## 3. Cache (20 хв)
- (10 хв) `lru_cache` демо на Fibonacci (CPU-bound) + idea для I/O-bound.
- (10 хв) Redis як зовнішній кеш, TTL стратегія, як не кешувати помилки.

## 4. RabbitMQ (40 хв)
- (10 хв) Трафік подій: user.created → Mongo sink.
- (15 хв) Producer, confirm/persistent delivery, JSON schema.
- (15 хв) Consumer, manual ack, idempotent insert (upsert).

## 5. Q&A / Advanced напрямки (15 хв)
- CDC з Postgres у Mongo (logical decoding/тригери), коли підняти Kafka.
- Sharding/индекси для Mongo, retries/backoff для черг.

## Домашнє завдання
- Додати поле `segments` у Mongo користувачів і оновлювати його через consumer.
- Написати Redis-кеш для результату запиту «усі юзери в країні N» з інвалідейшном при нових подіях.
- Додати тест, що перевіряє ідемпотентність consumer (однакова подія двічі → один запис).
