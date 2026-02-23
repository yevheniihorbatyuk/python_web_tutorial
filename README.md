# Python Web — Курс веб-розробки та баз даних

> Навчальний репозиторій для занять з Python web/data. Кожен модуль самодостатній: містить код, Docker-інфраструктуру, конспекти та сценарій уроку.

---

## Модулі

| Модуль | Тема | Стек | Папка |
|--------|------|------|-------|
| **06** | Реляційні БД, asyncio, PostgreSQL | asyncio, aiohttp, psycopg2, Docker | [`module_06/`](module_06/) |
| **08** | SQLAlchemy ORM, MongoDB, Redis, RabbitMQ | SQLAlchemy 2.0, PyMongo, Motor, pika | [`module_08/`](module_08/) |
| **10** | Django — веб-фреймворк, ORM, DRF | Django 5, DRF, PostgreSQL, Celery | [`module_10/`](module_10/) |
| **12** | FastAPI — три рівні складності | FastAPI, SQLAlchemy 2.0, asyncpg, JWT | [`module_12/`](module_12/) |
| **14** | Тестування та деплой FastAPI-додатку | pytest-asyncio, GitHub Actions, Render | [`module_14/`](module_14/) |

---

## Модуль 06 — Реляційні БД та асинхронне програмування [`module_06/`](module_06/)

**Beginner (3–4 год):** event loop, `async/await`, `aiohttp`, базові SQL-запити, PostgreSQL
**Advanced DS/DE (+2–3 год):** production ETL, архітектурні патерни (Repository, DI, Factory), ML feature store, аналітичний SQL (cohort, funnel, time-series)

```
module_06/
├── async_examples/          # event loop, aiohttp, WebSockets
├── advanced_examples/       # ETL pipeline, patterns, ML feature store
├── python_db/               # CRUD з psycopg2
├── sql_examples/            # базовий + аналітичний SQL
├── docker-compose.yml       # PostgreSQL 15
└── docs/                    # START_HERE, QUICKSTART, LESSON_PLAN, CHEATSHEET
```

**Стек:** Python 3.11+, PostgreSQL 15, asyncio, aiohttp, psycopg2, pandas, Jupyter, Docker

---

## Модуль 08 — SQLAlchemy, NoSQL, кеші та черги [`module_08/`](module_08/)

**Beginner (2.5–3 год):** SQLAlchemy 2.0 ORM, MongoDB (PyMongo), `lru_cache`/Redis, RabbitMQ
**Advanced DS/DE (+2 год):** event-driven ingestion, CDC-патерни, lean ETL, observability

```
module_08/
├── sqlalchemy_examples/     # models, CRUD, relationships (User→Address→City→Country)
├── mongodb_examples/        # PyMongo (sync) + Motor (async)
├── caching/                 # lru_cache та Redis cache-aside
├── messaging_rabbitmq/      # producer + consumer
├── beginner_edition/        # спрощений трек
├── advanced_edition/        # production-патерни
├── docker-compose.yml       # PostgreSQL, MongoDB, RabbitMQ, Redis
└── docs/                    # START_HERE, QUICKSTART, LESSON_PLAN, CHEATSHEET
```

**Стек:** SQLAlchemy 2.0, PostgreSQL, MongoDB, Motor, RabbitMQ (pika), Redis, Docker

---

## Модуль 10 — Django [`module_10/`](module_10/)

```
module_10/
├── 03_django_app/           # основний додаток: User, City, Country, admin
├── 04_event_hub/            # advanced: DRF, складні workflow
├── documentation/en/ uk/   # документація двома мовами
├── docker-compose.yml       # Django, PostgreSQL, Redis
└── requirements.txt
```

**Стек:** Django 5.0, Django REST Framework 3.14, PostgreSQL 15, Redis, Celery, pytest-django, Docker

---

## Модуль 12 — FastAPI (три рівні) [`module_12/`](module_12/)

