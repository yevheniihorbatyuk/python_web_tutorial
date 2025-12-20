# Урок 5: Django Views & URLs

## Вступ: Поєднання URL-адрес з логікою

**View (Представлення)** — це функція або клас Python, який приймає веб-запит і повертає веб-відповідь. **URL** зіставляє певний шлях URL з представленням.

**Цикл запит-відповідь:**
1.  Користувач переходить за URL-адресою (наприклад, `/quotes/`).
2.  Диспетчер URL-адрес Django перевіряє ваші файли `urls.py`, щоб знайти відповідний шаблон.
3.  Викликається відповідна функція представлення, отримуючи деталі запиту.
4.  Представлення виконує певну логіку (наприклад, отримує дані з бази даних).
5.  Представлення повертає відповідь, часто шляхом рендерингу HTML-шаблону.

---

## Частина 1: Представлення на основі функцій (FBV)

FBV — це проста функція Python, яка приймає `request` як свій перший аргумент.

```python
# quotes/views.py
from django.shortcuts import render
from .models import Quote

def quote_list(request):
    """Представлення для відображення всіх цитат."""
    quotes = Quote.objects.all()
    context = {'quotes': quotes}
    return render(request, 'quotes/quote_list.html', context)
```
- `render()`: функція-скорочення, яка поєднує шаблон зі словником контексту та повертає об'єкт `HttpResponse`.

---

## Частина 2: Маршрутизація URL-адрес

Вам потрібно зіставити URL-адресу з вашим представленням. Це робиться в `urls.py`.

1.  **Проєктний `urls.py` (`config/urls.py`)**: це кореневий URLconf. Найкраще включити URL-адреси з вашого додатку.
    ```python
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('quotes.urls')), # Включити URL-адреси вашого додатку
    ]
    ```

2.  **Додатковий `urls.py` (`quotes/urls.py`)**: створіть цей файл для зберігання URL-адрес, специфічних для вашого додатку.
    ```python
    from django.urls import path
    from . import views

    app_name = 'quotes' # Простір імен для URL-адрес

    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
        # Приклад з параметром:
        # path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    ]
    ```
- `name='quote_list'`: іменування вашої URL-адреси дозволяє однозначно посилатися на неї з інших місць у Django, особливо з шаблонів.

---

## Частина 3: Динамічні URL-адреси

Часто вам потрібні URL-адреси, які захоплюють значення зі шляху.

```python
# quotes/urls.py
path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),

# quotes/views.py
from django.shortcuts import get_object_or_404

def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    return render(request, 'quotes/quote_detail.html', {'quote': quote})
```
- `<int:quote_id>`: це конвертер шляху. Він відповідає цілому числу та передає його значення до представлення як аргумент `quote_id`.
- `get_object_or_404()`: поширене скорочення для отримання об'єкта або виклику помилки 404 (Не знайдено), якщо він не існує.

---

## Частина 4: Представлення на основі класів (CBV)

Для поширених шаблонів, таких як відображення списку об'єктів або сторінки деталей, Django надає загальні **представлення на основі класів**. Вони позбавляють вас від написання повторюваного коду.

### `ListView`

Відображає список об'єктів.

```python
# quotes/views.py
from django.views.generic import ListView
from .models import Quote

class QuoteListView(ListView):
    model = Quote
    template_name = 'quotes/quote_list.html' # Необов'язково, за замовчуванням quotes/quote_list.html
    context_object_name = 'quotes'           # Назва списку в контексті шаблону
    paginate_by = 10                         # Необов'язково: увімкнути пагінацію
```

### `DetailView`

Відображає один об'єкт.

```python
# quotes/views.py
from django.views.generic import DetailView

class QuoteDetailView(DetailView):
    model = Quote
    template_name = 'quotes/quote_detail.html'
    context_object_name = 'quote'
```

### Використання CBV в `urls.py`

Ви повинні викликати метод `.as_view()`.

```python
# quotes/urls.py
from .views import QuoteListView, QuoteDetailView

urlpatterns = [
    path('', QuoteListView.as_view(), name='quote_list'),
    path('quote/<int:pk>/', QuoteDetailView.as_view(), name='quote_detail'),
]
```
- Зауважте, що `DetailView` за замовчуванням очікує, що захоплений параметр URL буде називатися `pk` (первинний ключ).

---
## Додаткові ресурси

- [Документація Django Views](https://docs.djangoproject.com/en/stable/topics/http/views/)
- [Документація URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [Вбудовані загальні представлення на основі класів](https://docs.djangoproject.com/en/stable/ref/class-based-views/)
