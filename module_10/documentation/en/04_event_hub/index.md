# 04_event_hub Documentation

This document provides a detailed breakdown of the `04_event_hub`, a Django Rest Framework application for managing events.

## Project Structure

The project is a multi-app Django project with a focus on providing a RESTful API.

```
04_event_hub/
├── eventhub_config/    # Django project configuration
│   ├── settings.py     # Project settings
│   ├── urls.py         # Main URL configuration
│   └── celery.py       # Celery configuration
├── events/             # Event management app
├── bookings/           # Booking and waitlist management app
├── payments/           # Payment and invoice management app
├── users/              # Custom user model and profile app
├── notifications/      # Notifications, reviews, and certificates app
├── manage.py           # Django's command-line utility
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose configuration
```

## Features

The application provides a comprehensive set of features for an event management platform:

*   **Event Management:** Create, publish, and manage events.
*   **Booking System:** Users can book events, and a waitlist is available for full events.
*   **Payment Processing:** Integration with a payment system (mocked by default) and invoice generation.
*   **User Management:** Custom user model with roles (attendee, organizer, admin) and user profiles.
*   **Notifications:** A system for notifying users of important events.
*   **Reviews and Certificates:** Users can review events and receive certificates.
*   **Asynchronous Tasks:** Celery is used for background tasks like payment processing.
*   **API-First Design:** The entire application is exposed through a RESTful API.
*   **Dockerized:** The application is fully containerized for easy deployment.

## API Endpoints

The API is the primary way to interact with the application. Here's a summary of the available endpoints:

*   `/api/auth/token/`: Obtain a JWT token.
*   `/api/auth/token/refresh/`: Refresh a JWT token.
*   `/api/users/`: Manage users.
*   `/api/events/`: Manage events.
*   `/api/sessions/`: Manage event sessions.
*   `/api/bookings/`: Manage bookings.
*   `/api/waitlist/`: Manage waitlists.
*   `/api/payments/`: Manage payments.
*   `/api/invoices/`: Manage invoices.
*   `/api/notifications/`: Manage notifications.
*   `/api/reviews/`: Manage reviews.
*   `/api/certificates/`: Manage certificates.

For a detailed list of API endpoints and their parameters, please refer to the `API_ENDPOINTS.md` file in the project's root directory.

## Step-by-Step Tutorial

### 1. Setup (with Docker)

1.  **Clone the repository.**
2.  **Navigate to the `python_web/module_10/04_event_hub` directory.**
3.  **Create a `.env` file** based on the `.env.example` file and fill in the required information.
4.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```
5.  **The application will be available at `http://127.0.0.1:8000/`.**

### 2. Using the API

1.  **Obtain a JWT token** by sending a POST request to `/api/auth/token/` with your username and password.
2.  **Include the token** in the `Authorization` header of your requests (e.g., `Authorization: Bearer <token>`).
3.  **You can now interact with the API** by sending requests to the various endpoints.

**Example: Creating an Event**

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d 
    "title": "My Awesome Event",
    "description": "This is a great event.",
    "category": "workshop",
    "location": "Online",
    "is_online": true,
    "start_date": "2025-12-25T18:00:00Z",
    "end_date": "2025-12-25T20:00:00Z",
    "registration_deadline": "2025-12-24T23:59:59Z",
    "max_attendees": 100,
    "price": "25.00"
  \
```
