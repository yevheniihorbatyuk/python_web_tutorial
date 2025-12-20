# ⚡ QUICKSTART

## 1. Підготовка середовища
```bash
cd module_08
cp .env.example .env
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## 2. Запуск інфраструктури (Docker)
```bash
docker-compose up -d
# Перевірити сервіси
docker-compose ps
docker-compose logs -f postgres  # опціонально
```

## 3. PostgreSQL + SQLAlchemy
```bash
# Створити таблиці та дані
python sqlalchemy_examples/seed_data.py
# CRUD + вибірки (users в Україні, всі міста країни)
python sqlalchemy_examples/crud.py --demo
```

## 4. MongoDB
```bash
# Синхронний PyMongo
python mongodb_examples/01_pymongo_basics.py
# Асинхронний Motor (демо агрегації та latency порівняння)
python mongodb_examples/02_motor_async.py
```

## 5. Кешування
```bash
python caching/caching_fibonacci.py
```

## 6. RabbitMQ
```bash
# Запустити producer (створює повідомлення user.create)
python messaging_rabbitmq/producer.py
# В іншому терміналі — consumer, що пише у Mongo
python messaging_rabbitmq/consumer.py
```

## 7. Зупинка
```bash
docker-compose down
```

Далі переходьте до `docs/README.md` (план уроку) та `docs/ADVANCED_README.md` (production-патерни).
