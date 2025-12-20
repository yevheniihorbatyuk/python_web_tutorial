# 🚀 Швидкий Старт

## Крок 1: Підготовка

```bash
# Клонувати/створити папку проєкту
cd module6_async_db

# Створити віртуальне середовище
python -m venv venv

# Активувати (Linux/Mac)
source venv/bin/activate

# Активувати (Windows)
venv\Scripts\activate

# Встановити залежності
pip install -r requirements.txt
```

## Крок 2: Запустити PostgreSQL

```bash
# Скопіювати .env файл
cp .env.example .env

# Запустити тільки PostgreSQL (мінімальний режим)
docker-compose up -d

# АБО запустити повний стек (PostgreSQL + pgAdmin + Redis)
docker-compose --profile full up -d

# Перевірити статус
docker-compose ps

# Переглянути логи
docker-compose logs -f postgres
```

## Крок 3: Перевірити підключення

```bash
# Підключитися до PostgreSQL через psql
docker-compose exec postgres psql -U admin -d learning_db

# Виконати тестовий запит
SELECT COUNT(*) FROM customers;

# Вийти
\q
```

## Крок 4: Запустити Python приклади

```bash
# 1. Event Loop та async basics
python async_examples/01_async_basics.py

# 2. Асинхронні HTTP запити
python async_examples/02_async_http_client.py

# 3. WebSockets (опціонально)
python async_examples/03_websockets_demo.py

# 4. Робота з PostgreSQL
python python_db/05_db_connection.py
```

## Крок 5: Jupyter Notebook

```bash
# Конвертувати .py в .ipynb
jupytext --to notebook python_db/06_jupyter_db_operations.py

# Запустити Jupyter
jupyter notebook python_db/06_jupyter_db_operations.ipynb
```

## Доступ до сервісів

- **PostgreSQL**: `localhost:5432`
  - User: `admin`
  - Password: `admin123`
  - Database: `learning_db`

- **pgAdmin** (якщо запущено --profile full): `http://localhost:5050`
  - Email: `admin@example.com`
  - Password: `admin123`

- **Redis** (якщо запущено --profile full): `localhost:6379`

## Корисні команди Docker

```bash
# Зупинити все
docker-compose down

# Зупинити і видалити volumes (ВИДАЛИТЬ ДАНІ!)
docker-compose down -v

# Перезапустити PostgreSQL
docker-compose restart postgres

# Переглянути логи конкретного сервісу
docker-compose logs -f postgres

# Виконати команду в контейнері
docker-compose exec postgres bash
```

## Перевірка SQL запитів

```bash
# Відкрити psql
docker-compose exec postgres psql -U admin -d learning_db

# Корисні команди в psql:
\dt              # Показати всі таблиці
\d customers     # Показати структуру таблиці
\q               # Вийти
```

## Troubleshooting

### Помилка підключення до PostgreSQL

```bash
# Перевірити чи запущено
docker-compose ps

# Переглянути логи
docker-compose logs postgres

# Перезапустити
docker-compose restart postgres
```

### Порт вже зайнятий

Змініть порт у `.env` файлі:
```
POSTGRES_PORT=5433  # Змініть на вільний порт
```

### Помилка з залежностями Python

```bash
# Оновити pip
pip install --upgrade pip

# Переустановити залежності
pip install -r requirements.txt --force-reinstall
```

## Очищення

```bash
# Зупинити все
docker-compose down

# Видалити volumes (база даних буде видалена!)
docker-compose down -v

# Видалити віртуальне середовище
rm -rf venv
```

## Наступні кроки

1. Пройдіть всі Python приклади
2. Виконайте SQL задачі з `sql_examples/04_sql_examples.sql`
3. Дослідіть дані через Jupyter Notebook
4. Спробуйте написати власні асинхронні скрипти
5. Створіть свої SQL запити та аналітику

---

**Готово! Тепер можна працювати з матеріалами заняття! 🎉**
