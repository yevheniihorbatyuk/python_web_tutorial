# Посібник: Створення Django-додатку для відображення даних

Ласкаво просимо до посібника по Django! На попередніх уроках ми навчилися збирати дані з веб-сайтів. Тепер настав час створити повноцінний веб-додаток, щоб красиво відобразити ці дані, керувати ними та взаємодіяти з ними.

Ми крок за кроком створимо простий додаток для каталогізації цитат, який буде включати:
- Моделі для зберігання даних в базі.
- Адмін-панель для керування даними.
- Веб-сторінки для відображення цитат (список та детальна сторінка).
- Форми для додавання та редагування цитат.

---

## Крок 1: Створення та налаштування Django-проєкту

Спочатку нам потрібно створити структуру проєкту та налаштувати його.

### 1.1. Встановлення залежностей
Відкрийте термінал і встановіть Django:
```bash
pip install Django
```

### 1.2. Створення проєкту та додатку
```bash
# Створюємо папку для проєкту та переходимо в неї
mkdir quote_app_project && cd quote_app_project

# Створюємо Django-проєкт з основною конфігурацією в папці 'config'
django-admin startproject config .

# Створюємо додаток, де буде наша основна логіка
python manage.py startapp quotes
```

### 1.3. Налаштування проєкту
Відкрийте файл `config/settings.py` і додайте наш новий додаток `quotes` до списку `INSTALLED_APPS`:

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quotes',  # <-- Додайте цей рядок
]
```

---

## Крок 2: Моделі та база даних

Моделі — це Python-класи, які описують структуру нашої бази даних.

### 2.1. Визначення моделей
Відкрийте файл `quotes/models.py` і додайте наступний код:

```python
# quotes/models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    born_date = models.CharField(max_length=50, blank=True)
    born_location = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='quotes')
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f'"{self.text[:50]}..."'
```
- **Author**: Модель для зберігання інформації про авторів.
- **Tag**: Модель для тегів.
- **Quote**: Основна модель для цитат, яка пов'язана з автором (`ForeignKey`) та тегами (`ManyToManyField`).

### 2.2. Створення та застосування міграцій
Міграції — це "версії" вашої схеми бази даних.

```bash
# Створюємо файл міграції на основі змін у models.py
python manage.py makemigrations

# Застосовуємо міграцію до бази даних (створюємо таблиці)
python manage.py migrate
```

---

## Крок 3: Адмін-панель Django

Django надає готову адмін-панель для керування даними.

### 3.1. Реєстрація моделей
Щоб наші моделі з'явилися в адмінці, зареєструємо їх у файлі `quotes/admin.py`:

```python
# quotes/admin.py
from django.contrib import admin
from .models import Author, Tag, Quote

admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Quote)
```

### 3.2. Створення суперкористувача
```bash
python manage.py createsuperuser
```
Введіть логін, email та пароль для адміністратора.

### 3.3. Перевірка адмін-панелі
Запустіть сервер розробки:
```bash
python manage.py runserver
```
Перейдіть за адресою [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/), увійдіть під своїм логіном і переконайтеся, що ви можете додавати, редагувати та видаляти авторів, теги та цитати.

---

## Крок 4: Відображення даних (Views та Templates)

Тепер створимо сторінки, які будуть бачити користувачі.

### 4.1. Налаштування URL-адрес
Спочатку налаштуємо маршрутизацію.

**`config/urls.py` (головний файл URL)**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quotes.urls')), # <-- Підключаємо URL нашого додатку
]
```

**`quotes/urls.py` (створіть цей файл)**
```python
from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    # Головна сторінка зі списком цитат
    path('', views.quote_list, name='quote_list'),
    # Сторінка для додавання нової цитати
    path('add/', views.add_quote, name='add_quote'),
]
```

### 4.2. Створення View-функцій
Views — це функції, які обробляють запити та повертають відповіді (зазвичай, HTML).

**`quotes/views.py`**
```python
from django.shortcuts import render, redirect
from .models import Quote
from .forms import QuoteForm

def quote_list(request):
    quotes = Quote.objects.select_related('author').prefetch_related('tags').all()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:quote_list')
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})
```

### 4.3. Створення форм
Форми в Django допомагають обробляти дані, що надходять від користувача, та валідувати їх.

**`quotes/forms.py` (створіть цей файл)**
```python
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
```

### 4.4. Створення шаблонів (Templates)
Шаблони — це HTML-файли з вкрапленнями логіки Django.

**Створіть наступну структуру папок:**
```
quotes/
└── templates/
    └── quotes/
        ├── base.html
        ├── quote_list.html
        └── add_quote.html
```

**`quotes/templates/quotes/base.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quote App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="{% url 'quotes:quote_list' %}">QuoteApp</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'quotes:add_quote' %}">Add Quote</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

**`quotes/templates/quotes/quote_list.html`**
```html
{% extends 'quotes/base.html' %}

{% block content %}
    <h1 class="mb-4">Quotes</h1>
    {% for quote in quotes %}
        <div class="card mb-3">
            <div class="card-body">
                <p class="card-text">"{{ quote.text }}"</p>
                <footer class="blockquote-footer">{{ quote.author.name }}</footer>
                <div>
                    <strong>Tags:</strong>
                    {% for tag in quote.tags.all %}
                        <span class="badge bg-primary">{{ tag.name }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>
    {% empty %}
        <p>No quotes yet. Be the first to <a href="{% url 'quotes:add_quote' %}">add one</a>!</p>
    {% endfor %}
{% endblock %}
```

**`quotes/templates/quotes/add_quote.html`**
```html
{% extends 'quotes/base.html' %}

{% block content %}
    <h1 class="mb-4">Add a New Quote</h1>
    <form method="post">
        {% csrf_token %}
        <div class="mb-3">
            <label class="form-label">Quote Text</label>
            {{ form.text }}
        </div>
        <div class="mb-3">
            <label class="form-label">Author</label>
            {{ form.author }}
        </div>
        <div class="mb-3">
            <label class="form-label">Tags</label>
            {{ form.tags }}
        </div>
        <button type="submit" class="btn btn-primary">Save Quote</button>
    </form>
{% endblock %}
```

---

## Крок 5: Запуск та перевірка

Запустіть сервер ще раз:
```bash
python manage.py runserver
```
- Перейдіть на [http://127.0.0.1:8000/](http://127.0.0.1:8000/) — ви повинні побачити порожній список цитат.
- Перейдіть на [http://127.0.0.1:8000/add/](http://127.0.0.1:8000/add/) — ви побачите форму для додавання цитати.
- Додайте кілька авторів та тегів через адмін-панель, а потім спробуйте додати цитату через веб-форму.

**Вітаємо! Ви щойно створили свій перший повноцінний веб-додаток на Django!**

## Корисні посилання
- **[Офіційна документація Django](https://docs.djangoproject.com/en/stable/)**: Найкраще джерело інформації.
- **[Django Tutorial (Polls App)](https://docs.djangoproject.com/en/stable/intro/tutorial01/)**: Класичний туторіал від розробників Django.
- **[Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/getting-started/introduction/)**: Для стилізації вашого додатку.
