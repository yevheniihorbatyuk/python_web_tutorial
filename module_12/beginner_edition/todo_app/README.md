# Todo App - Simple FastAPI Application

A beginner-friendly FastAPI application demonstrating CRUD operations with JWT authentication.

## 📋 Features

- User registration and JWT authentication
- Create, read, update, delete todos
- Filter todos by completion status
- User-specific todo lists
- PostgreSQL database with async SQLAlchemy
- Docker Compose deployment

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- or Python 3.11+ and PostgreSQL

### Option 1: Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# Wait for database to be ready (about 10 seconds)
sleep 10

# The app will be available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database URL
export DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Run the application
uvicorn app.main:app --reload
```

## 📚 API Documentation

Once running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## 🔐 Authentication

### Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "securepassword123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "securepassword123"
  }'
```

This returns:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📝 Todo Operations

All todo endpoints require authentication. Use the `access_token` from login in the `Authorization` header.

### List Todos

```bash
# Get all todos
curl http://localhost:8000/todos \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only completed todos
curl "http://localhost:8000/todos?completed=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only incomplete todos
curl "http://localhost:8000/todos?completed=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create a Todo

```bash
curl -X POST http://localhost:8000/todos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete the Todo API tutorial",
    "due_date": "2025-02-01T00:00:00"
  }'
```

### Get a Specific Todo

```bash
curl http://localhost:8000/todos/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update a Todo

```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI (updated)",
    "completed": false
  }'
```

### Mark Todo as Complete

```bash
curl -X PATCH http://localhost:8000/todos/1/complete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete a Todo

```bash
curl -X DELETE http://localhost:8000/todos/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

## 📁 Project Structure

```
todo_app/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic schemas for validation
│   ├── database.py       # Database configuration
│   └── auth.py           # JWT and password utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # pytest fixtures
│   ├── test_auth.py      # Authentication tests
│   └── test_todos.py     # Todo CRUD tests
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md            # This file
```

## 🔑 Key Concepts

### JWT Authentication
- Access tokens expire after 24 hours
- JWT secret key is stored in `JWT_SECRET_KEY` environment variable
- Passwords are hashed using bcrypt

### Database Models
- **User**: Stores user account information
- **Todo**: Stores todo items with owner reference

### API Patterns
- RESTful endpoint design
- Proper HTTP status codes (201 for creation, 404 for not found, etc.)
- Request/response validation with Pydantic
- Async/await for non-blocking I/O

## 🛠️ Troubleshooting

### Connection refused to postgres

Make sure the database container is running and healthy:
```bash
docker-compose ps
docker-compose logs postgres
```

### Port already in use

If port 8000 or 5432 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change external port from 8000 to 8001
```

## 📖 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

## 📝 License

This is an educational project.
