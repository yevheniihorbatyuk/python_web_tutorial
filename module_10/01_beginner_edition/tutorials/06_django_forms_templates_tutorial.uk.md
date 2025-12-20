# Туторіал: Django Forms & Templates

Цей туторіал проведе вас через створення форми для додавання нових цитат і шаблонів, необхідних для її відображення.

**Мета:** Створити сторінку з формою для додавання нових цитат та інтегрувати її в проєкт.

---

## Крок 1: Створення класу форми

Спочатку нам потрібно створити `ModelForm` для нашої моделі `Quote`.

Створіть новий файл `quotes/forms.py` та додайте наступне:
```python
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
        # Додаємо віджети для застосування класів Bootstrap до полів форми
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
```

---

## Крок 2: Створення представлення

Тепер створіть представлення для обробки форми.

Відкрийте `quotes/views.py` та додайте представлення `add_quote`:
```python
from django.shortcuts import render, redirect
from .forms import QuoteForm

# ... (ваші існуючі представлення) ...

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

---

## Крок 3: Додавання URL-адреси

Додайте шаблон URL для нового представлення в `quotes/urls.py`:
```python
urlpatterns = [
    path('', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('add/', views.add_quote, name='add_quote'), # <-- Додайте цей рядок
]
```

---

## Крок 4: Створення шаблонів

Нам потрібен базовий шаблон і шаблон для нашої форми.

1.  **Створіть `quotes/templates/quotes/base.html`**:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{% block title %}Додаток цитат{% endblock %}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
                <a class="navbar-brand" href="{% url 'quotes:quote_list' %}">QuoteApp</a>
                <a class="nav-link" href="{% url 'quotes:add_quote' %}">Додати цитату</a>
            </nav>
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    ```

2.  **Створіть `quotes/templates/quotes/add_quote.html`**:
    ```html
    {% extends 'quotes/base.html' %}

    {% block title %}Додати цитату{% endblock %}

    {% block content %}
        <h1 class="mb-4">Додати нову цитату</h1>
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-3">
                <label class="form-label">Текст цитати</label>
                {{ form.text }}
            </div>
            <div class="mb-3">
                <label class="form-label">Автор</label>
                {{ form.author }}
            </div>
            <div class="mb-3">
                <label class="form-label">Теги</label>
                {{ form.tags }}
            </div>
            
            <button type="submit" class="btn btn-primary">Зберегти цитату</button>
        </form>
    {% endblock %}
    ```

3.  **Оновіть `quote_list.html`**, щоб він успадковував базовий шаблон:
    ```html
    {% extends 'quotes/base.html' %}

    {% block title %}Цитати{% endblock %}

    {% block content %}
        <h1>Цитати</h1>
        ... (решта вашого шаблону списку) ...
    {% endblock %}
    ```

---

## Крок 5: Тестування форми

1.  Запустіть сервер: `python manage.py runserver`.
2.  Перейдіть за адресою `http://127.0.0.1:8000/add/`.
3.  Ви повинні побачити форму для додавання нової цитати.
4.  Заповніть форму та надішліть її. У разі успіху вас має перенаправити на список цитат, і ваша нова цитата повинна з'явитися.

Ви успішно створили повний цикл CRUD (Create, Read) для ваших цитат! Ті ж принципи застосовуються для створення функціоналу оновлення та видалення.
