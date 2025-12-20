"""
Урок 4: Моделі Django та ORM

Цей файл містить робочі приклади визначення моделей Django.
Ви можете імпортувати ці моделі в Django shell або використовувати їх
у вашому додатку для створення таблиць у базі даних.
"""
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

# Щоб протестувати ці моделі:
# 1. Додайте цей додаток в INSTALLED_APPS у settings.py.
# 2. Запустіть `python manage.py makemigrations`.
# 3. Запустіть `python manage.py migrate`.
# 4. Запустіть `python manage.py shell` і імпортуйте моделі:
#    from your_app.models import Author, Tag, Quote
