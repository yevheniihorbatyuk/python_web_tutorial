# Lesson 3: Django Fundamentals

## Introduction: From Data to Web Application

We have scraped data, but it's just sitting in a database. **Django** is a high-level Python web framework that allows us to build a web application to display and manage this data.

### The MVT Architecture

Django uses the **Model-View-Template (MVT)** pattern:
- **Model**: Defines the structure of your data (your database schema). This is what we created in `models.py`.
- **View**: The business logic. It receives web requests, interacts with the Model to get data, and decides what to show the user.
- **Template**: The presentation layer. It's an HTML file with special syntax that displays the data prepared by the View.

---

## Part 1: Project and App Structure

A Django project is a collection of configurations and apps. An **app** is a self-contained module that does something (e.g., a blog, a user management system).

### Creating the Structure

1.  **Install Django**:
    ```bash
    pip install Django
    ```
2.  **Create a project**: This command creates the main project directory and configuration files.
    ```bash
    django-admin startproject myproject .
    ```
3.  **Create an app**: This command creates a directory for your app's logic.
    ```bash
    python manage.py startapp quotes
    ```

---

## Part 2: Settings and Configuration

The `myproject/settings.py` file is the heart of your project's configuration.

### Key Settings

- **`INSTALLED_APPS`**: A list of all apps active in the project. You must add your new app here.
  ```python
  INSTALLED_APPS = [
      ...,
      'quotes', # Add your app
  ]
  ```
- **`DATABASES`**: Configuration for your database connection (e.g., SQLite, PostgreSQL).
- **`STATIC_URL`**: The base URL to serve static files (CSS, JavaScript, images).

---

## Part 3: Models and Migrations

This is the step where you define your data structure.

1.  **Define Models**: In `quotes/models.py`, you create classes that inherit from `django.db.models.Model`. Each class represents a database table, and each attribute represents a column.

2.  **Create Migrations**: Migrations are like version control for your database. After changing your models, you run:
    ```bash
    python manage.py makemigrations
    ```
    This command creates a file that describes the changes to your database schema.

3.  **Apply Migrations**: To apply these changes to the database, you run:
    ```bash
    python manage.py migrate
    ```
    This command executes the migration files and updates your database tables.

---

## Part 4: The Django Admin

Django comes with a built-in admin interface, which is a powerful tool for managing your data.

1.  **Create a Superuser**: To access the admin panel, you need an admin account.
    ```bash
    python manage.py createsuperuser
    ```
2.  **Register Models**: To make your models appear in the admin, you must register them in `quotes/admin.py`.
    ```python
    from django.contrib import admin
    from .models import Author, Quote

    admin.site.register(Author)
    admin.site.register(Quote)
    ```
3.  **Run the Server and Log In**:
    ```bash
    python manage.py runserver
    ```
    Navigate to `http://127.0.0.1:8000/admin/` and log in. You can now add, edit, and delete data directly.

---
## Additional Resources

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django Project Structure](https://docs.djangoproject.com/en/stable/intro/tutorial01/#creating-a-project)
- [Django Migrations](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [The Django Admin Site](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
