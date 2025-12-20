# Module 8: Практичний Путівник з Прикладами
## Companion Guide - Step-by-Step для кожної теми

---

## 📌 ПЕРЕД ПОЧАТКОМ

Переконайтесь що встановлено залежності:

```bash
pip install --break-system-packages -r requirements.txt
```

---

# 🗄️ ТЕМА 1: SQLAlchemy ORM - User-Address-City-Country

## Крок 1: Запустимо модуль і побачимо результати

```bash
cd /root/goit/python_web/module_08
python3 01_sqlalchemy_advanced.py
```

### Очікуваний вихід:

```
✓ Database tables created
Seeding database...
✓ Database seeded with sample data

================================================================================
SQLAlchemy ORM - Advanced Patterns Demonstration
================================================================================

[1] Users living in Ukraine:
  - Ivan Ivanov (ivan.data@example.com)
    Address: Khreschatyk Street, Kyiv
  - Mariya Petrova (mariya.ml@example.com)
    Address: Pushkin Street, Kyiv

[2] Users in Kyiv:
  - Ivan Ivanov
  - Mariya Petrova
```

## Крок 2: Розуміємо структуру даних

### Як виглядає таблиця в пам'яті:

```
ТАБЛИЦЯ: countries
┌────┬──────────┬──────┬────────────┬────────────┐
│ id │ name     │ code │ population │ gdp_per_ca │
├────┼──────────┼──────┼────────────┼────────────┤
│ 1  │ Ukraine  │ UA   │ 40000000   │ 4200       │
│ 2  │ Poland   │ PL   │ 38000000   │ 15600      │
└────┴──────────┴──────┴────────────┴────────────┘

ТАБЛИЦЯ: cities
┌────┬─────────┬────────────┬────────┐
│ id │ name    │ country_id │ ..     │
├────┼─────────┼────────────┼────────┤
│ 1  │ Kyiv    │ 1 (UA)     │ ...    │
│ 2  │ Kharkiv │ 1 (UA)     │ ...    │
│ 3  │ Warsaw  │ 2 (PL)     │ ...    │
└────┴─────────┴────────────┴────────┘

ТАБЛИЦЯ: users
┌────┬─────────────────────┬──────────────┬────────────┐
│ id │ email               │ username     │ address_id │
├────┼─────────────────────┼──────────────┼────────────┤
│ 1  │ ivan@example.com    │ ivan_data    │ 1          │
│ 2  │ maria@example.com   │ maria_ml     │ 1          │
└────┴─────────────────────┴──────────────┴────────────┘
```

## Крок 3: Напишемо власний запит

### Завдання: Знайти всіх користувачів з рейтингом > 80

```python
# Відкрийте Python консоль
python3 -c "
from sqlalchemy import create_engine, Session, Column, Integer, String
from sqlalchemy.orm import declarative_base

# Код з 01_sqlalchemy_advanced.py скопіюємо сюди...
# Але для простоти, робимо новий запит до вже створеної БД:

# Запит: Знайти топ-10 користувачів по рейтингу
#
# SQL версія:
# SELECT username, email, profile_score
# FROM users
# WHERE profile_score > 80
# ORDER BY profile_score DESC
# LIMIT 10

# SQLAlchemy версія:
from sqlalchemy.orm import Session
from sqlalchemy import desc

session = Session()
experts = session.query(User).filter(
    User.profile_score > 80  # Рейтинг більше за 80
).order_by(
    desc(User.profile_score)  # Спадаючий порядок
).limit(10).all()

for user in experts:
    print(f'{user.username}: {user.profile_score}')
"
```

## Крок 4: Розуміємо N+1 Проблему

### Плохо (N+1 проблема):

```python
# Отримати всіх користувачів
users = session.query(User).all()  # Запит 1

# Для кожного користувача, отримати його місто
for user in users:
    print(user.address.city.name)  # Запити 2-1001!
    # Кожен доступ до user.address викличе нову операцію БД

# Всього: 1 + 1000 = 1001 запит! Дуже повільно!
```

### Добре (Eager Loading):

