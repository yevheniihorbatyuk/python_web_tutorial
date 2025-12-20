# Туторіал: Моделі Django та ORM

Цей туторіал проведе вас через створення та взаємодію з моделями Django.

**Мета:** Визначити моделі, створити таблиці бази даних за допомогою міграцій та використовувати Django ORM для виконання основних операцій CRUD (Create, Read, Update, Delete).

---

## Крок 1: Визначення ваших моделей

Відкрийте `quotes/models.py` і переконайтеся, що він містить моделі для `Author`, `Tag` та `Quote`.

```python
# quotes/models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    # ... інші поля

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
```

---

## Крок 2: Створення та застосування міграцій

1.  **Згенеруйте файл міграції.** Django перевіряє ваші моделі та створює план міграції.
    ```bash
    python manage.py makemigrations
    ```
    Ви повинні побачити новий файл, створений у `quotes/migrations/`.

2.  **Застосуйте міграцію.** Ця команда запускає міграцію та створює таблиці у вашій базі даних.
    ```bash
    python manage.py migrate
    ```

---

## Крок 3: Взаємодія з моделями через Django Shell

Django shell — це інтерактивна консоль, де ви можете виконувати код Python у контексті вашого проєкту.

1.  **Запустіть shell:**
    ```bash
    python manage.py shell
    ```

2.  **Імпортуйте ваші моделі:**
    ```python
    from quotes.models import Author, Tag, Quote
    ```

---

## Крок 4: Операції CRUD у Shell

### Створення (Create)

```python
# Створити автора
author = Author.objects.create(name='Альберт Ейнштейн', born_date='14 березня 1879')

# Створити кілька тегів
tag1 = Tag.objects.create(name='наука')
tag2 = Tag.objects.create(name='філософія')

# Створити цитату та пов'язати її з автором
quote = Quote.objects.create(
    text='Світ, яким ми його створили, є процесом нашого мислення.',
    author=author
)

# Додати теги до цитати
quote.tags.add(tag1, tag2)
```

### Читання (Read)

```python
# Отримати всіх авторів
authors = Author.objects.all()
print(authors)

# Отримати одного автора за іменем
einstein = Author.objects.get(name='Альберт Ейнштейн')
print(einstein.born_date)

# Фільтрувати цитати за автором
einstein_quotes = Quote.objects.filter(author=einstein)
# Або більш потужно:
einstein_quotes = Quote.objects.filter(author__name='Альберт Ейнштейн')
print(einstein_quotes)

# Отримати цитати з певним тегом
science_quotes = Quote.objects.filter(tags__name='наука')
print(science_quotes)
```

### Оновлення (Update)

```python
# Отримати об'єкт автора
author_to_update = Author.objects.get(name='Альберт Ейнштейн')

# Змінити поле та зберегти
author_to_update.born_location = 'Ульм, Німеччина'
author_to_update.save()

print(author_to_update.born_location)
```

### Видалення (Delete)

```python
# Отримати об'єкт і видалити його
tag_to_delete = Tag.objects.get(name='філософія')
tag_to_delete.delete()

# Перевірити, що він зник
Tag.objects.all()
```

---

## Крок 5: Реєстрація моделей в адмін-панелі

Щоб керувати даними через веб-інтерфейс, зареєструйте свої моделі в `quotes/admin.py`.

```python
from django.contrib import admin
from .models import Author, Tag, Quote

admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Quote)
```

Тепер запустіть сервер (`python manage.py runserver`), перейдіть до адмін-панелі (`/admin/`), і ви зможете виконувати операції CRUD візуально.
