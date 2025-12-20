# Module 10: Django Web Applications

Welcome to Module 10, a comprehensive module for building and understanding web applications with Django.

This module contains several projects and extensive documentation to guide you through the learning process.

## 🚀 Quick Start

The primary application in this module is `03_django_app`. To get it running quickly with Docker:

```bash
# Navigate to the module root
cd python_web/module_10

# Build and start the Docker containers
docker-compose up -d --build

# Apply database migrations
docker-compose exec app python manage.py migrate

# Create a superuser to access the admin panel
docker-compose exec app python manage.py createsuperuser
```

Once done, the application will be available at **[http://localhost:8000](http://localhost:8000)**.

## 📚 Documentation

All documentation, including detailed setup guides, tutorials, and project deep-dives, has been organized into a central `documentation` directory.

The documentation is available in two languages:

*   **[Browse English Documentation](./documentation/en/)**
*   **[Переглянути українську документацію](./documentation/uk/)**

Inside, you will find detailed information for each project within this module.

## 📁 Module Structure

*   `03_django_app/`: A complete Django application for managing Users, Cities, and Countries. This is the main project for this module.
*   `04_event_hub/`: A more advanced, API-driven event management platform built with Django Rest Framework.
*   `documentation/`: The central hub for all documentation, tutorials, and guides.
*   `docker-compose.yml`: Defines the services, networks, and volumes for the Dockerized environment (Django app, PostgreSQL, Redis).
*   `requirements.txt`: A list of all Python dependencies for the projects in this module.

---
For detailed instructions, please refer to the documentation. Happy coding!
