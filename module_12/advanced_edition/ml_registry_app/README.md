# ML Model Registry - Advanced FastAPI Application

A production-style FastAPI application for managing machine learning models with modern authentication and storage integration.

---

## Features

- FastAPI async API with JWT access + refresh tokens
- Role-based access control (user/reviewer/admin)
- SQLAlchemy 2.0 async ORM
- PostgreSQL database
- MinIO (S3-compatible) file storage
- Redis integration
- Alembic migrations
- Docker Compose stack
- pytest test suite

---

## Prerequisites

- Python 3.10+
- Docker and Docker Compose

---

## Quick Start

```bash
cd python_web/module_12/advanced_edition/ml_registry_app
cp .env.example .env

docker-compose up -d
```

Open:
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (minioadmin / minioadmin123)

---

## Verify the API

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login (form-encoded)
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123" | jq -r '.access_token')

# Create model
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Model","framework":"sklearn","task_type":"classification"}'
```

---

## Testing

```bash
pytest tests/ -v
```

---

## Project Structure

```
ml_registry_app/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── api/v1/
│   ├── auth/
│   └── storage/
├── tests/
├── notebooks/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## API Endpoints (High Level)

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

### ML Models
- `GET /api/v1/models/`
- `POST /api/v1/models/`
- `GET /api/v1/models/{id}`
- `PUT /api/v1/models/{id}`
- `DELETE /api/v1/models/{id}`

### Files
- `POST /api/v1/files/upload`
- `GET /api/v1/files/download/{path}`
- `GET /api/v1/files/presigned-url/{path}`