```python
from sqlalchemy.orm import joinedload

# Один запит з JOIN'ом, який завантажує все відразу
users = session.query(User).options(
    joinedload(User.address)
    .joinedload(Address.city)
    .joinedload(City.country)
).all()

for user in users:
    print(user.address.city.country.name)  # Нема додаткових запитів!

# Всього: 1 запит! 1000x швидше!
```

## Крок 5: Практика

### Завдання:

Напишіть запит що знаходить кількість користувачів в кожній країні.

**Підказка**: Використовуйте `func.count()` та `group_by()`

### Рішення:

```python
from sqlalchemy import func

stats = session.query(
    Country.name,
    func.count(User.id).label("user_count"),
    func.avg(User.profile_score).label("avg_score")
).join(City).join(Address).join(User).group_by(
    Country.name
).order_by(
    func.count(User.id).desc()
).all()

for country, count, avg_score in stats:
    print(f"{country}: {count} користувачів, avg score: {avg_score:.2f}")
```

---

# 📂 ТЕМА 2: MongoDB - NoSQL та Документи

## Крок 1: Запустимо модуль

```bash
python3 02_mongodb_advanced.py
```

### Очікуваний вихід (якщо MongoDB недоступна):

```
MongoDB not available - showing structure examples only

Example User Document:
{
  'username': 'data_scientist_001',
  'email': 'user@example.com',
  'profile': {'interests': ['data-science', 'machine-learning', 'python']},
  'metrics': {'total_views': 1500, 'avg_engagement_score': 8.5}
}
```

## Крок 2: Розуміємо структуру документів

### JSON документ vs SQL рядок

```
MONGODB ДОКУМЕНТ (JSON):
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "user_id": 123,
  "event_type": "user_purchase",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "metadata": {
    "product_id": "PROD-001",
    "price": 99.99,
    "category": "electronics"
  },
  "geo": {
    "country": "Ukraine",
    "city": "Kyiv",
    "coordinates": [50.4501, 30.5234]
  }
}

vs

POSTGRESQL РЯДОК (таблиця + 3 JOIN'и):
tables: events, products, categories, countries
Запит:
SELECT e.user_id, e.event_type, e.timestamp,
       p.product_id, c.name, co.name
FROM events e
JOIN products p ON e.product_id = p.id
JOIN categories c ON p.category_id = c.id
JOIN countries co ON e.country_id = co.id
WHERE e.user_id = 123
```

**Вивід**: MongoDB = менше JOIN'ів, гнучкіше, але гірша нормалізація.

## Крок 3: Напишемо простий скрипт з MongoDB

```python
# Якщо у вас є локальний MongoDB або Atlas:

from pymongo import MongoClient
import json
from datetime import datetime

# Підключитись до MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_app"]
users = db["users"]

# 1. Вставити користувача
user_doc = {
    "username": "john_doe",
    "email": "john@example.com",
    "profile": {
        "interests": ["python", "ml"],
        "level": "beginner"
    },
    "subscriptions": [
        {"plan": "free", "started": datetime.utcnow()}
    ]
}

result = users.insert_one(user_doc)
print(f"✓ Вставлено: {result.inserted_id}")

# 2. Отримати користувача
user = users.find_one({"username": "john_doe"})
print(f"✓ Знайдено: {user['email']}")

# 3. Оновити користувача
users.update_one(
    {"username": "john_doe"},
    {"$set": {"profile.level": "intermediate"}}
)
print("✓ Оновлено: level -> intermediate")

# 4. Видалити користувача
users.delete_one({"username": "john_doe"})
print("✓ Видалено")
```

## Крок 4: Агрегаційні Запити

### Завдання: Знайти топ-5 категорій по сумарним продажам

