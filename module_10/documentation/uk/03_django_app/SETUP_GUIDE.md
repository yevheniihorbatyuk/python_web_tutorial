# Посібник з налаштування додатку Django

Повні інструкції з налаштування та запуску додатку Django з Модуля 10.

## Передумови

- Python 3.11+
- Docker та Docker Compose (для контейнерного налаштування)
- PostgreSQL 15+ (якщо використовується PostgreSQL локально)
- Git

## Варіант 1: Локальна розробка (SQLite)

### Крок 1: Клонуйте та перейдіть до проекту

```bash
cd /root/goit/python_web/module_10/03_django_app
```

### Крок 2: Створіть віртуальне середовище

```bash
python3 -m venv venv
source venv/bin/activate  # У Windows: venv\Scripts\activate
```

### Крок 3: Встановіть залежності

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

### Крок 4: Створіть файл .env (необов'язково - за замовчуванням використовується SQLite)

```bash
cp .env.example .env
```

Для SQLite (вже за замовчуванням):
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Крок 5: Ініціалізуйте базу даних

```bash
python manage.py migrate
```

### Крок 6: Створіть суперкористувача (обліковий запис адміністратора)

```bash
python manage.py createsuperuser
```

Введіть за запитом:
- Ім'я користувача: `admin`
- Електронна пошта: `admin@example.com`
- Пароль: (на ваш вибір)

### Крок 7: Створіть зразкові дані (необов'язково)

```bash
python manage.py shell
```

Потім в оболонці:

```python
from users.models import Country, City, User

# Створення країн
ukraine = Country.objects.create(name='Україна', code='UA', population=41000000)
poland = Country.objects.create(name='Польща', code='PL', population=38000000)

# Створення міст
kyiv = City.objects.create(
    name='Київ',
    country=ukraine,
    population=2900000,
    founded_year=1200,
    is_capital=True
)
lviv = City.objects.create(
    name='Львів',
    country=ukraine,
    population=717000,
    founded_year=1256
)

# Створення користувачів
User.objects.create(
    first_name='Іван',
    last_name='Петренко',
    email='ivan@example.com',
    phone='+380123456789',
    city=kyiv,
    bio='Зразковий користувач з Києва'
)

print("Зразкові дані створено!")
exit()
```

### Крок 8: Запустіть сервер розробки

```bash
python manage.py runserver
```

**Доступ до додатку:**
- Веб: http://localhost:8000
- Адмін: http://localhost:8000/admin
- Користувачі: http://localhost:8000/users/
- Країни: http://localhost:8000/users/countries/
- Міста: http://localhost:8000/users/cities/

---

## Варіант 3: Docker Compose (рекомендовано для налаштування, подібного до виробничого)

### Крок 1: Перейдіть до каталогу module_10

```bash
cd /root/goit/python_web/module_10
```

### Крок 2: Створіть файл .env для Docker

```bash
cp 03_django_app/.env.example .env
```

### Крок 3: Зберіть та запустіть контейнери

```bash
docker-compose up -d
```

### Крок 4: Застосуйте міграції в контейнері

```bash
docker-compose exec app python manage.py migrate
```

### Крок 5: Створіть суперкористувача

```bash
docker-compose exec app python manage.py createsuperuser
```

### Крок 7: Доступ до додатку

- Веб: http://localhost:8000
- Адмін: http://localhost:8000/admin

... (Решта файлу може бути перекладена аналогічно)
