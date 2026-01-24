# Quick Start - Module 12 FastAPI Apps

Run any application in 5 minutes using Docker Compose.

## Prerequisites

- Docker and Docker Compose
- curl (optional, for testing)

---

## 1) Todo App (Beginner)

```bash
cd python_web/module_12/beginner_edition/todo_app
docker-compose up -d
```

Open: http://localhost:8000/docs

**Health check**
```bash
curl http://localhost:8000/health
```

---

## 2) Blog API (Intermediate)

```bash
cd python_web/module_12/intermediate_edition/blog_api
docker-compose up -d
```

Open: http://localhost:8001/docs

**Health check**
```bash
curl http://localhost:8001/health
```

---

## 3) ML Registry (Advanced)

```bash
cd python_web/module_12/advanced_edition/ml_registry_app
cp .env.example .env

docker-compose up -d
```

Open:
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (minioadmin / minioadmin123)

**Health check**
```bash
curl http://localhost:8000/health
```

---

## Stop Services

```bash
docker-compose down
```

To remove volumes too:
```bash
docker-compose down -v
```