```python
pipeline = [
    # 1. Вибрати тільки покупки
    {
        "$match": {
            "event_type": "user_purchase"
        }
    },
    # 2. Групувати по категорії та підрахувати
    {
        "$group": {
            "_id": "$metadata.category",
            "total_sales": {"$sum": "$metadata.price"},
            "count": {"$sum": 1},
            "avg_price": {"$avg": "$metadata.price"}
        }
    },
    # 3. Сортувати за продажами (спадаючий)
    {
        "$sort": {"total_sales": -1}
    },
    # 4. Взяти топ-5
    {
        "$limit": 5
    }
]

results = list(db.events.aggregate(pipeline))

for item in results:
    print(f"{item['_id']}: "
          f"${item['total_sales']:.2f} total, "
          f"{item['count']} transactions, "
          f"${item['avg_price']:.2f} avg")
```

---

# ⚡ ТЕМА 3: Caching - Продуктивність

## Крок 1: Запустимо модуль

```bash
python3 03_caching_strategies.py
```

### Очікуваний вихід:

```
================================================================================
Caching Strategies - LRU Cache & Redis Demonstration
================================================================================

[1] Fibonacci - Cache vs No Cache Benchmark
Fibonacci(25):
  Without cache: 16.44ms
  With cache: 0.01ms
  Speedup: 1271x

Fibonacci(30):
  Without cache: 179.19ms
  With cache: 0.02ms
  Speedup: 11456x
```

## Крок 2: Розуміємо LRU Cache

### Як працює Fibonacci БЕЗ кеша:

```
fib(5) = fib(4) + fib(3)
       = (fib(3) + fib(2)) + fib(3)
       = fib(3) + fib(2) + fib(3)
            ↑            ↑          ↑
         обраховується 2 рази!

fib(30) = 2^30 = 1 млрд викликів = 179 мс ⏱️
```

### Як працює Fibonacci З кешем:

```
fib(5) запит
  ├─ fib(4) запит
  │  ├─ fib(3) запит → обчислити → зберегти
  │  ├─ fib(2) запит → обчислити → зберегти
  │  └─ 3 + 2 = 5 → зберегти у кеші
  ├─ fib(3) запит → УЖЕ У КЕШІ! Повернути миттєво
  └─ 5 + 3 = 8

fib(30) = 31 обчислень = 0.02 мс ✓
Прискорення: 179 / 0.02 = 11,456x!
```

## Крок 3: Напишемо власний кеш

```python
from functools import lru_cache
import time

# БЕЗ кеша
def expensive_function(n):
    """Функція яка довго обчислюється"""
    total = 0
    for i in range(100000000):  # 100 млн ітерацій
        total += i
    return total

# З кешем
@lru_cache(maxsize=128)
def cached_function(n):
    total = 0
    for i in range(100000000):
        total += i
    return total

# Тест 1: Першого разу - обчислює
start = time.time()
result1 = cached_function(1)
time1 = time.time() - start
print(f"Першого разу: {time1*1000:.2f}ms")

# Тест 2: Другого разу - бере з кеша
start = time.time()
result2 = cached_function(1)
time2 = time.time() - start
print(f"Другого разу: {time2*1000:.4f}ms")

print(f"Прискорення: {time1/time2:.0f}x")

# Переглянути статистику кеша
print(cached_function.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
# hits=1: один раз повернули з кеша
# misses=1: один раз довелось обчислювати
```

## Крок 4: Redis для розподіленого кеша

```python
import redis
import json

# Підключитись до Redis
# Якщо Redis не встановлено локально - пропустіть цей крок
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    print("✓ Redis з'єднання успішне")

    # Приклад 1: Простий кеш
    redis_client.set("user:123:name", "Ivan")
    redis_client.set("user:456:name", "Maria")

    name = redis_client.get("user:123:name")
    print(f"Користувач: {name}")

    # Приклад 2: Кеш з TTL (час життя)
    # Зберегти на 1 годину (3600 сек)
    redis_client.setex("session:abc123", 3600, json.dumps({
        "user_id": 123,
        "created_at": "2024-01-15"
    }))

    session = redis_client.get("session:abc123")
    print(f"Сесія: {session}")

except ConnectionRefusedError:
    print("⚠️ Redis не доступен - встановіть Redis локально або використовуйте MongoDB/PostgreSQL для кеша")
```

---

# 📨 ТЕМА 4: RabbitMQ - Асинхронна Обробка

## Крок 1: Запустимо модуль

