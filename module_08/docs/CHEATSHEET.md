# CHEATSHEET

## Docker
- `docker-compose up -d` — підняти всі сервіси
- `docker-compose down` — зупинити
- `docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB` — термінал psql

## SQLAlchemy
- Створити таблиці: `python sqlalchemy_examples/seed_data.py`
- CRUD демо: `python sqlalchemy_examples/crud.py --demo`
- Отримати всі міста країни: `python sqlalchemy_examples/crud.py --country UA`
- Отримати юзерів за країною: `python sqlalchemy_examples/crud.py --users-in UA`

## MongoDB
- Запустити PyMongo приклад: `python mongodb_examples/01_pymongo_basics.py`
- Асинхронний Motor: `python mongodb_examples/02_motor_async.py`
- Compass підключення: `mongodb://localhost:27017`

## RabbitMQ
- Веб-UI: http://localhost:15672 (guest/guest за замовчуванням)
- Producer: `python messaging_rabbitmq/producer.py`
- Consumer: `python messaging_rabbitmq/consumer.py`

## Cache
- lru_cache демо: `python caching/caching_fibonacci.py`
- Очистити Redis: `docker-compose exec redis redis-cli FLUSHALL`
