# User Management Django Application

**Complete working Django application demonstrating Module 10 concepts**

## 🚀 Quick Start

### Setup & Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Create database and run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Enter: username, email, password

# Run development server
python manage.py runserver
```

**Access the application:**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin

### With Docker

```bash
cd ..
docker-compose up -d
docker-compose exec app bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## 📁 Project Structure

```
django_app/
├── manage.py                    # Django CLI tool
├── config/                      # Project configuration
│   ├── settings.py             # Database, apps, middleware
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # Production server
│   └── asgi.py                 # Async server
├── users/                      # Users app
│   ├── models.py               # Country, City, User models
│   ├── views.py                # CRUD views
│   ├── forms.py                # ModelForms with validation
│   ├── urls.py                 # App URLs
│   ├── admin.py                # Admin customization
│   └── templates/users/        # HTML templates
├── templates/                  # Project-wide templates
│   ├── base.html               # Bootstrap base template
│   └── home.html               # Home page
├── static/                     # Static files
│   ├── css/style.css
│   └── js/main.js
└── README.md                   # This file
```

## 🎯 Features Demonstrated

### Models (Lesson 4)
- **Country**: name, code, population
- **City**: name, country (ForeignKey), population, is_capital
- **User**: first_name, last_name, email, phone, city, bio, is_active

### Views (Lesson 5)
- ListView with filtering and pagination
- DetailView with related objects
- CreateView with form validation
- UpdateView with pre-population
- DeleteView with confirmation

### Forms (Lesson 6)
- ModelForm with custom validation
- Field-level and form-level validation
- Bootstrap styling
- Error messages

### Templates (Lesson 6)
- Base template with Bootstrap
- List templates with tables and pagination
- Detail templates with information display
- Form templates with validation errors
- Delete confirmation pages

## 🔧 Management Commands

```bash
python manage.py migrate           # Apply migrations
python manage.py makemigrations    # Create migrations
python manage.py createsuperuser   # Create admin user
python manage.py runserver         # Start dev server
python manage.py shell             # Interactive shell
python manage.py test              # Run tests
```

## 🌐 URL Patterns

```
/                    Home
/admin/              Django admin
/users/              User list
/users/1/            User detail
/users/create/       Create user
/users/1/edit/       Edit user
/users/1/delete/     Delete user
/users/cities/       City list
/users/countries/    Country list
```

## 📖 Learn More

See lesson files in `../beginner_edition/` for detailed explanations.

---

**This is a production-ready Django application!** 🚀
