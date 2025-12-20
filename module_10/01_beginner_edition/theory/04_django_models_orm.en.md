# Lesson 4: Django Models & ORM

## Introduction: Databases Without SQL

The **Object-Relational Mapper (ORM)** is one of Django's most powerful features. It allows you to interact with your database, like querying and manipulating data, using Python code instead of writing SQL.

- **Model**: A Python class that represents a table in your database.
- **Field**: An attribute on a model that represents a column in the table.
- **QuerySet**: A collection of objects from your database.

---

## Part 1: Defining Models

A model is a class that inherits from `django.db.models.Model`.

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

### Common Field Types

- `CharField`: For short strings. `max_length` is required.
- `TextField`: For long strings.
- `IntegerField`, `FloatField`: For numbers.
- `BooleanField`: For true/false values.
- `DateTimeField`, `DateField`: For dates and times.
- `EmailField`, `URLField`: For validated strings.

### Field Options

- `max_length`: The maximum length for `CharField`.
- `unique=True`: Ensures all values in this column are unique.
- `blank=True`: Allows the field to be blank in forms.
- `null=True`: Allows the database to store a `NULL` value.
- `default`: A default value for the field.

---

## Part 2: Relationships

Django can define the three major types of database relationships.

### `ForeignKey` (Many-to-One)

Used when one model instance is related to many instances of another model. In our example, one `Author` can have many `Quotes`.

```python
author = models.ForeignKey(Author, on_delete=models.CASCADE)
```
- `on_delete=models.CASCADE`: If an author is deleted, all their quotes will be deleted too.

### `ManyToManyField` (Many-to-Many)

Used when an instance of one model can be related to many instances of another, and vice-versa. For example, a `Quote` can have many `Tags`, and a `Tag` can be on many `Quotes`.

```python
tags = models.ManyToManyField(Tag)
```

### `OneToOneField` (One-to-One)

Used when an instance of one model is related to exactly one instance of another. For example, a `User` might have one `Profile`.

---

## Part 3: Querying Data with the ORM

Once you have models, you can use the ORM to query your database.

### Retrieving Objects

- **`all()`**: Get all objects.
  ```python
  all_quotes = Quote.objects.all()
  ```
- **`get()`**: Get a single object. Throws an error if no object or multiple objects are found.
  ```python
  one_author = Author.objects.get(pk=1)
  ```
- **`filter()`**: Get a `QuerySet` of objects that match the lookup parameters.
  ```python
  einstein_quotes = Quote.objects.filter(author__name='Albert Einstein')
  ```
- **`exclude()`**: Get a `QuerySet` of objects that *do not* match.

### Field Lookups

When using `filter()`, you can use lookups to specify the type of comparison.
- `__exact`: Exact match (default).
- `__iexact`: Case-insensitive match.
- `__contains`: Case-sensitive containment test.
- `__icontains`: Case-insensitive.
- `__gt`, `__gte`, `__lt`, `__lte`: Greater than, greater than or equal to, etc.
- `__in`: In a given list.

```python
# Find authors whose names start with 'A'
authors = Author.objects.filter(name__startswith='A')
```

### Spanning Relationships

To query across relationships, use a double underscore (`__`).
```python
# Find all quotes by authors born in 'Ulm, Germany'
quotes = Quote.objects.filter(author__born_location='Ulm, Germany')
```

---
## Additional Resources

- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [QuerySet API Reference](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Field Types Reference](https://docs.djangoproject.com/en/stable/ref/models/fields/)
