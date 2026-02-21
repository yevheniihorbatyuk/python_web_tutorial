# План заняття — Module 14: Testing & Deployment

**Тривалість:** 4 години (240 хвилин)
**Формат:** Live-coding + розбір готового коду + практика
**Передумови:** Module 12 (FastAPI, JWT, SQLAlchemy 2.0 async, pytest)

---

## Структура заняття

| Час | Блок | Зміст |
|-----|------|-------|
| 0:00–0:20 | **[Блок 0]** Огляд і запуск | Архітектура, docker-compose up, Swagger |
| 0:20–0:50 | **[Блок 1]** Email верифікація | Токени, MailHog, FastAPI-Mail |
| 0:50–1:15 | **[Блок 2]** Завантаження файлів | Cloudinary, MIME-валідація |
| 1:15–1:30 | **[Блок 3]** Rate Limiting | SlowAPI, Redis, 429 |
| 1:30–2:00 | **[Блок 4]** Redis Caching | Cache-aside, birthday endpoint |
| 2:00–2:10 | ☕ Перерва | |
| 2:10–3:00 | **[Блок 5]** Тестування | Unit, integration, AsyncMock, coverage |
| 3:00–3:30 | **[Блок 6]** CI/CD | GitHub Actions, PostgreSQL в CI |
| 3:30–3:50 | **[Блок 7]** Deployment | Render.com, Alembic на старті |
| 3:50–4:00 | **[Блок 8]** Q&A + Підсумок | Чекліст, де застосовувати далі |

---

## [Блок 0] Огляд і запуск (0:00–0:20)

### Мета
Розуміти що будуємо і побачити готовий результат перед розбором коду.

### Матеріали
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — системна діаграма
- [contacts_api/README.md](../contacts_api/README.md) — quick start
- [contacts_api/docker-compose.yml](../contacts_api/docker-compose.yml)

### Хід

**1. Нагадування зв'язку з Module 12 (3 хв)**

```
Module 12                      Module 14 (додаємо)
─────────────────────────────────────────────────
User model                  →  + is_verified, avatar_url
JWT access + refresh tokens →  + email verification token
get_current_user dep        →  + require_verified dep
SQLAlchemy 2.0 async        →  Contact model + birthday query
AsyncClient + ASGITransport →  повний test suite (unit + integration)
```

**2. Схема системи (5 хв)**

Намалювати на дошці або показати Mermaid-діаграму з ARCHITECTURE.md:

```
Client → FastAPI → PostgreSQL
              ↘ Redis (cache + rate limit + token blacklist)
              ↘ Cloudinary (avatars)
              ↘ SMTP/MailHog (email verification)
```

**3. Запуск стека (5 хв)**

```bash
cd contacts_api
cp .env.example .env
docker-compose up -d

# Перевірити що все піднялося
docker-compose ps

# MailHog UI: http://localhost:8025
# App Swagger: http://localhost:8000/docs
```

**4. Демо готового API (7 хв)**

Пройти в Swagger:
- `POST /api/v1/auth/register` → email у MailHog
- Клік по лінку верифікації → `is_verified = true`
- `POST /api/v1/auth/login` → отримати токени
- `POST /api/v1/contacts` → створити контакт
- `GET /api/v1/contacts/birthdays` → побачити кешований результат

---

## [Блок 1] Email верифікація (0:20–0:50)

### Мета
Розуміти чому email verification токен ≠ access токен і як це реалізовано.

### Матеріали
- `standalone_examples/02_email_verification_tokens.py`
- `standalone_examples/01_email_sending.py`
- `app/core/security.py`
- `app/services/email.py`
- `app/api/v1/auth.py`

### Хід

**1. Проблема — посилання без терміну дії (5 хв)**

Запустити приклад і показати вивід:

```bash
python standalone_examples/02_email_verification_tokens.py
```

Пояснити таблицю безпеки у виводі:

| Підхід | Термін дії | Purpose claim | Окремий секрет | Безпека |
|--------|-----------|---------------|----------------|---------|
| UUID (підхід 1) | ❌ ніколи | ❌ | ❌ | Низька |
| JWT без exp (підхід 2) | ❌ ніколи | ❌ | ❌ | Середня |
| JWT + exp + purpose (підхід 3) | ✅ 24 год | ✅ | ✅ | Висока |

**Ключове питання до студентів:** "Що станеться якщо access токен (30 хв) спробувати використати як email verification?"

