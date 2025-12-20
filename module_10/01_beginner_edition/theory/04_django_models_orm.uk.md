# Урок 4: Моделі Django та ORM

## Вступ: Бази даних без SQL

**Object-Relational Mapper (ORM)** — одна з найпотужніших функцій Django. Вона дозволяє вам взаємодіяти з вашою базою даних, наприклад, робити запити та маніпулювати даними, використовуючи код Python замість написання SQL.

- **Модель**: клас Python, який представляє таблицю у вашій базі даних.
- **Поле**: атрибут моделі, який представляє колонку в таблиці.
- **QuerySet**: колекція об'єктів з вашої бази даних.

---

## Частина 1: Визначення моделей

Модель — це клас, який успадковується від `django.db.models.Model`.

```python
# quotes/models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    born_date = models.CharField(max_length=50)

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

### Поширені типи полів

- `CharField`: для коротких рядків. `max_length` є обов'язковим.
- `TextField`: для довгих рядків.
- `IntegerField`, `FloatField`: для чисел.
- `BooleanField`: для значень true/false.
- `DateTimeField`, `DateField`: для дат і часу.
- `EmailField`, `URLField`: для валідованих рядків.

### Опції полів

- `max_length`: максимальна довжина для `CharField`.
- `unique=True`: гарантує, що всі значення в цій колонці є унікальними.
- `blank=True`: дозволяє полю бути порожнім у формах.
- `null=True`: дозволяє базі даних зберігати значення `NULL`.
- `default`: значення за замовчуванням для поля.

---

## Частина 2: Відносини

Django може визначати три основні типи відносин у базі даних.

### `ForeignKey` (багато-до-одного)

Використовується, коли один екземпляр моделі пов'язаний з багатьма екземплярами іншої моделі. У нашому прикладі один `Author` може мати багато `Quotes`.

```python
author = models.ForeignKey(Author, on_delete=models.CASCADE)
```
- `on_delete=models.CASCADE`: якщо автора буде видалено, всі його цитати також будуть видалені.

### `ManyToManyField` (багато-до-багатьох)

Використовується, коли екземпляр однієї моделі може бути пов'язаний з багатьма екземплярами іншої, і навпаки. Наприклад, `Quote` може мати багато `Tags`, а `Tag` може бути на багатьох `Quotes`.

```python
tags = models.ManyToManyField(Tag)
```

### `OneToOneField` (один-до-одного)

Використовується, коли екземпляр однієї моделі пов'язаний рівно з одним екземпляром іншої. Наприклад, `User` може мати один `Profile`.

---

## Частина 3: Запити до даних за допомогою ORM

Коли у вас є моделі, ви можете використовувати ORM для запитів до вашої бази даних.

### Отримання об'єктів

- **`all()`**: отримати всі об'єкти.
  ```python
  all_quotes = Quote.objects.all()
  ```
- **`get()`**: отримати один об'єкт. Викликає помилку, якщо об'єкт не знайдено або знайдено декілька.
  ```python
  one_author = Author.objects.get(pk=1)
  ```
- **`filter()`**: отримати `QuerySet` об'єктів, що відповідають параметрам пошуку.
  ```python
  einstein_quotes = Quote.objects.filter(author__name='Albert Einstein')
  ```
- **`exclude()`**: отримати `QuerySet` об'єктів, що *не* відповідають параметрам.

### Пошукові запити до полів

При використанні `filter()` ви можете використовувати пошукові запити для визначення типу порівняння.
- `__exact`: точна відповідність (за замовчуванням).
- `__iexact`: відповідність без урахування регістру.
- `__contains`: перевірка наявності підрядка з урахуванням регістру.
- `__icontains`: без урахування регістру.
- `__gt`, `__gte`, `__lt`, `__lte`: більше, більше або дорівнює, і т.д.
- `__in`: у заданому списку.

```python
# Знайти авторів, чиї імена починаються на 'А'
authors = Author.objects.filter(name__startswith='A')
```

### Охоплення відносин

Для запитів через відносини використовуйте подвійне підкреслення (`__`).
```python
# Знайти всі цитати авторів, народжених в 'Ульмі, Німеччина'
quotes = Quote.objects.filter(author__born_location='Ulm, Germany')
```

---
## Додаткові ресурси

- [Документація моделей Django](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Довідник API QuerySet](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Довідник типів полів](https://docs.djangoproject.com/en/stable/ref/models/fields/)
