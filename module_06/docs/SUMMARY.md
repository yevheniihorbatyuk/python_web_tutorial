# 📚 Підсумковий Конспект - Модуль 6

## Реляційні бази даних та Асинхронне програмування

---

## 🎯 Частина 1: Асинхронне Програмування

### 1.1 Основні Концепції

**Event Loop** - це цикл, який керує виконанням асинхронних задач в Python.

**Як це працює**:
```
Синхронний код:
Task 1 (2с) → Task 2 (2с) → Task 3 (2с) = 6с

Асинхронний код:
Task 1 (2с) ┐
Task 2 (2с) ├─ паралельно = 2с
Task 3 (2с) ┘
```

### 1.2 Синтаксис

```python
import asyncio

# Оголошення async функції
async def fetch_data():
    await asyncio.sleep(1)  # await - очікування
    return "data"

# Запуск кількох задач паралельно
async def main():
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data()
    )

# Запуск
asyncio.run(main())
```

**Ключові слова**:
- `async def` - оголошення асинхронної функції
- `await` - очікування завершення async операції
- `asyncio.gather()` - паралельний запуск кількох задач
- `asyncio.sleep()` - async затримка (НЕ блокує)

### 1.3 aiohttp - Асинхронні HTTP запити

```python
import aiohttp

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Паралельні запити
urls = ['http://site1.com', 'http://site2.com', 'http://site3.com']
results = await asyncio.gather(*[fetch_url(url) for url in urls])
```

**Переваги**:
- 5-10x швидше для множинних запитів
- Ефективне використання ресурсів
- Підтримка POST, headers, timeout

### 1.4 Коли використовувати async?

✅ **Добре підходить**:
- I/O операції (HTTP, файли, БД)
- Множинні мережеві запити
- Web scraping
- Real-time додатки

❌ **НЕ підходить**:
- CPU-інтенсивні задачі
- Прості послідовні операції
- Коли код стає складнішим без реальної користі

---

## 💾 Частина 2: SQL та PostgreSQL

### 2.1 Основи SQL

#### SELECT - вибірка даних
```sql
-- Всі дані
SELECT * FROM customers;

-- Конкретні колонки
SELECT first_name, last_name FROM customers;

-- З умовами
SELECT * FROM products WHERE price > 10000;

-- Сортування
SELECT * FROM customers ORDER BY registration_date DESC;

-- Обмеження
SELECT * FROM products LIMIT 10;
```

#### WHERE - фільтрація
```sql
-- Рівність
WHERE city = 'Kyiv'

-- Порівняння
WHERE price > 1000
WHERE age BETWEEN 18 AND 65

-- Список значень
WHERE city IN ('Kyiv', 'Lviv', 'Odesa')

-- Пошук по патерну
WHERE name LIKE '%Phone%'

-- Логічні оператори
WHERE price > 1000 AND is_available = TRUE
```

### 2.2 Агрегатні Функції

```sql
-- Підрахунок
SELECT COUNT(*) FROM customers;

-- Сума
SELECT SUM(total_amount) FROM orders;

-- Середнє
SELECT AVG(price) FROM products;

-- Мінімум/Максимум
SELECT MIN(price), MAX(price) FROM products;

-- GROUP BY - групування
SELECT city, COUNT(*) as customer_count
FROM customers
GROUP BY city;

-- HAVING - фільтрація після GROUP BY
SELECT city, COUNT(*) as count
FROM customers
GROUP BY city
HAVING COUNT(*) > 5;
```

### 2.3 JOIN - Об'єднання Таблиць

```sql
-- INNER JOIN - тільки співпадіння
SELECT c.name, o.total_amount
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id;

-- LEFT JOIN - всі з лівої + співпадіння
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;

-- RIGHT JOIN - всі з правої + співпадіння
-- FULL OUTER JOIN - всі з обох таблиць
```

**Коли що використовувати**:
- **INNER JOIN**: тільки записи що є в обох таблицях
- **LEFT JOIN**: всі з лівої таблиці + співпадіння
- **RIGHT JOIN**: всі з правої таблиці + співпадіння

### 2.4 SUBQUERY - Підзапити

