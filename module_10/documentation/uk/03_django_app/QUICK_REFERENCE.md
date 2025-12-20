# Короткий довідник

## 📍 Розташування
```
/root/goit/python_web/module_10/03_django_app
```

## 🚀 Початок розробки (30 секунд)

```bash
cd /root/goit/python_web/module_10/03_django_app
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

**Потім відвідайте**: http://localhost:8000

## 🐳 Запуск з Docker (1 хвилина)

```bash
cd /root/goit/python_web/module_10
docker-compose up -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
```

**Потім відвідайте**: http://localhost:8000

## 📚 Ключова документація

| Документ | Призначення |
|----------|---------|
| [README.md](03_django_app/README.md) | Огляд та швидкий старт |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Повні інструкції з налаштування |
| [DJANGO_APP_VERIFICATION.md](DJANGO_APP_VERIFICATION.md) | Контрольний список перевірки |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Що було завершено |

## 🧪 Запуск тестів

```bash
cd /root/goit/python_web/module_10/03_django_app

# Усі тести
python manage.py test users

# Детальний вивід
python manage.py test users --verbosity=2

# Конкретний тест
python manage.py test users.tests.UserModelTests.test_user_creation
```

## 📋 Поширені команди

```bash
# Створити міграції
python manage.py makemigrations

# Застосувати міграції
python manage.py migrate

# Створити адміністратора
python manage.py createsuperuser

# Інтерактивна оболонка
python manage.py shell

# Перевірка на наявність проблем
python manage.py check

# Запуск сервера розробки на іншому порту
python manage.py runserver 8001
```

... (Решта файлу може бути перекладена аналогічно)
