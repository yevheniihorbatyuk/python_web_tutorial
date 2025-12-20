# 🔧 Beginner Edition Code Cleanup & Enhancement

**Working Directory:** `/root/goit/python_web/module_10/01_beginner_edition/`

---

## 📋 ЗАДАЧА 1: Очистити код від print()

### Мета
Видалити всі `print()` вислови з файлів `code/*.py` - залишити тільки робочий код.

### Файли для обробки
```
code/01_beautiful_soup_practice.py
code/02_real_world_scraping.py
code/03_django_setup_guide.py
code/04_django_models.py
code/05_django_crud_views.py
code/06_django_forms.py
```

### Що розуміємо під "очисткою"
- ❌ Видалити: `print(f"...")`, `print("...")` - все що пояснює концепції
- ❌ Видалити: коментарі типу `# This is a comment explaining concept`
- ✅ Залишити: логічні коментарі типу `# Get all users`, `# Filter active users`
- ✅ Залишити: docstrings для функцій/класів
- ✅ Залишити: logging.info(), logging.error() - це виробничі логи
- ✅ Залишити: весь функціональний код

### Приклад "ДО":
```python
def scrape_page(self, url):
    """Scrape a single page."""
    print("Starting scrape...")  # ❌ ВИДАЛИТИ

    # Get HTML from URL using requests library  # ❌ ВИДАЛИТИ
    response = requests.get(url)

    print(f"Status: {response.status_code}")  # ❌ ВИДАЛИТИ
    return response.text
```

### Приклад "ПІСЛЯ":
```python
def scrape_page(self, url):
    """Scrape a single page."""
    response = requests.get(url)
    return response.text
```

### Кроки виконання
1. Прочитати кожен файл в `code/`
2. Видалити всі print() вислови
3. Видалити пояснюючі коментарі
4. Залишити docstrings і важливі коментарі
5. Перевірити, що код все ще робочий
6. Зберегти файли

---

## 📋 ЗАДАЧА 2: Розвинути 03_django_app - Production Ready

### Мета
Зробити `/root/goit/python_web/module_10/03_django_app/` повноцінним, готовим до використання Django проектом.

### Батьківська директорія
```
/root/goit/python_web/module_10/03_django_app/
```

### 2.1 Створити `requirements.txt`

**Розташування:** `/root/goit/python_web/module_10/requirements.txt`

**Вміст:**
```
Django==4.2.8
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pytest==7.4.3
pytest-django==4.7.0
```

### 2.2 Створити `.env.example`

**Розташування:** `/root/goit/python_web/module_10/03_django_app/.env.example`

**Вміст:**
```
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=goit_module10
DB_USER=goit
DB_PASSWORD=goit_password
DB_HOST=localhost
DB_PORT=5432

# OR use SQLite for development
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3
```

### 2.3 Оновити `config/settings.py`

Додати підтримку `.env` файлу:

```python
# В топі файлу, після импортів:
from dotenv import load_dotenv

load_dotenv()

# Замість硬кодованих значень:
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Database configuration з .env
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
```

### 2.4 Додати `docker-compose.yml`

**Розташування:** `/root/goit/python_web/module_10/docker-compose.yml`

**Вміст:**
```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: goit_module10
      POSTGRES_USER: goit
      POSTGRES_PASSWORD: goit_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U goit"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./03_django_app:/app
    ports:
      - "8000:8000"
    environment:
      DEBUG: "True"
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: goit_module10
      DB_USER: goit
      DB_PASSWORD: goit_password
      DB_HOST: postgres
      DB_PORT: 5432
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

### 2.5 Додати `Dockerfile`

**Розташування:** `/root/goit/python_web/module_10/Dockerfile`

**Вміст:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY 03_django_app .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 2.6 Створити `tests.py` для users app

**Розташування:** `/root/goit/python_web/module_10/03_django_app/users/tests.py`

**Вміст:** Базові тести для моделей і views:
- Test Country model creation
- Test City model with ForeignKey
- Test User model with validation
- Test UserListView filtering
- Test UserCreateView form validation
- Test UserDeleteView confirmation

Використовувати `TestCase` з `django.test`.

### 2.7 Оновити `README.md` проекту

**Розташування:** `/root/goit/python_web/module_10/README.md` (новий файл)

**Включити:**
- Overview модулю 10
- Структура каталогів
- Посилання на Beginner & Advanced Edition
- Посилання на 03_django_app
- Інструкції для запуску всього
- Development vs Production setup

---

## 📋 ЗАДАЧА 3: Документація і Посилання

### 3.1 Оновити головний README

Переконатися, що `/root/goit/python_web/module_10/README.md` має:
- ✅ Описання всіх 3 компонентів (Beginner, Advanced, Django App)
- ✅ Структура каталогів
- ✅ Посилання на кожен компонент
- ✅ Quick start інструкції

### 3.2 Додати .gitignore

**Розташування:** `/root/goit/python_web/module_10/.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Django
db.sqlite3
*.log
/media/
/static/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
```

---

## ✅ Чек-лист завдань

### Beginner Edition Code Cleanup
- [ ] code/01_beautiful_soup_practice.py - очищено
- [ ] code/02_real_world_scraping.py - очищено
- [ ] code/03_django_setup_guide.py - очищено
- [ ] code/04_django_models.py - очищено
- [ ] code/05_django_crud_views.py - очищено
- [ ] code/06_django_forms.py - очищено
- [ ] Код протестовано і працює
- [ ] Docstrings збережені
- [ ] Логічні коментарі збережені

### Django App Enhancement
- [ ] requirements.txt створено
- [ ] .env.example створено
- [ ] config/settings.py оновлено (.env support)
- [ ] docker-compose.yml створено
- [ ] Dockerfile створено
- [ ] tests.py написано
- [ ] README.md оновлено
- [ ] .gitignore створено
- [ ] Проект можна запустити без помилок

### Final Verification
- [ ] `python manage.py runserver` - працює
- [ ] `python manage.py migrate` - працює
- [ ] Django admin доступний
- [ ] Усі URL patterns працюють
- [ ] Forms validate правильно

---

## 🚀 Як запустити результат

### Без Docker (Development)
```bash
cd /root/goit/python_web/module_10/03_django_app
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### З Docker
```bash
cd /root/goit/python_web/module_10
docker-compose up -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
# http://localhost:8000
```

---

## 📞 Якщо щось неясно

- Питайте на кожному кроці
- Показуйте код для перевірки
- Просіть рецензію

**Успіхів!** 🎉
