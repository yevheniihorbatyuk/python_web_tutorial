# Module 02 — Learning Path

5 кроків від "що таке ABC" до "бот у Docker-контейнері".

---

## Крок 1: ABC та ієрархія класів

**Файл:** `standalone_examples/01_abc_and_oop.py`

**Запустіть і подивіться що відбувається:**
```bash
python 01_abc_and_oop.py
```

**Що вивчається:**
- `from abc import ABC, abstractmethod`
- Різниця між абстрактним і конкретним методом
- LSP (Liskov Substitution Principle) — порушення vs правильна реалізація
- Навіщо взагалі інтерфейси якщо Python і так duck typing?

**Ключове питання:** Якщо Python підтримує duck typing (`if it walks like a duck...`), навіщо ABC?
→ ABC дає **компіляторну перевірку на рівні instantiation** — не можна створити об'єкт
  якщо не реалізовані всі абстрактні методи. Помилка одразу, не пізніше під час виклику.

---

## Крок 2: SOLID принципи

**Файл:** `standalone_examples/02_solid_principles.py`

Те саме сімейство класів `Human/Person/Child` розширюється щоб показати кожен принцип.

| Принцип | Приклад у файлі | Найчастіший у junior-коді? |
|---------|----------------|--------------------------|
| SRP | `UserService` vs `GodClass` | Так — "God class" анти-патерн |
| OCP | `NotificationSender` + нові канали | Так — `if type == "email": ... elif type == "sms":` |
| LSP | `Child.run()` без порушення | Так — subclass змінює поведінку |
| ISP | `Workable` + `Eatable` окремо | Рідко явно, але важливо |
| DIP | `MessageService(sender: Sender)` | Так — тестабільність |

**Ключове питання:** Які принципи порушуються найчастіше в junior-коді?
→ SRP (god class), OCP (if-elif замість полімorfізму), DIP (жорстко вшиті залежності).

---

## Крок 3: Design Patterns

**Файл:** `standalone_examples/03_design_patterns.py`

**Три паттерни що junior зустріне в реальних проектах:**

```
Singleton → підключення до БД (один пул з'єднань на весь додаток)
Factory   → різні типи повідомлень (Email, SMS, Push) з єдиним інтерфейсом
Adapter   → обгортка навколо стороннього API зі своїм інтерфейсом
```

**Ключове питання:** Коли Singleton — це антипаттерн?
→ Коли ускладнює тестування (глобальний стан) або вводить неявні залежності.
  Краще передавати залежність через конструктор (DIP) і мати Singleton на рівні DI-контейнера.

---

## Крок 4: Dev Tools

**Файл:** `standalone_examples/04_dev_tools.py`

```bash
python 04_dev_tools.py
# Генерує: pyproject.toml, Pipfile, requirements.txt у поточній директорії
```

**Що вивчається:**
- `pip freeze > requirements.txt` — найпростіший підхід, але без поділу dev/prod
- `pipenv` — Pipfile + Pipfile.lock; `pipenv install`, `pipenv shell`
- `poetry` — pyproject.toml + poetry.lock; `poetry add`, `poetry run`

**Правило вибору:**
- Скрипт чи навчальний проект → `pip + requirements.txt`
- Командний web-проект → `poetry` (кращий UX, підтримка публікації на PyPI)
- Legacy проект вже на pipenv → залишити pipenv

---

## Крок 5: Docker

**Файл:** `standalone_examples/06_docker_intro.py`

```bash
python 06_docker_intro.py > Dockerfile
docker build -t chatbot .
docker run -it chatbot          # -i = interactive, -t = pseudo-TTY (термінал)
docker run -d chatbot           # -d = detached (у фоні, без термінала)
```

**Що вивчається:**
- `image` vs `container`: image — клас, container — екземпляр
- `docker build` → `docker run` → `docker ps` → `docker stop`
- Різниця `-i -t` (для інтерактивних додатків) та `-d` (для серверів)

**Ключове питання:** Чому `-it` для нашого чат-бота, але не для FastAPI?
→ Чат-бот читає stdin (інтерактивний). FastAPI — сервер у фоні, отримує HTTP-запити.

---

## Бонус: Chatbot Demo

**Файл:** `standalone_examples/05_chatbot_demo.py`

Простий чат-бот що використовує `Human` інтерфейс — демонструє як паттерни з кроків 1-3
живуть у реальному коді:
- `Human` ABC → команди бота
- Factory → різні типи відповідей
- Команди: `walk`, `run`, `breathe`, `quit`
