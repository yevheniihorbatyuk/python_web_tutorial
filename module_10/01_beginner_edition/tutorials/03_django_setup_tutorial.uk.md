# Туторіал: Налаштування проєкту Django

Цей туторіал проведе вас через початкове налаштування проєкту Django з нуля.

**Мета:** Створити новий проєкт Django та додаток, налаштувати параметри та запустити сервер розробки.

---

## Крок 1: Встановлення Django

Якщо ви ще не встановили Django, встановіть його за допомогою pip.
```bash
pip install Django
```

---

## Крок 2: Створення проєкту та додатку

1.  **Створіть папку проєкту** та перейдіть до неї.
    ```bash
    mkdir my_django_project && cd my_django_project
    ```

2.  **Створіть новий проєкт Django.** Крапка `.` в кінці вказує Django створити проєкт у поточному каталозі.
    ```bash
    django-admin startproject config .
    ```

3.  **Створіть новий додаток.** Назвемо наш додаток `quotes`.
    ```bash
    python manage.py startapp quotes
    ```

Тепер ваш каталог повинен виглядати так:
```
my_django_project/
├── config/
├── quotes/
└── manage.py
```

---

## Крок 3: Налаштування `settings.py`

Вам потрібно повідомити Django про ваш новий додаток.

1.  Відкрийте `config/settings.py`.
2.  Знайдіть список `INSTALLED_APPS`.
3.  Додайте ваш додаток `quotes` до списку.

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quotes.apps.QuotesConfig', # Або просто 'quotes'
]
```

---

## Крок 4: Запуск сервера розробки

Переконаймося, що все працює.
```bash
python manage.py runserver
```
Ви повинні побачити вивід, схожий на цей:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
Відкрийте веб-браузер і перейдіть за адресою `http://127.0.0.1:8000/`. Ви повинні побачити стандартну сторінку привітання Django.

---

## Крок 5: Застосування початкових міграцій

Django постачається з вбудованими додатками (такими як `admin` та `auth`), яким потрібні власні таблиці в базі даних. Створімо їх.

Зупиніть сервер (Ctrl+C) і запустіть:
```bash
python manage.py migrate
```
Ця команда створює початкову базу даних (файл `db.sqlite3`) і налаштовує необхідні таблиці для основних функцій Django.

---

## Крок 6: Створення суперкористувача

Щоб отримати доступ до адмін-панелі, вам потрібен обліковий запис адміністратора.
```bash
python manage.py createsuperuser
```
Дотримуйтесь інструкцій, щоб створити ім'я користувача та пароль.

---

## Крок 7: Дослідження адмін-панелі

1.  **Знову запустіть сервер**:
    ```bash
    python manage.py runserver
    ```
2.  **Перейдіть за URL-адресою адмін-панелі**: `http://127.0.0.1:8000/admin/`
3.  **Увійдіть**, використовуючи облікові дані суперкористувача, які ви щойно створили.

Тепер ви перебуваєте в панелі адміністрування Django. Зараз вона переважно порожня, але коли ви додасте моделі до свого додатку `quotes`, ви зможете керувати ними звідси.

Вітаємо! Ви успішно налаштували проєкт Django. Наступний крок — визначення ваших моделей.