```sql
-- В WHERE
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- В SELECT
SELECT
    name,
    price,
    (SELECT AVG(price) FROM products) AS avg_price
FROM products;

-- В FROM
SELECT category, avg_price
FROM (
    SELECT category_id, AVG(price) AS avg_price
    FROM products
    GROUP BY category_id
) AS category_stats;
```

### 2.5 Window Functions

```sql
-- ROW_NUMBER - нумерація
SELECT
    name,
    price,
    ROW_NUMBER() OVER (ORDER BY price DESC) AS rank
FROM products;

-- PARTITION BY - нумерація в групах
SELECT
    category,
    name,
    price,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rank
FROM products;

-- LAG/LEAD - попередній/наступний рядок
SELECT
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) AS prev_revenue
FROM sales;

-- Накопичувальна сума
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM transactions;
```

---

## 🐍 Частина 3: Python + PostgreSQL

### 3.1 Підключення

```python
import psycopg2

# Базове підключення
conn = psycopg2.connect(
    host="localhost",
    database="learning_db",
    user="admin",
    password="admin123"
)

# Context Manager (рекомендується)
with psycopg2.connect(**config) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM customers")
        # Автоматично закриється
```

### 3.2 CRUD Операції

```python
# CREATE - створення
query = "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id;"
cursor.execute(query, ("John Doe", "john@example.com"))
new_id = cursor.fetchone()[0]

# READ - читання
query = "SELECT * FROM customers WHERE city = %s;"
cursor.execute(query, ("Kyiv",))
rows = cursor.fetchall()

# UPDATE - оновлення
query = "UPDATE customers SET city = %s WHERE id = %s;"
cursor.execute(query, ("Lviv", 1))

# DELETE - видалення
query = "DELETE FROM customers WHERE id = %s;"
cursor.execute(query, (1,))
```

### 3.3 SQL Injection Захист ⚠️

```python
# ❌ НЕБЕЗПЕЧНО - НЕ РОБІТЬ ТАК!
email = user_input
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# ✅ БЕЗПЕЧНО - Параметризовані запити
email = user_input
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))  # Параметри як tuple
```

**Завжди використовуйте `%s` та передавайте параметри окремо!**

### 3.4 Транзакції

```python
try:
    # Початок транзакції
    cursor.execute("UPDATE account SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE account SET balance = balance + 100 WHERE id = 2")

    # Зберегти зміни
    conn.commit()
    print("Транзакція успішна")

except Exception as e:
    # Відкатити зміни при помилці
    conn.rollback()
    print(f"Помилка: {e}")
```

**Коли використовувати транзакції**:
- Операції, які мають виконатись разом
- Фінансові операції
- Критичні зміни даних

### 3.5 Batch Операції

```python
# Вставка багатьох записів
data = [
    ("Product 1", 999.99),
    ("Product 2", 1299.99),
    ("Product 3", 799.99),
]

query = "INSERT INTO products (name, price) VALUES (%s, %s)"
cursor.executemany(query, data)  # Ефективніше ніж цикл
```

### 3.6 RealDictCursor - Результати як словники

```python
from psycopg2.extras import RealDictCursor

with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    cursor.execute("SELECT id, name, email FROM customers")
    rows = cursor.fetchall()
    # rows = [{'id': 1, 'name': 'John', 'email': 'john@...'}]

    for row in rows:
        print(row['name'])  # Доступ по ключу
```

---

## 📊 Частина 4: Аналіз Даних з Pandas

### 4.1 Завантаження даних з PostgreSQL

```python
import pandas as pd
import psycopg2

conn = psycopg2.connect(**config)

# Завантажити дані у DataFrame
df = pd.read_sql_query("SELECT * FROM customers", conn)

# Або через SQLAlchemy (альтернатива)
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/db')
df = pd.read_sql_query("SELECT * FROM customers", engine)
```

### 4.2 Базовий Аналіз

```python
# Перегляд даних
df.head()       # Перші 5 рядків
df.info()       # Інформація про колонки
df.describe()   # Статистика

# Фільтрація
kyiv_customers = df[df['city'] == 'Kyiv']

# Агрегація
df.groupby('city')['id'].count()
df['price'].mean()

# Сортування
df.sort_values('price', ascending=False)
```

### 4.3 RFM Аналіз

**RFM** - модель сегментації клієнтів:
- **R**ecency - як давно купляв
- **F**requency - як часто купляє
- **M**onetary - скільки витрачає

