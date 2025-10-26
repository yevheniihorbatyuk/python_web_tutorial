# 🚀 Швидкий Старт

## Крок 1: Клонувати та налаштувати Python

```bash
# Клонувати репозиторій
git clone <repository-url>
cd python_web_tutorial

# Створити віртуальне середовище
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Встановити пакет у режимі розробки (включно з pytest)
pip install -e .[dev]
```

## Крок 2: Запустити PostgreSQL

```bash
# Скопіювати змінні середовища
cp .env.example .env

# Підняти інфраструктуру
docker-compose up -d

# Перевірити статус
docker-compose ps

# Переглянути логи (опціонально)
docker-compose logs -f postgres
```

## Крок 3: Підготувати навчальні дані

```bash
# Створити схему та завантажити демо-дані
python -m python_web_tutorial.tools.bootstrap_data

# Перевірити стан таблиць без змін
python -m python_web_tutorial.tools.bootstrap_data --check

# Повторно залити демо-дані
python -m python_web_tutorial.tools.bootstrap_data --force
```

## Крок 4: Запустити Python приклади

```bash
# 1. Event Loop та async basics
python python_web_tutorial/async_examples/01_async_basics.py

# 2. Асинхронні HTTP запити
python python_web_tutorial/async_examples/02_async_http_client.py

# 3. WebSockets (опціонально)
python python_web_tutorial/async_examples/03_websockets_demo.py

# 4. Робота з PostgreSQL
python python_web_tutorial/python_db/05_db_connection.py
```

## Крок 5: Jupyter Notebook

```bash
# Конвертувати .py в .ipynb (опціонально)
jupytext --to notebook python_web_tutorial/python_db/06_jupyter_db_operations.py

# Запустити Jupyter
jupyter notebook python_web_tutorial/python_db/06_jupyter_db_operations.ipynb
```

## Доступ до сервісів

- **PostgreSQL**: `localhost:5432`
  - User: `admin`
  - Password: `admin123`
  - Database: `learning_db`

- **pgAdmin** (якщо запущено `--profile full`): `http://localhost:5050`
  - Email: `admin@example.com`
  - Password: `admin123`

- **Redis** (якщо запущено `--profile full`): `localhost:6379`

## Корисні команди Docker

```bash
# Зупинити все
docker-compose down

# Зупинити і видалити volumes (видалить дані!)
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

### Проблеми з Python залежностями

```bash
# Оновити pip
pip install --upgrade pip

# Перевстановити пакет у режимі розробки
pip install --force-reinstall -e .[dev]
```

## Очищення

```bash
# Зупинити все
docker-compose down

# Видалити volumes (база даних буде видалена!)
docker-compose down -v

# Видалити віртуальне середовище
rm -rf .venv
```

## Наступні кроки

1. Пройдіть всі Python приклади
2. Виконайте SQL задачі з `python_web_tutorial/sql_examples/04_sql_examples.sql`
3. Дослідіть дані через Jupyter Notebook
4. Спробуйте написати власні асинхронні скрипти
5. Створіть свої SQL запити та аналітику

---

**Готово! Тепер можна працювати з матеріалами заняття! 🎉**