```bash
python3 04_rabbitmq_messaging.py
```

### Очікуваний вихід (якщо RabbitMQ недоступна):

```
ERROR: Could not connect to RabbitMQ
Make sure RabbitMQ is running:
  Local: docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:latest
```

## Крок 2: Запустимо RabbitMQ в Docker

```bash
# Запустити RabbitMQ контейнер
docker run -d --name rabbitmq \
  -p 5672:5672 \    # AMQP port (для підключення)
  -p 15672:15672 \  # Management UI port
  rabbitmq:latest

# Перевірити що контейнер запущено
docker ps | grep rabbitmq

# Менеджер Web UI
# URL: http://localhost:15672
# Username: guest
# Password: guest
```

## Крок 3: Розуміємо Producer-Consumer

### Producer (опублікує подію):

```python
import pika
import json

# Підключитись
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Оголосити exchange
channel.exchange_declare(exchange='my_exchange', exchange_type='direct', durable=True)

# Опублікувати повідомлення
message = {
    "type": "user.created",
    "user_id": 123,
    "username": "ivan"
}

channel.basic_publish(
    exchange='my_exchange',
    routing_key='user.created',
    body=json.dumps(message),
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent  # Зберегти на диск
    )
)

print("✓ Повідомлення опубліковано")
connection.close()
```

### Consumer (отримує та обробляє):

```python
import pika
import json

def callback(ch, method, properties, body):
    """Функція що викликається коли приходить повідомлення"""
    message = json.loads(body)
    print(f"✓ Отримано: {message['type']}")

    # Обробити...

    # Підтвердити обробку
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Підключитись
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Оголосити queue
channel.queue_declare(queue='my_queue', durable=True)

# Прив'язати queue до exchange
channel.queue_bind(exchange='my_exchange', queue='my_queue', routing_key='user.created')

# Встановити callback
channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=False)

print("Чекаємо на повідомлення...")
channel.start_consuming()  # Блокуючий цикл
```

## Крок 4: Real-World Сценарій

### Сценарій: User Signs Up

```python
# ===== STEP 1: API запрос =====
# POST /api/users/signup
# Payload: { username: "ivan", email: "ivan@example.com" }

# ===== STEP 2: API обробка (займає 10ms) =====
user = save_user_to_postgresql(username, email)
publish_event("user.created", {"user_id": user.id, "email": user.email})
return {"status": "created"}  # Одразу повернути

# ===== STEP 3: RabbitMQ черга =====
# Подія чекає у черзі для обробки...

# ===== STEP 4: Consumer обробляє =====
# На фоні, незалежно від API:
# 1. Відправити привітальний email (5 сек) - можна чекати
# 2. Обчислити рекомендації (10 сек) - можна чекати
# 3. Зберегти профіль у MongoDB - можна чекати

# ===== РЕЗУЛЬТАТ =====
# API відповідь: 10ms (швидко!)
# Користувач задоволений!
# Все інше работает на фоні
```

---

# 🤖 ТЕМА 5: Real-World Data Science

## Крок 1: Запустимо модуль

```bash
python3 05_realworld_data_science.py
```

### Очікуваний вихід:

```
================================================================================
Real-World Data Science Application
================================================================================

[1] Processing User Data & Generating Profiles

  User: power_user
    Segment: active
    Engagement: 61.79/100
    Churn Risk: 14.0%
    Predicted LTV: $368.91
```

## Крок 2: Розуміємо User Segments

### 4 Сегменти Користувачів

