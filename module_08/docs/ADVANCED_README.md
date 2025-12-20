# ADVANCED (для Senior DS/DE)

## 1) Event-driven ingestion
- Producer шле події `user.created`/`user.updated` в RabbitMQ.
- Consumer:
  - Читає подію, перевіряє версію (timestamp/sequence).
  - Upsert у Mongo (`external_id` як ключ) → гарантує ідемпотентність.
  - Кешує результат у Redis з TTL 10–60 cек (наприклад, список міст по країні).
- Backpressure: prefetch=10, retry з exponential backoff.

## 2) CDC з Postgres у Mongo без Debezium
- Легкий варіант: тригери в Postgres записують у таблицю `outbox_events`.
- Скрипт-воркер читає outbox та пушить у RabbitMQ → Mongo consumer.
- Перевага: узгодженість транзакцій без окремого брокера змін (підходить для навчальних проектів).

## 3) Інфраструктура для індексів і TTL
- Postgres: індекси по `country.iso_code`, `user.email` (Unique), `address.city_id`.
- Mongo: індекси по `country_code`, `city`, `external_id`; TTL index для тимчасових кешів/подій.
- Розбийте колекції: `users`, `events`, `aggregates` (precomputed).

## 4) Кеш-стратегія
- CPU-bound: `lru_cache` (in-process) з невеликим `maxsize` для гарячих значень.
- I/O-bound: Redis з TTL; інвалідейшн при подіях `user.updated`.
- Observability: логувати cache hit/miss, метрики часу відповіді (Prometheus/Grafana).

## 5) Тестування
- Unit: `caching_fibonacci` (hit/miss), CRUD з sqlite in-memory для ORM.
- Integration: docker-compose up, потім producer/consumer проганяє 5–10 подій.
- Chaos: затримки в Mongo/RabbitMQ, перевірити retry/backoff.

## 6) Референси
- SQLAlchemy 2.0 ORM docs: Declarative with Annotated Table Mapping.
- MongoDB Aggregation Pipeline
- RabbitMQ Tutorials (publisher confirms, manual ack)
- Redis cache design patterns (cache-aside)