→ Без purpose claim — спрацює. З purpose claim — 400 `Wrong token purpose`.

**2. Три токени в системі (7 хв)**

Показати `app/core/security.py`:

```python
# Три токени, три секрети, три цілі
create_access_token(email)    # purpose="access",       TTL=30хв
create_refresh_token(email)   # purpose="refresh",      TTL=7 днів
create_email_token(email)     # purpose="email_verify", TTL=24 год
```

Чому окремі секрети? → Defense-in-depth: якщо один скомпрометовано, інші не зачеплені.

**3. FastAPI-Mail vs smtplib (5 хв)**

```bash
# Не запускати — просто показати код 01_email_sending.py
# Секція 1: smtplib — блокує event loop!
# Секція 2: aiosmtplib — async, але треба конфігурувати вручну
# Секція 3: FastAPI-Mail — production-ready, Jinja2 шаблони, config через Settings
```

**4. Register → Verify flow (10 хв)**

Читати `app/api/v1/auth.py` разом зі студентами:

```python
# POST /auth/register
# 1. Перевірити що email унікальний
# 2. Хешувати пароль (bcrypt)
# 3. is_verified = False
# 4. create_email_token(email)
# 5. send_verification_email(email, token)
# 6. Повернути 201 (НЕ токени — треба верифікувати!)

# GET /auth/verify/{token}
# 1. decode_email_token(token) → перевіряє exp + purpose
# 2. Знайти user за email
# 3. is_verified = True
# 4. Повернути 200

# POST /auth/login
# if not user.is_verified: raise 403 (не 401!)  ← чому 403?
```

**Питання:** "Чому 403 а не 401 при вході невірифікованого?"
→ 401 = не авторизований (немає токену). 403 = авторизований (знаємо хто) але доступ заборонено.

**5. Перевірка в MailHog (3 хв)**

Зареєструвати нового користувача → http://localhost:8025 → показати лист → перейти по лінку.

---

## [Блок 2] Завантаження файлів (0:50–1:15)

### Мета
Розуміти як FastAPI приймає файли, чому MIME-валідація важлива і як Cloudinary спрощує file hosting.

### Матеріали
- `standalone_examples/03_cloudinary_upload.py`
- `app/services/cloudinary_service.py`
- `app/api/v1/users.py`

### Хід

**1. Чому не зберігати файли на сервері (3 хв)**

```
Проблема з local filesystem:
  - Render.com перезапускає контейнер → файли зникають
  - Горизонтальне масштабування: 3 інстанси не бачать файли одне одного
  - Немає CDN для глобальних клієнтів

Рішення: Cloudinary (free tier) або S3 (DEPLOYMENT_GUIDE.md)
```

**2. UploadFile у FastAPI (5 хв)**

```python
# app/api/v1/users.py
@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile,   # ← НЕ JSON, а multipart/form-data
    current_user: User = Depends(require_verified),
):
    contents = await file.read()  # ← async read у байти
```

Показати різницю у Swagger: звичайний endpoint vs endpoint з `UploadFile`.

**3. MIME-валідація по magic bytes (7 хв)**

Показати `app/services/cloudinary_service.py`:

```python
ALLOWED_MIME_MAGIC = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG":      "image/png",
    b"GIF8":         "image/gif",
    b"RIFF":         "image/webp",
}

def _validate_mime(data: bytes) -> None:
    for magic, mime_type in ALLOWED_MIME_MAGIC.items():
        if data.startswith(magic):
            return  # OK
    raise HTTPException(422, "File must be a JPEG, PNG, GIF or WebP image")
```

**Питання:** "Чому не перевіряємо розширення файлу (.jpg, .png)?"
→ Розширення легко підробити: `malicious.exe` → `avatar.jpg`. Magic bytes підробити набагато складніше.

**4. Cloudinary upload та URL-трансформації (10 хв)**

```python
# upload_avatar() — що відбувається:
# 1. read() → bytes
# 2. _validate_mime(contents) → 422 якщо не зображення
# 3. cloudinary.uploader.upload(contents, public_id=..., overwrite=True)
# 4. Повернути URL

# URL-трансформація (без повторного завантаження!)
# https://res.cloudinary.com/demo/image/upload/w_200,h_200,c_fill/avatar_42.jpg
```

Показати `standalone_examples/03_cloudinary_upload.py` секцію URL-трансформацій.

---