```python
# Розрахувати RFM метрики
rfm = customers.groupby('customer_id').agg({
    'order_date': lambda x: (pd.Timestamp.now() - x.max()).days,  # Recency
    'order_id': 'count',                                          # Frequency
    'total': 'sum'                                                # Monetary
})

# Створити RFM оцінки (1-5)
rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])
rfm['F_score'] = pd.qcut(rfm['frequency'], 5, labels=[1,2,3,4,5])
rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5])

# Сегментація
rfm['segment'] = rfm.apply(segment_customer, axis=1)
```

**Сегменти**:
- **VIP**: високі R, F, M (найкращі клієнти)
- **Loyal**: високі F, M (постійні клієнти)
- **Potential**: високий R (нові клієнти)
- **At Risk**: низький R (давно не купляли)

---

## 🎯 Практичні Паттерни

### Паттерн 1: Connection Pool

```python
from psycopg2 import pool

# Створити пул з'єднань
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **db_config
)

# Використання
conn = connection_pool.getconn()
try:
    cursor = conn.cursor()
    # Робота з БД
finally:
    connection_pool.putconn(conn)
```

### Паттерн 2: Context Manager для БД

```python
from contextlib import contextmanager

@contextmanager
def get_db_cursor(commit=True):
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# Використання
with get_db_cursor() as cursor:
    cursor.execute("SELECT * FROM customers")
```

### Паттерн 3: Async Database Access

```python
import asyncpg  # Більш швидка альтернатива

async def get_customers():
    conn = await asyncpg.connect(**config)
    rows = await conn.fetch('SELECT * FROM customers')
    await conn.close()
    return rows
```

---

## ⚡ Оптимізація

### SQL Оптимізація

```sql
-- Використовуйте індекси
CREATE INDEX idx_customer_email ON customers(email);

-- EXPLAIN для аналізу запиту
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1;

-- Уникайте SELECT *
SELECT id, name FROM products;  -- Краще

-- Використовуйте LIMIT
SELECT * FROM products LIMIT 100;

-- JOIN тільки необхідні таблиці
```

### Python Оптимізація

```python
# Використовуйте executemany() для batch операцій
cursor.executemany(query, data)  # Швидше

# Використовуйте connection pool
# Закривайте з'єднання
# Використовуйте індекси в БД
```

---

## 🔑 Ключові Висновки

### Асинхронне програмування
1. ✅ async/await для I/O операцій
2. ✅ aiohttp для HTTP запитів
3. ✅ Прискорення в 5-10x для паралельних операцій
4. ✅ Event Loop керує виконанням задач

### SQL
1. ✅ SELECT для вибірки, WHERE для фільтрації
2. ✅ JOIN для об'єднання таблиць
3. ✅ GROUP BY для агрегації
4. ✅ Window Functions для аналітики

### Python + PostgreSQL
1. ✅ psycopg2 для підключення
2. ✅ ЗАВЖДИ параметризовані запити (%s)
3. ✅ Context managers для автоматичного закриття
4. ✅ Транзакції для критичних операцій

### Аналіз даних
1. ✅ pandas + PostgreSQL = потужний аналіз
2. ✅ RFM для сегментації клієнтів
3. ✅ DataFrame для зручної роботи з даними

---

## 📖 Чек-лист Знань

Перевірте себе:

**Асинхронне програмування**:
- [ ] Розумію як працює Event Loop
- [ ] Можу написати async функцію
- [ ] Знаю різницю між asyncio.sleep() і time.sleep()
- [ ] Можу використати aiohttp для HTTP запитів
- [ ] Розумію коли використовувати async

**SQL**:
- [ ] Можу написати SELECT з WHERE та ORDER BY
- [ ] Знаю різницю між INNER JOIN та LEFT JOIN
- [ ] Можу використати GROUP BY та HAVING
- [ ] Розумію що таке SUBQUERY
- [ ] Знаю як працюють Window Functions

**Python + PostgreSQL**:
- [ ] Можу підключитись до PostgreSQL
- [ ] Можу виконати CRUD операції
- [ ] Розумію SQL Injection і як його уникнути
- [ ] Знаю що таке транзакції
- [ ] Можу використати pandas для аналізу даних

---

**Вітаю! Тепер ви знаєте основи асинхронного програмування та роботи з PostgreSQL! 🎉**
