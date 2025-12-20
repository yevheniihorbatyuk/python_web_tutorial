# Урок 6: Django Forms & Templates

## Вступ: Взаємодія з користувачем

**Форми** обробляють введення, валідацію та обробку даних користувача. **Шаблони** відповідають за рендеринг HTML, який бачить користувач. Разом вони дозволяють створювати інтерактивні веб-сторінки.

---

## Частина 1: Django Forms

Обробка форм у Django використовує класи `Form`.

### `ModelForm`

`ModelForm` — це допоміжний клас, який дозволяє створити клас `Form` з моделі Django. Це значно економить час при створенні форм, які безпосередньо відповідають моделям бази даних.

```python
# quotes/forms.py
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
```
- `model`: модель, на якій базується форма.
- `fields`: поля з моделі, які потрібно включити до форми.

### Використання форми у представленні

Ось як використовувати `Form` у представленні для обробки як відображення форми (запит `GET`), так і обробки надісланих даних (запит `POST`).

```python
# quotes/views.py
from .forms import QuoteForm

def add_quote(request):
    if request.method == 'POST':
        # Створити екземпляр форми та заповнити його даними із запиту
        form = QuoteForm(request.POST)
        # Перевірити, чи є форма валідною
        if form.is_valid():
            form.save() # Зберегти нову цитату в базу даних
            return redirect('quotes:quote_list')
    else:
        # Якщо це GET-запит, створити порожню форму
        form = QuoteForm()
        
    return render(request, 'quotes/add_quote.html', {'form': form})
```

### Валідація форми

Валідація для `ModelForm` є автоматичною на основі визначення вашої моделі (наприклад, `max_length`). Ви також можете додати власні методи валідації до вашого класу форми.

```python
class MyForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        """Власний метод валідації для конкретного поля."""
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Ім'я повинно містити принаймні 3 символи.")
        return name
```

---

## Частина 2: Django Templates

Шаблони — це текстові файли, які можуть генерувати будь-який текстовий формат (HTML, XML, CSV).

### Синтаксис шаблонів

- **`{{ variable }}`**: змінні замінюються їхніми значеннями з контексту.
- **`{% tag %}`**: теги забезпечують логіку, таку як цикли або умовні оператори.

### Успадкування шаблонів

Це потужна функція, яка дозволяє створити базовий "скелетний" шаблон, що містить усі загальні елементи вашого сайту та визначає **блоки**, які дочірні шаблони можуть перевизначати.

**`base.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Мій сайт{% endblock %}</title>
</head>
<body>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**`quote_list.html`**
```html
{% extends "base.html" %}

{% block title %}Список цитат{% endblock %}

{% block content %}
    <h1>Цитати</h1>
    ...
{% endblock %}
```

### Рендеринг форми в шаблоні

```html
<form method="post">
    {% csrf_token %}  <!-- Важливо для безпеки! -->
    
    {{ form.as_p }}   <!-- Рендерити поля форми як теги <p> -->
    
    <button type="submit">Зберегти</button>
</form>
```
- `{% csrf_token %}`: захищає від атак міжсайтової підробки запитів. **Завжди** включайте його у форми, що використовують `POST`.

### Фільтри шаблонів

Фільтри змінюють змінні для відображення.
- `{{ quote.text|truncatewords:10 }}`: обрізає текст.
- `{{ quote.created_at|date:"F j, Y" }}`: форматує дату.
- `{{ author.name|upper }}`: перетворює у верхній регістр.

---
## Додаткові ресурси

- [Документація Django Forms](https://docs.djangoproject.com/en/stable/topics/forms/)
- [Мова шаблонів Django](https://docs.djangoproject.com/en/stable/ref/templates/language/)
- [Вбудовані теги та фільтри шаблонів](https://docs.djangoproject.com/en/stable/ref/templates/builtins/)
