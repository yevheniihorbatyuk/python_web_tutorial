# Tutorial: Setting Up a Django Project

This tutorial will walk you through the initial setup of a Django project from scratch.

**Goal:** Create a new Django project and an app, configure the settings, and run the development server.

---

## Step 1: Install Django

If you haven't already, install Django using pip.
```bash
pip install Django
```

---

## Step 2: Create the Project and App

1.  **Create a project folder** and navigate into it.
    ```bash
    mkdir my_django_project && cd my_django_project
    ```

2.  **Create a new Django project.** The `.` at the end tells Django to create the project in the current directory.
    ```bash
    django-admin startproject config .
    ```

3.  **Create a new app.** We'll call our app `quotes`.
    ```bash
    python manage.py startapp quotes
    ```

Your directory should now look like this:
```
my_django_project/
├── config/
├── quotes/
└── manage.py
```

---

## Step 3: Configure `settings.py`

You need to tell Django about your new app.

1.  Open `config/settings.py`.
2.  Find the `INSTALLED_APPS` list.
3.  Add your `quotes` app to the list.

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quotes.apps.QuotesConfig', # Or simply 'quotes'
]
```

---

## Step 4: Run the Development Server

Let's make sure everything is working.
```bash
python manage.py runserver
```
You should see output similar to this:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
Open your web browser and navigate to `http://127.0.0.1:8000/`. You should see the default Django welcome page.

---

## Step 5: Apply Initial Migrations

Django comes with built-in apps (like `admin` and `auth`) that need their own database tables. Let's create them.

Stop the server (Ctrl+C) and run:
```bash
python manage.py migrate
```
This command creates the initial database (an `db.sqlite3` file) and sets up the necessary tables for Django's core features.

---

## Step 6: Create a Superuser

To access the admin panel, you need an admin account.
```bash
python manage.py createsuperuser
```
Follow the prompts to create a username and password.

---

## Step 7: Explore the Admin Panel

1.  **Start the server again**:
    ```bash
    python manage.py runserver
    ```
2.  **Navigate to the admin URL**: `http://127.0.0.1:8000/admin/`
3.  **Log in** with the superuser credentials you just created.

You are now in the Django administration panel. It's mostly empty right now, but as you add models to your `quotes` app, you will be able to manage them from here.

Congratulations! You have successfully set up a Django project. The next step is to define your models.