## [Блок 3] Rate Limiting (1:15–1:30)

### Мета
Розуміти навіщо rate limiting на auth endpoints і як SlowAPI + Redis реалізує distributed лімітування.

### Матеріали
- `standalone_examples/04_rate_limiting.py`
- `app/core/rate_limit.py`
- `app/api/v1/auth.py`

### Хід

**1. Навіщо rate limiting (3 хв)**

```
Без rate limit на /login:
  Атакуючий: for password in wordlist: POST /login
  → Brute force за секунди

Без rate limit на /register:
  Бот: while True: POST /register
  → Спам до email-провайдера, database flood
```

**2. SlowAPI setup (4 хв)**

Показати `app/core/rate_limit.py`:

```python
limiter = Limiter(
    key_func=get_remote_address,   # ключ = IP клієнта
    storage_uri="redis://redis:6379",  # distributed counter
)

# В main.py:
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

**3. Декоратори на endpoints (3 хв)**

```python
# app/api/v1/auth.py
@router.post("/register")
@limiter.limit("5/minute")       # ← 5 реєстрацій з одного IP за хвилину
async def register(..., request: Request):  # ← request обов'язковий для SlowAPI
    ...

@router.post("/login")
@limiter.limit("10/minute")      # ← login трохи лояльніше
```

**4. Демо 429 (5 хв)**

```bash
# Запустити приклад сервера в окремому терміналі
python standalone_examples/04_rate_limiting.py

# Перевантажити /register (6-й запит → 429)
for i in $(seq 1 7); do
    curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8001/register \
    -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"123"}'
done
```

Показати 429 + `Retry-After` заголовок.

**5. Rate limit у тестах (1 хв)**

```python
# tests/conftest.py — чому вимикаємо лімітер в тестах
app.state.limiter.enabled = False
# Без цього: 6-й тест падає на 429 навіть для коректних даних
```

---

## [Блок 4] Redis Caching (1:30–2:00)

### Мета
Розуміти cache-aside pattern, дизайн cache ключів і birthday query з year-rollover.

### Матеріали
- `standalone_examples/05_redis_caching.py`
- `app/core/cache.py`
- `app/services/contacts.py`
- `app/api/v1/contacts.py`

### Хід

**1. Навіщо кешувати birthday endpoint (5 хв)**

```
GET /contacts/birthdays — проблема без кешу:
  - Кожен запит → SQL з date arithmetic по всіх контактах
  - Дані змінюються рідко (тільки при create/update/delete контакту)
  - Один юзер може перевіряти щогодини → зайве навантаження

Рішення: Cache-aside з TTL = 1 год
```

**2. Cache-aside pattern (7 хв)**

```python
# app/core/cache.py — патерн у чистому вигляді
async def get_or_set_cache(key: str, ttl: int, loader):
    redis = await get_redis()

    # 1. Перевірити кеш
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)   # ← CACHE HIT

    # 2. Промах → завантажити свіжі дані
    data = await loader()           # ← DB query

    # 3. Зберегти в кеш
    await redis.setex(key, ttl, json.dumps(data))

    return data                     # ← CACHE MISS (але тепер закешовано)
```

Намалювати flowchart: Request → Redis HIT? → Return | MISS → DB → Store → Return

**3. Дизайн cache ключа (5 хв)**

```python
# app/api/v1/contacts.py
cache_key = f"birthdays:{current_user.id}:{date.today()}"
# ┌─────────────────────────────────────────────────────────
# │ birthdays:42:2026-02-21
# └─────────────────────────────────────────────────────────
# Чому включаємо date.today()?
# → Завтра ключ буде birthdays:42:2026-02-22
# → Стара версія (2026-02-21) ніколи не вернеться
# → Cache автоматично "протухає" о опівночі без explicit invalidation!
```

**4. Cache invalidation (3 хв)**

```python
# При будь-якій зміні контактів — видалити кеш дня
await redis.delete(f"birthdays:{user_id}:{date.today()}")
```

**Питання:** "Що якщо TTL ще не вийшов але контакт видалили?"
→ Invalidate при DELETE. А якщо забути? → TTL = 1 год захищає від вічної сталевості.

**5. Birthday query — year-rollover (7 хв)**

Показати `app/services/contacts.py` — `get_upcoming_birthdays()`:

```python
# Проблема: 28 грудня + 7 днів = 4 січня наступного року
# EXTRACT(month, day) не розуміє "наступного тижня"

