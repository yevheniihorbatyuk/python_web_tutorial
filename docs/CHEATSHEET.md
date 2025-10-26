# ⚡ Швидкий Довідник Команд

## 🚀 Запуск Проєкту

```bash
# 1. Створити .env файл
cp .env.example .env

# 2. Запустити PostgreSQL
docker-compose up -d

# 3. Перевірити статус
docker-compose ps

# 4. Переглянути логи
docker-compose logs -f postgres
```

---

## 🐳 Docker Команди

### Основні
```bash
# Запустити (мінімальний: тільки PostgreSQL)
docker-compose up -d

# Запустити (повний: PostgreSQL + pgAdmin + Redis)
docker-compose --profile full up -d

# Зупинити
docker-compose down

# Зупинити + видалити дані
docker-compose down -v

# Перезапустити
docker-compose restart postgres

# Статус
docker-compose ps
```

### Логи
```bash
# Всі логи
docker-compose logs

# Логи PostgreSQL
docker-compose logs -f postgres

# Останні 100 рядків
docker-compose logs --tail=100 postgres
```

### Виконання Команд
```bash
# Bash в контейнері
docker-compose exec postgres bash

# psql
docker-compose exec postgres psql -U admin -d learning_db

# SQL файл
docker-compose exec -T postgres psql -U admin -d learning_db < query.sql
```

---

## 🗄️ PostgreSQL (psql) Команди

### Підключення
```bash
# З хосту
docker-compose exec postgres psql -U admin -d learning_db

# З контейнера
psql -U admin -d learning_db
```

### Основні Команди
```sql
\l              -- Список баз даних
\c database     -- Підключитись до БД
\dt             -- Список таблиць
\d table_name   -- Структура таблиці
\du             -- Список користувачів
\q              -- Вийти

\timing on      -- Показувати час виконання
\x              -- Розширений вивід

-- Виконати SQL файл
\i /path/to/file.sql

-- Експорт в CSV
\copy (SELECT * FROM customers) TO '/tmp/customers.csv' CSV HEADER;
```

### Корисні Запити
```sql
-- Розмір таблиць
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Активні з'єднання
SELECT * FROM pg_stat_activity;

-- Версія PostgreSQL
SELECT version();
```

---

## 🐍 Python Команди

### Віртуальне Середовище
```bash
# Створити
python -m venv venv

# Активувати (Linux/Mac)
source venv/bin/activate

# Активувати (Windows)
venv\Scripts\activate

# Деактивувати
deactivate
```

### Залежності
```bash
# Встановити все
pip install -r requirements.txt

# Встановити конкретний пакет
pip install aiohttp psycopg2-binary

# Оновити requirements.txt
pip freeze > requirements.txt

# Показати встановлені
pip list
```

### Запуск Скриптів
```bash
# Event Loop basics
python async_examples/01_async_basics.py

# HTTP клієнт
python async_examples/02_async_http_client.py

# WebSockets
python async_examples/03_websockets_demo.py

# Database connection
python python_db/05_db_connection.py
```

---

## 📓 Jupyter Notebook

### Конвертація
```bash
# .py → .ipynb
jupytext --to notebook python_db/06_jupyter_db_operations.py

# .ipynb → .py
jupytext --to py notebook.ipynb
```

### Запуск
```bash
# Запустити Jupyter Lab
jupyter lab

# Запустити Jupyter Notebook
jupyter notebook

# Конкретний файл
jupyter notebook python_db/06_jupyter_db_operations.ipynb

# Без браузера
jupyter notebook --no-browser
```

---

## 📊 SQL Швидкий Довідник

### SELECT
```sql
-- Базовий
SELECT column1, column2 FROM table;

-- З фільтром
SELECT * FROM customers WHERE city = 'Kyiv';

-- З сортуванням
SELECT * FROM products ORDER BY price DESC LIMIT 10;

-- З агрегацією
SELECT city, COUNT(*) as count 
FROM customers 
GROUP BY city
HAVING COUNT(*) > 5;
```

### JOIN
```sql
-- INNER JOIN
SELECT c.name, o.total
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id;

-- LEFT JOIN
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

### SUBQUERY
```sql
-- В WHERE
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- В FROM
SELECT * FROM (
    SELECT customer_id, SUM(total) as total_spent
    FROM orders
    GROUP BY customer_id
) AS customer_totals
WHERE total_spent > 10000;
```

### Window Functions
```sql
-- ROW_NUMBER
SELECT 
    product_name,
    price,
    ROW_NUMBER() OVER (ORDER BY price DESC) as rank
FROM products;

-- LAG
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month
FROM sales;
```

---

## 🔧 Git Команди

```bash
# Ініціалізація
git init

# Додати файли
git add .

# Commit
git commit -m "Initial commit"

# Перегляд статусу
git status

# Історія
git log --oneline

# Створити .gitignore
echo "venv/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## 🛠️ Troubleshooting

### Порт зайнятий
```bash
# Змінити порт в .env
POSTGRES_PORT=5433

# Або знайти процес
lsof -i :5432
kill -9 <PID>
```

### PostgreSQL не запускається
```bash
# Переглянути логи
docker-compose logs postgres

# Видалити volumes та перезапустити
docker-compose down -v
docker-compose up -d
```

### Python помилки
```bash
# Перевстановити залежності
pip install -r requirements.txt --force-reinstall

# Оновити pip
pip install --upgrade pip
```

### Помилка підключення до БД
```bash
# Перевірити чи запущено
docker-compose ps

# Перевірити логи
docker-compose logs postgres

# Перезапустити
docker-compose restart postgres

# Тест підключення
docker-compose exec postgres psql -U admin -d learning_db -c "SELECT 1"
```

---

## 📝 Корисні Посилання

### Документація
- asyncio: https://docs.python.org/3/library/asyncio.html
- aiohttp: https://docs.aiohttp.org/
- PostgreSQL: https://www.postgresql.org/docs/
- psycopg2: https://www.psycopg.org/docs/

### Навчання
- DataLemur SQL: https://datalemur.com/
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- Real Python: https://realpython.com/

### Інструменти
- pgAdmin: http://localhost:5050 (якщо запущено)
- DBeaver: https://dbeaver.io/
- TablePlus: https://tableplus.com/

---

## ⌨️ VS Code Shortcuts

```
Ctrl+`          - Відкрити термінал
Ctrl+Shift+P    - Command Palette
Ctrl+/          - Закоментувати
Ctrl+D          - Вибрати наступне співпадіння
Ctrl+Shift+K    - Видалити рядок
Alt+Up/Down     - Перемістити рядок
```

---

## 📋 Чеклист Перед Початком

- [x] Docker встановлено та запущено
- [x] Python 3.10+ встановлено
- [x] Git встановлено (опціонально)
- [ ] .env файл створено
- [ ] PostgreSQL запущено (`docker-compose up -d`)
- [ ] Підключення працює (`docker-compose exec postgres psql -U admin -d learning_db`)
- [ ] Python залежності встановлено (`pip install -r requirements.txt`)
- [ ] Тестовий скрипт запущено (`python async_examples/01_async_basics.py`)

---

**✅ Все готово! Можна починати!**

Збережіть цей файл для швидкого доступу до команд під час роботи з проєктом.