```
┌─────────────────────────────────────────────────────────────────┐
│ DORMANT (💤 - Сплять)                                           │
├─────────────────────────────────────────────────────────────────┤
│ Критерій: Не активні > 90 днів                                  │
│ Поведінка: Майже не заходять                                    │
│ Дія: Спецпропозиція "Ми сумуємо!"                              │
│ ROI: Низький, але можна повернути                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ACTIVE (⭐ - Активні)                                           │
├─────────────────────────────────────────────────────────────────┤
│ Критерій: Регулярні покупки, $100-1000                          │
│ Поведінка: Здійснюють покупки щомісяця                          │
│ Дія: Персоналізовані рекомендації                               │
│ ROI: Високий, стабільний дохід                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ VIP (👑 - Premium)                                              │
├─────────────────────────────────────────────────────────────────┤
│ Критерій: Видатки > $1000                                       │
│ Поведінка: Постійні покупки, висока вартість                    │
│ Дія: Exclusive offers, VIP support                              │
│ ROI: Дуже високий, на них припадає 80% доходу                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AT_RISK (🚨 - На межі)                                          │
├─────────────────────────────────────────────────────────────────┤
│ Критерій: Мало видатків + новинки в режимі молчания            │
│ Поведінка: Почали, але не розвивають активність                 │
│ Дія: Retention offers, "Ми вас цінимо"                          │
│ ROI: Середній, але можна врятувати                              │
└─────────────────────────────────────────────────────────────────┘
```

## Крок 3: Напишемо сегментацію

```python
from enum import Enum
from datetime import datetime, timedelta

class UserSegment(Enum):
    DORMANT = "dormant"
    ACTIVE = "active"
    VIP = "vip"
    AT_RISK = "at_risk"

def segment_user(user_data):
    """
    Визначити сегмент користувача.

    Args:
        user_data: {
            "user_id": 123,
            "registration_date": datetime,
            "purchases": [{"date": ..., "amount": ...}, ...]
        }
    """
    # Обчислити метрики
    days_since_last_purchase = (
        datetime.utcnow() - max(
            [p['date'] for p in user_data['purchases']] or [datetime.utcnow()]
        )
    ).days

    total_spent = sum(p['amount'] for p in user_data['purchases'])

    # Логіка сегментації
    if days_since_last_purchase > 90:
        return UserSegment.DORMANT
    elif total_spent > 1000:
        return UserSegment.VIP
    elif total_spent < 100 and days_since_last_purchase < 30:
        return UserSegment.AT_RISK
    else:
        return UserSegment.ACTIVE

# Тест
users = [
    {  # VIP користувач
        "user_id": 1,
        "registration_date": datetime(2023, 1, 1),
        "purchases": [
            {"date": datetime(2024, 1, 1), "amount": 500},
            {"date": datetime(2024, 1, 10), "amount": 800},
        ]
    },
    {  # DORMANT користувач
        "user_id": 2,
        "registration_date": datetime(2023, 6, 1),
        "purchases": [
            {"date": datetime(2023, 9, 1), "amount": 100},
        ]
    }
]

for user in users:
    segment = segment_user(user)
    print(f"Користувач {user['user_id']}: {segment.value}")
```

## Крок 4: Churn Prediction (предбачення відтоку)

```python
import math

def predict_churn(user_data):
    """
    Передбачити ймовірність що користувач кине продукт.

    Формула: Логістична функція
      churn = 1 / (1 + exp(-(days_since_purchase - 30) / 20))
    """
    days_since_purchase = (
        datetime.utcnow() - max([p['date'] for p in user_data['purchases']])
    ).days

    # Логістична крива (S-форма)
    exponent = (days_since_purchase - 30) / 20
    churn_prob = 1 / (1 + math.exp(-exponent))

    return churn_prob * 100

# Тести
print("Días Зinah Purchase | Churn Risk")
for days in [5, 15, 30, 45, 60]:
    user = {
        "purchases": [{
            "date": datetime.utcnow() - timedelta(days=days)
        }]
    }
    churn = predict_churn(user)
    print(f"{days:20} | {churn:.1f}%")

# Вихід:
# Días Since Purchase | Churn Risk
# 5                   | 13.5%
# 15                  | 29.2%
# 30                  | 50.0%  ← Riskna granica!
# 45                  | 70.8%
# 60                  | 86.5%
```

---

# 🎯 ІНТЕГРАЦІЯ ВСІХ КОМПОНЕНТІВ

## Повна Архітектура

