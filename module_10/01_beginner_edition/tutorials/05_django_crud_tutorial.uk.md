# Туторіал: Django Views & URLs

Цей туторіал проведе вас через створення представлень та шаблонів URL для відображення даних з ваших моделей.

**Мета:** Створити сторінку для переліку всіх цитат та сторінку деталей для однієї цитати.

---

## Крок 1: Створення функції представлення

Почнемо з простого представлення на основі функції для відображення списку всіх цитат.

Відкрийте `quotes/views.py` та додайте наступний код:
```python
from django.shortcuts import render
from .models import Quote

def quote_list(request):
    """
    Це представлення отримує всі об'єкти Quote з бази даних
    і передає їх до шаблону.
    """
    quotes = Quote.objects.all()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})
```

---

## Крок 2: Створення шаблону

Представленням Django потрібні шаблони для рендерингу HTML.

1.  Створіть необхідні каталоги:
    ```bash
    mkdir -p quotes/templates/quotes
    ```
2.  Створіть новий файл `quotes/templates/quotes/quote_list.html`:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Цитати</title>
    </head>
    <body>
        <h1>Цитати</h1>
        <ul>
            {% for quote in quotes %}
                <li>
                    "{{ quote.text }}" - <em>{{ quote.author.name }}</em>
                </li>
            {% empty %}
                <li>Цитат не знайдено.</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    ```
    - `{% for quote in quotes %}`: це тег шаблону Django для циклу.
    - `{{ quote.text }}`: це змінна шаблону, яка відображає дані.

---

## Крок 3: Налаштування URL-адрес

Тепер нам потрібно підключити URL до нашого представлення `quote_list`.

1.  **Створіть `quotes/urls.py`**:
    ```python
    from django.urls import path
    from . import views

    app_name = 'quotes'

    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
    ]
    ```

2.  **Включіть URL-адреси додатка до `urls.py` основного проєкту**:
    ```python
    # config/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('quotes.urls')),
    ]
    ```

---

## Крок 4: Тестування вашого списку

1.  **Запустіть сервер розробки:**
    ```bash
    python manage.py runserver
    ```
2.  **Відкрийте браузер** і перейдіть за адресою `http://127.0.0.1:8000/`.

Ви повинні побачити сторінку зі списком усіх цитат, які є у вашій базі даних.

---

## Крок 5: Створення представлення та URL для деталей

Створімо сторінку для відображення деталей однієї цитати.

1.  **Додайте представлення деталей до `quotes/views.py`**:
    ```python
    from django.shortcuts import get_object_or_404

    def quote_detail(request, quote_id):
        quote = get_object_or_404(Quote, pk=quote_id)
        return render(request, 'quotes/quote_detail.html', {'quote': quote})
    ```

2.  **Додайте шаблон URL до `quotes/urls.py`**:
    ```python
    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
        path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    ]
    ```

3.  **Створіть шаблон деталей `quotes/templates/quotes/quote_detail.html`**:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Деталі цитати</title>
    </head>
    <body>
        <h1>Цитата</h1>
        <blockquote>
            <p>"{{ quote.text }}"</p>
            <footer>- {{ quote.author.name }}</footer>
        </blockquote>
        
        <strong>Теги:</strong>
        <ul>
        {% for tag in quote.tags.all %}
            <li>{{ tag.name }}</li>
        {% endfor %}
        </ul>

        <a href="{% url 'quotes:quote_list' %}">Назад до списку</a>
    </body>
    </html>
    ```
    - `{% url 'quotes:quote_list' %}`: цей тег шаблону генерує URL-адресу, реверсуючи ім'я URL, що є більш надійним, ніж жорстке кодування URL-адрес.

4.  **Оновіть шаблон списку**, щоб посилатися на сторінку деталей:
    ```html
    <!-- Всередині циклу for у quote_list.html -->
    <li>
        <a href="{% url 'quotes:quote_detail' quote.id %}">
            "{{ quote.text }}"
        </a> - <em>{{ quote.author.name }}</em>
    </li>
    ```

Тепер поверніться на сторінку списку цитат, і ви зможете натискати на кожну цитату, щоб побачити її сторінку деталей.