# Рішення: нормалізувати birthdate до поточного року
for contact in contacts:
    try:
        birthday_this_year = contact.birthday.replace(year=today.year)
    except ValueError:  # ← 29 лютого у не-високосний рік
        birthday_this_year = contact.birthday.replace(year=today.year, day=28)

    if birthday_this_year < today:
        birthday_this_year = birthday_this_year.replace(year=today.year + 1)

    days_until = (birthday_this_year - today).days
    if 0 <= days_until <= 7:
        ...
```

**6. Token blacklist (3 хв)**

```python
# Logout — додати refresh token до blacklist
# app/core/cache.py
await blacklist_token(refresh_token, ttl=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400)

# Кожен запит — перевірити чи не в blacklist
if await is_token_blacklisted(token):
    raise HTTPException(401, "Token has been revoked")
```

---

## ☕ Перерва (2:00–2:10)

---

## [Блок 5] Тестування (2:10–3:00)

### Мета
Розуміти різницю між unit і integration тестами, AsyncMock, dependency_overrides, coverage.

### Матеріали
- `standalone_examples/06_async_testing.py`
- `tests/conftest.py`
- `tests/unit/test_security.py`
- `tests/unit/test_contact_service.py`
- `tests/integration/test_auth.py`
- `docs/TESTING_GUIDE.md`

### Хід

**1. Піраміда тестування (5 хв)**

```
        ╱ E2E ╲         ← не маємо (занадто повільно)
      ╱─────────╲
    ╱ Integration ╲     ← tests/integration/ (HTTP flows)
  ╱─────────────────╲
╱       Unit          ╲  ← tests/unit/ (чисті функції)
```

**Unit тести:** без HTTP, SQLite in-memory, без зовнішніх сервісів. Швидко (<2с).
**Integration тести:** повний HTTP flow з AsyncClient, SQLite in-memory + AsyncMock для email/Cloudinary.

**2. conftest.py — fixture chain (10 хв)**

Читати `tests/conftest.py` зверху вниз:

```python
# 1. async_engine → тимчасова SQLite БД для одного тесту
# 2. async_session → AsyncSession з цієї БД
# 3. client → AsyncClient + dependency_overrides[get_db] → наша тестова сесія
# 4. test_user → зареєстрований, верифікований юзер
# 5. auth_headers → {"Authorization": "Bearer <token>"}

# Ключовий патерн:
app.dependency_overrides[get_db] = lambda: async_session
# FastAPI замінює реальну get_db() нашою тестовою сесією
# → жодного підключення до PostgreSQL в тестах
```

Ключова ідея: `dependency_overrides` — це механізм DI-підміни. Той самий, що дозволяє підміняти Redis, Email і Cloudinary в тестах.

**3. Unit тести: чисті функції (8 хв)**

Показати `tests/unit/test_security.py`:

```python
def test_create_access_token_has_correct_claims():
    token = create_access_token("alice@example.com")
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["purpose"] == "access"
    assert payload["sub"] == "alice@example.com"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()
```

Показати `tests/unit/test_contact_service.py` — parametrize для birthday edge cases:

```python
@pytest.mark.parametrize("birthday,expected_days", [
    (date(1990, 2, 28), 7),   # звичайний випадок
    (date(1992, 2, 29), 6),   # 29 лютого → fallback на 28-ме у не-високосний рік
    (date(1985, 12, 30), 1),  # year-rollover: 30 грудня
])
def test_get_upcoming_birthdays(birthday, expected_days):
    ...
```

**4. Integration тести: HTTP flows (12 хв)**

```python
# tests/integration/test_auth.py — повний register → verify → login flow