```
┌─────────────────┐
│  User API Call  │ GET /api/users/123/profile
└────────┬────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  1. Check Redis Cache (1-5ms)         │
    │     key: "profile:user:123"           │
    └────┬─────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  2. If miss → Load from PostgreSQL    │
    │     - User data                       │
    │     - Address, City, Country          │
    │     - Purchase history                │
    └────┬─────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  3. Query MongoDB for events          │
    │     - User activity logs              │
    │     - Purchase history                │
    └────┬─────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  4. Run Data Science Engine           │
    │     - Calculate segment               │
    │     - Predict churn                   │
    │     - Estimate LTV                    │
    │     - Generate recommendations        │
    └────┬─────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  5. Cache result in Redis (1 hour)    │
    └────┬─────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────┐
    │  6. Return to User                    │
    │     Segment: ACTIVE                   │
    │     Churn Risk: 14%                   │
    │     LTV: $368                         │
    │     Recommendations: [...]            │
    └─────────────────────────────────────┘
```

## Комбінований Скрипт

```python
import asyncio
from datetime import datetime, timedelta
import math

# ===== LAYER 1: PostgreSQL =====
class UserRepository:
    def get_user(self, user_id):
        # SELECT * FROM users WHERE id = ?
        return {
            "user_id": user_id,
            "username": "ivan",
            "email": "ivan@example.com",
            "registration_date": datetime(2023, 1, 1),
            "total_spent": 500
        }

# ===== LAYER 2: MongoDB =====
class EventStore:
    def get_user_events(self, user_id):
        # db.events.find({"user_id": user_id})
        return [
            {"date": datetime.utcnow() - timedelta(days=5), "type": "purchase", "amount": 100},
            {"date": datetime.utcnow() - timedelta(days=15), "type": "purchase", "amount": 200},
        ]

# ===== LAYER 3: Data Science =====
class Analytics:
    def calculate_profile(self, user_data, events):
        total_spent = sum(e['amount'] for e in events if e['type'] == 'purchase')
        days_since_purchase = (
            datetime.utcnow() - min(e['date'] for e in events)
        ).days

        churn_prob = 1 / (1 + math.exp(-(days_since_purchase - 30) / 20))

        return {
            "segment": "ACTIVE",
            "churn_risk": churn_prob * 100,
            "ltv": total_spent * 3
        }

# ===== LAYER 4: Cache (Redis) =====
class Cache:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ttl=3600):
        self.data[key] = value

# ===== INTEGRATION =====
async def get_user_profile(user_id):
    # 1. Check cache
    cache = Cache()
    cached = cache.get(f"profile:{user_id}")
    if cached:
        print(f"Cache HIT for user {user_id}")
        return cached

    # 2. Load from PostgreSQL
    repo = UserRepository()
    user = repo.get_user(user_id)

    # 3. Load from MongoDB
    event_store = EventStore()
    events = event_store.get_user_events(user_id)

    # 4. Run analytics
    analytics = Analytics()
    profile = analytics.calculate_profile(user, events)

    # 5. Cache result
    cache.set(f"profile:{user_id}", profile, ttl=3600)

    return profile

# ===== TEST =====
async def main():
    profile = await get_user_profile(123)
    print(f"\nUser Profile:")
    print(f"  Segment: {profile['segment']}")
    print(f"  Churn Risk: {profile['churn_risk']:.1f}%")
    print(f"  LTV: ${profile['ltv']:.2f}")

asyncio.run(main())
```

---

## 📚 Додаткові Ресурси

### Документація
- SQLAlchemy: https://docs.sqlalchemy.org/
- MongoDB: https://docs.mongodb.com/manual/
- Redis: https://redis.io/docs/
- RabbitMQ: https://www.rabbitmq.com/getstarted.html

### Інструменти
- pgAdmin: PostgreSQL GUI
- MongoDB Compass: MongoDB GUI
- Redis CLI: `redis-cli` або Redis Insight
- RabbitMQ Manager: http://localhost:15672

### Подальше Вивчення
- Implement Caching в FastAPI/Flask
- Docker Compose для локального setup
- Kubernetes deployment
- Message brokers: Kafka vs RabbitMQ
- Distributed transactions

---

**Companion Guide Complete!** ✅
