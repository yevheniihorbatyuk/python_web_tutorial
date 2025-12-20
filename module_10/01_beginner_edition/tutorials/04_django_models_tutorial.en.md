# Tutorial: Django Models & ORM

This tutorial will guide you through creating and interacting with Django models.

**Goal:** Define models, create database tables via migrations, and use the Django ORM to perform basic CRUD (Create, Read, Update, Delete) operations.

---

## Step 1: Define Your Models

Open `quotes/models.py` and ensure it contains the models for `Author`, `Tag`, and `Quote`.

```python
# quotes/models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    # ... other fields

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
```

---

## Step 2: Create and Apply Migrations

1.  **Generate the migration file.** Django inspects your models and creates a migration plan.
    ```bash
    python manage.py makemigrations
    ```
    You should see a new file created in `quotes/migrations/`.

2.  **Apply the migration.** This command runs the migration and creates the tables in your database.
    ```bash
    python manage.py migrate
    ```

---

## Step 3: Interact with Models via the Django Shell

The Django shell is an interactive console where you can run Python code within the context of your project.

1.  **Start the shell:**
    ```bash
    python manage.py shell
    ```

2.  **Import your models:**
    ```python
    from quotes.models import Author, Tag, Quote
    ```

---

## Step 4: CRUD Operations in the Shell

### Create (C)

```python
# Create an author
author = Author.objects.create(name='Albert Einstein', born_date='March 14, 1879')

# Create some tags
tag1 = Tag.objects.create(name='science')
tag2 = Tag.objects.create(name='philosophy')

# Create a quote and link it to the author
quote = Quote.objects.create(
    text='The world as we have created it is a process of our thinking.',
    author=author
)

# Add tags to the quote
quote.tags.add(tag1, tag2)
```

### Read (R)

```python
# Get all authors
authors = Author.objects.all()
print(authors)

# Get a single author by name
einstein = Author.objects.get(name='Albert Einstein')
print(einstein.born_date)

# Filter quotes by author
einstein_quotes = Quote.objects.filter(author=einstein)
# Or more powerfully:
einstein_quotes = Quote.objects.filter(author__name='Albert Einstein')
print(einstein_quotes)

# Get quotes that have a specific tag
science_quotes = Quote.objects.filter(tags__name='science')
print(science_quotes)
```

### Update (U)

```python
# Get the author object
author_to_update = Author.objects.get(name='Albert Einstein')

# Change a field and save
author_to_update.born_location = 'Ulm, Germany'
author_to_update.save()

print(author_to_update.born_location)
```

### Delete (D)

```python
# Get an object and delete it
tag_to_delete = Tag.objects.get(name='philosophy')
tag_to_delete.delete()

# Verify it's gone
Tag.objects.all()
```

---

## Step 5: Register Models in the Admin

To manage your data through a web interface, register your models in `quotes/admin.py`.

```python
from django.contrib import admin
from .models import Author, Tag, Quote

admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Quote)
```

Now, run the server (`python manage.py runserver`), go to the admin panel (`/admin/`), and you will be able to perform CRUD operations visually.