async def test_full_auth_flow(client):
    # 1. Register
    resp = await client.post("/api/v1/auth/register",
        json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 201

    # 2. Login до верифікації → 403
    resp = await client.post("/api/v1/auth/login",
        data={"username": "test@example.com", "password": "secret123"})
    assert resp.status_code == 403

    # 3. Verify
    token = get_verification_token_from_mock()  # AsyncMock перехопив виклик
    resp = await client.get(f"/api/v1/auth/verify/{token}")
    assert resp.status_code == 200

    # 4. Login після верифікації → 200
    resp = await client.post("/api/v1/auth/login", ...)
    assert resp.status_code == 200
    assert "access_token" in resp.json()
```

Показати як MockMail перехоплює `send_message`:

```python
# conftest.py
mock_mail = AsyncMock()
app.dependency_overrides[get_email_service] = lambda: mock_mail

# В тесті
args = mock_mail.send_message.call_args
token = extract_token_from_email(args)  # дістати токен з "листа"
```

**5. Запустити тести і coverage (10 хв)**

```bash
cd contacts_api

# Unit тести (швидко, без Docker)
pytest tests/unit/ -v

# Integration тести (потрібен docker-compose up)
pytest tests/integration/ -v

# З coverage
pytest tests/ --cov=app --cov-report=term-missing

# Тільки провалені тести
pytest tests/ -v --tb=short -x

# Конкретний тест
pytest tests/unit/test_security.py::test_create_access_token_has_correct_claims -v
```

Показати coverage report і пояснити: 80% — не магія, а contractual minimum.

---

## [Блок 6] CI/CD — GitHub Actions (3:00–3:30)

### Мета
Розуміти структуру workflow і чому тести в CI різняться від локальних.

### Матеріали
- `standalone_examples/07_github_actions_explained.py`
- `contacts_api/.github/workflows/ci.yml`

### Хід

**1. Згенерувати і прочитати CI файл (8 хв)**

```bash
python standalone_examples/07_github_actions_explained.py
# → виводить .github/workflows/ci.yml з inline коментарями
```

Ключові секції в YAML (читати разом):

```yaml
# Тригери
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Service containers
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_PASSWORD: testpassword
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
    # HealthCheck: runner чекає поки postgres готовий

  redis:
    image: redis:7-alpine
    options: --health-cmd "redis-cli ping"
```

**2. Два job-и: unit → integration (7 хв)**

```yaml
jobs:
  unit-tests:       # SQLite in-memory, без сервісів, швидко
    runs-on: ubuntu-latest
    steps:
      - pytest tests/unit/ --cov=app

  integration-tests: # Потрібні postgres + redis
    runs-on: ubuntu-latest
    needs: [unit-tests]    # ← запускається ПІСЛЯ unit
    services:
      postgres: ...
      redis: ...
    steps:
      - pytest tests/integration/ --cov=app
```

**Питання:** "Чому unit тести без PostgreSQL?"
→ SQLite швидший і не вимагає сервісу. Якщо unit тести провалились — не гаємо час на запуск сервісів.

**3. Чому PostgreSQL в CI, SQLite локально (5 хв)**

```
Локально:  SQLite in-memory — швидко, просто, ізольовано
CI:        PostgreSQL — реальний рушій виловлює баги специфічні для PG:
             - EXTRACT() семантика
             - RETURNING clause
             - ILIKE case sensitivity
             - ON CONFLICT поведінка

Помилка яку SQLite не зловить:
  SQLAlchemy: func.extract('month', Contact.birthday)
  → SQLite: повертає рядок "2"
  → PostgreSQL: повертає число 2
```

**4. Auto-deploy (5 хв)**

```
GitHub push → GitHub Actions → all tests pass → Render auto-deploy

Render webhook URL додається в GitHub Secrets:
  Settings → Secrets → RENDER_DEPLOY_HOOK_URL

В ci.yml:
  - name: Deploy to Render
    if: github.ref == 'refs/heads/main' && success()
    run: curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

**5. Branch protection (5 хв)**

```
GitHub Settings → Branches → Branch protection rules:
  ✅ Require status checks: unit-tests, integration-tests
  ✅ Require branches to be up to date
  ✅ Restrict who can push to main

Результат: жодного push в main без зелених тестів
```

---

## [Блок 7] Deployment на Render.com (3:30–3:50)

### Мета
Зрозуміти повний шлях від коду до production.

### Матеріали
- `docs/DEPLOYMENT_GUIDE.md`
- `contacts_api/Dockerfile`

### Хід

**1. Render.com — чому (3 хв)**

```
Render vs Heroku vs Railway vs Fly.io:
  ✅ Free PostgreSQL (без кредитки)
  ✅ Auto-deploy з GitHub
  ✅ SSL автоматично
  ✅ Environment variables через UI
  ✅ Logs в реальному часі
  ❌ Free tier "cold start" (30 сек прогрів)
```

**2. Alembic на старті (5 хв)**

```bash
# Render "Start command":
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

```
Чому так а не окремий step?
  - Render не підтримує pre-start hooks у free tier
  - Alembic upgrade head ідемпотентний (безпечно запускати кожного разу)
  - Якщо upgrade провалиться — uvicorn не запуститься → помітно відразу
```

**3. Environment variables у prod (5 хв)**

```bash
# Render Dashboard → Environment → Add Variable:
JWT_SECRET_KEY=<random 64 chars>
JWT_REFRESH_SECRET=<random 64 chars>
EMAIL_TOKEN_SECRET=<random 64 chars>
DATABASE_URL=<Render PostgreSQL URL>
REDIS_URL=<Upstash Redis або Render Redis>
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=<Gmail App Password — НЕ основний пароль!>
```

**4. Gmail App Password (2 хв)**

```
Google Account → Security → 2-Step Verification → App passwords
→ Generate → 16-символьний пароль
→ Це йде в MAIL_PASSWORD (не основний пароль!)
```

**5. S3 як альтернатива Cloudinary (5 хв)**

Показати секцію в `docs/DEPLOYMENT_GUIDE.md`:

```python
# Тільки services/cloudinary_service.py змінюється:
import boto3

async def upload_avatar(data: bytes, user_id: int) -> str:
    s3 = boto3.client("s3")
    key = f"avatars/{user_id}.jpg"
    s3.put_object(Bucket="my-bucket", Key=key, Body=data)
    return f"https://my-bucket.s3.amazonaws.com/{key}"

# Все інше (API endpoint, schema, model) — без змін
# Це і є перевага шару services/
```

---

## [Блок 8] Q&A і Підсумок (3:50–4:00)

### Чекліст: що студент має вміти після цього заняття

```
Email verification:
  □ Пояснити навіщо purpose claim у JWT
  □ Пояснити чому access token ≠ verification token
  □ Показати flow: register → email → verify → login

File uploads:
  □ Пояснити чому MIME validation по magic bytes, а не по розширенню
  □ Описати як Cloudinary URL-трансформації економлять ресурси

Rate limiting:
  □ Пояснити навіщо rate limit тільки на /login і /register
  □ Показати як вимкнути limiter в тестах

Redis caching:
  □ Намалювати cache-aside flowchart
  □ Пояснити чому cache key включає date.today()
  □ Сказати коли треба робити cache invalidation

Testing:
  □ Пояснити різницю unit vs integration тестів
  □ Показати як dependency_overrides замінює get_db
  □ Показати як AsyncMock перехоплює email

CI/CD:
  □ Пояснити чому два job-и (unit → integration)
  □ Пояснити чому SQLite локально але PostgreSQL в CI
```

### Де ці патерни зустрінуться далі

| Патерн | Де ще |
|--------|-------|
| Email verification | Password reset, 2FA, newsletters |
| File upload + Cloudinary | Profile photos, document management |
| Rate limiting (SlowAPI) | Всі public API |
| Redis cache-aside | Session storage, feed caching, leaderboards |
| pytest-asyncio + AsyncMock | Всі наступні async Python проекти |
| GitHub Actions | Всі professional проекти |
| Render/cloud deploy | Railway, Fly.io, AWS ECS — та сама концепція |

---

## Домашнє завдання (опціонально)

**Рівень 1 (базовий):**
1. Запустити стек локально (`docker-compose up`)
2. Пройти повний flow через Swagger: register → verify → login → CRUD
3. Запустити `pytest tests/ --cov=app` і прочитати coverage report

**Рівень 2 (середній):**
4. Додати endpoint `DELETE /api/v1/contacts/{id}` з cache invalidation
5. Написати unit тест для нового endpoint
6. Написати integration тест (verify → login → create → delete)

**Рівень 3 (advanced):**
7. Додати `POST /auth/password-reset/request` — надіслати email з токеном
8. Додати `POST /auth/password-reset/confirm` — прийняти токен і новий пароль
9. Написати повний integration тест flow

---

## Швидкі команди для заняття

```bash
# Запуск стека
cd contacts_api && docker-compose up -d

# Перегляд логів
docker-compose logs -f app

# Тести (без Docker)
pytest tests/unit/ -v

# Тести (потрібен docker-compose)
pytest tests/integration/ -v

# З coverage
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80

# Генерація CI файлу
python standalone_examples/07_github_actions_explained.py > .github/workflows/ci.yml

# Демо rate limit
for i in $(seq 1 7); do curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"spam@test.com","password":"123456","full_name":"Bot"}'; done

# MailHog UI
open http://localhost:8025

# Swagger
open http://localhost:8000/docs
```