```
module_12/
├── beginner_edition/        # ⭐⭐   todo_app — маршрути, CRUD, JWT, тести
├── intermediate_edition/    # ⭐⭐⭐  blog_api — відносини моделей, пагінація
├── advanced_edition/        # ⭐⭐⭐⭐ ml_registry — production архітектура, ML
├── Module12_Complete_Learning_Path.ipynb
└── docs/                    # LEARNING_PATH, QUICKSTART, CHECKLIST
```

**Стек:** FastAPI 0.109, SQLAlchemy 2.0, asyncpg, Pydantic 2.5+, python-jose (JWT), pytest-asyncio, PostgreSQL, Docker

---

## Модуль 14 — Тестування та деплой [`module_14/`](module_14/)

Повноцінний **Contacts API** з email-верифікацією, аватарами, rate limiting і CI/CD.

```
module_14/
├── contacts_api/
│   ├── app/
│   │   ├── api/v1/          # auth, contacts, users
│   │   ├── core/            # security, cache, rate_limit, dependencies
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── schemas/         # Pydantic
│   │   └── services/        # auth, contacts, email, cloudinary
│   ├── tests/
│   │   ├── unit/            # security, email service, contact service
│   │   └── integration/     # auth flow, contacts CRUD, users/avatar
│   ├── alembic/             # міграції БД
│   ├── .github/workflows/   # CI/CD: unit + integration jobs → deploy Render
│   ├── docker-compose.yml   # FastAPI, PostgreSQL 16, Redis, MailHog
│   └── pyproject.toml       # pytest config, coverage ≥ 80%
└── standalone_examples/     # email, tokens, cloudinary, rate limiting, redis, CI/CD
```

**API ендпоінти:**

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/api/v1/auth/register` | Реєстрація + email-верифікація |
| GET | `/api/v1/auth/verify/{token}` | Підтвердження email |
| POST | `/api/v1/auth/login` | Логін (OAuth2 form) |
| POST | `/api/v1/auth/refresh` | Оновлення access token |
| POST | `/api/v1/auth/logout` | Інвалідація refresh token (Redis blacklist) |
| GET/POST | `/api/v1/contacts/` | Список / створення контактів |
| GET | `/api/v1/contacts/birthdays` | Дні народження (кешується в Redis) |
| GET/PATCH/DELETE | `/api/v1/contacts/{id}` | Операції з контактом |
| GET | `/api/v1/users/me` | Профіль поточного користувача |
| POST | `/api/v1/users/me/avatar` | Завантаження аватара (Cloudinary) |

**Тестування:**
- 49 тестів (23 unit + 26 integration), покриття 84%
- SQLite in-memory для інтеграційних тестів — без зовнішнього PostgreSQL
- Redis і rate limiter замінюються in-memory моками в `conftest.py`
- CI: два окремих jobs — `unit-tests` і `integration-tests` → деплой на Render

**Стек:** FastAPI 0.115, SQLAlchemy 2.0, asyncpg, Alembic, FastAPI-Mail, Cloudinary, Redis, SlowAPI, pytest-asyncio, GitHub Actions, Docker, PostgreSQL 16

---

## Як користуватися

```bash
# 1. Оберіть модуль і прочитайте START_HERE
cd module_14/contacts_api/
cat docs/QUICKSTART.md

# 2. Скопіюйте змінні оточення
cp .env.example .env

# 3. Запустіть інфраструктуру
docker-compose up -d

# 4. Запустіть тести
pytest tests/ -v --cov=app --cov-report=term-missing

# 5. Для поглиблення
cat docs/LESSON_PLAN.md
cat docs/ARCHITECTURE.md
```

---

## Загальні принципи репозиторію

- Кожен модуль є самодостатнім: власний `docker-compose.yml`, `.env.example`, документація.
- Документація в `docs/`: `START_HERE`, `QUICKSTART`, `LESSON_PLAN`, `SUMMARY`, `ADVANCED_README`, `CHEATSHEET`.
- Нові модулі додавайте як `module_XX/` зі стандартною структурою `docs/`.
- Секрети — тільки у `.env` (не комітити). Зразок у `.env.example`.

---

**Версія:** 2.1 · **Оновлено:** 2026-02-21
