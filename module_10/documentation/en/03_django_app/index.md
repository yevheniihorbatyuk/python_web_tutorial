# 03_django_app Documentation

This document provides a detailed breakdown of the `03_django_app`, a Django application for managing users, cities, and countries.

## Project Structure

The project is a standard Django application with a single app named `users`.

```
03_django_app/
├── config/             # Django project configuration
│   ├── settings.py     # Project settings
│   └── urls.py         # Main URL configuration
├── users/              # The 'users' application
│   ├── models.py       # Database models (Country, City, User)
│   ├── views.py        # Views for CRUD operations
│   ├── urls.py         # App-specific URLs
│   ├── forms.py        # Forms for creating and updating data
│   └── templates/      # HTML templates
└── manage.py           # Django's command-line utility
```

## Features

The application provides the following features:

*   **CRUD Operations:** Create, Read, Update, and Delete for Users, Cities, and Countries.
*   **Relationships:**
    *   A `User` belongs to a `City`.
    *   A `City` belongs to a `Country`.
*   **User-Friendly Interface:** A simple, template-based interface for interacting with the data.
*   **Search and Filtering:** The ability to search and filter lists of users, cities, and countries.

## Models

### `Country`

*   `name`: The name of the country.
*   `code`: The two-letter country code (e.g., "US").
*   `population`: The population of the country.

### `City`

*   `name`: The name of the city.
*   `country`: A foreign key to the `Country` model.
*   `population`: The population of the city.
*   `founded_year`: The year the city was founded.
*   `is_capital`: A boolean indicating if the city is a capital.

### `User`

*   `first_name`: The user's first name.
*   `last_name`: The user's last name.
*   `email`: The user's email address.
*   `phone`: The user's phone number.
*   `city`: A foreign key to the `City` model.
*   `bio`: A short biography of the user.
*   `is_active`: A boolean indicating if the user is active.

## Views

The application uses class-based views for all CRUD operations.

*   **List Views:** `CountryListView`, `CityListView`, `UserListView`
*   **Detail Views:** `CountryDetailView`, `CityDetailView`, `UserDetailView`
*   **Create Views:** `CountryCreateView`, `CityCreateView`, `UserCreateView`
*   **Update Views:** `CountryUpdateView`, `CityUpdateView`, `UserUpdateView`
*   **Delete Views:** `CountryDeleteView`, `CityDeleteView`, `UserDeleteView`

## URLs

The application's URLs are structured as follows:

*   `/users/`: The main page, which lists all users.
*   `/users/countries/`: Lists all countries.
*   `/users/cities/`: Lists all cities.

Each model has its own set of URLs for CRUD operations (e.g., `/users/create/`, `/users/1/edit/`, `/users/1/delete/`).

## Step-by-Step Tutorial

### 1. Setup

1.  **Clone the repository.**
2.  **Navigate to the `python_web/module_10/03_django_app` directory.**
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a `.env` file** based on the `.env.example` file and fill in the required information.
5.  **Run the database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Start the development server:**
    ```bash
    python manage.py runserver
    ```

### 2. Using the Application

1.  **Navigate to `http://127.0.0.1:8000/users/`** in your web browser.
2.  **You will see a list of users.**
3.  **You can create, edit, and delete users, cities, and countries** by clicking on the appropriate buttons.
4.  **You can also view the details** of each user, city, and country.
5.  **The admin interface** is available at `http://127.0.0.1:8000/admin/`.
