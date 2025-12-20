"""
Урок 3: Посібник з налаштування Django

Цей файл слугує довідником для початкового налаштування Django проєкту.
Замість того, щоб бути виконуваним скриптом, він містить текстові блоки
з інструкціями та прикладами коду, які ви можете копіювати та використовувати.
"""

def show_project_structure():
    """Відображає типову структуру Django проєкту."""
    structure = """
my_project/
├── manage.py                   # Утиліта для керування проєктом
├── config/                     # Папка конфігурації проєкту
│   ├── settings.py             # Головний файл налаштувань
│   └── urls.py                 # Головний файл URL-маршрутів
└── my_app/                     # Ваш додаток
    ├── migrations/             # Файли міграцій бази даних
    ├── models.py               # Моделі (структура БД)
    ├── views.py                # Представлення (логіка)
    ├── admin.py                # Налаштування адмін-панелі
    ├── apps.py                 # Конфігурація додатку
    └── tests.py                # Тести
"""
    print("--- Django Project Structure ---")
    print(structure)

def show_install_commands():
    """Відображає команди для встановлення та створення проєкту."""
    commands = """
# 1. Встановлення Django
pip install Django

# 2. Створення проєкту (де 'config' - папка налаштувань)
django-admin startproject config .

# 3. Створення додатку
python manage.py startapp my_app
"""
    print("--- Installation and Setup Commands ---")
    print(commands)

if __name__ == '__main__':
    show_install_commands()
    show_project_structure()
