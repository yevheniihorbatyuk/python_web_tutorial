# API Request Examples - Module 12

Practical request examples for each application.

---

## Todo App (Beginner)

Base URL: `http://localhost:8000`

### Register + Login
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"pass123"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'
```

### Create Todo
```bash
curl -X POST http://localhost:8000/todos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","description":"Complete module 12"}'
```

---

## Blog API (Intermediate)

Base URL: `http://localhost:8001`

### Register + Login
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"author@example.com","username":"author","password":"pass123"}'

curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"author","password":"pass123"}'
```

### Create Post + Comment
```bash
curl -X POST http://localhost:8001/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"FastAPI","content":"Hello","published":true}'

curl -X POST http://localhost:8001/posts/1/comments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Great post"}'
```

---

## ML Registry (Advanced)

Base URL: `http://localhost:8000/api/v1`

### Register + Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"mluser","password":"pass123"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=mluser&password=pass123"
```

### Create ML Model
```bash
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Fraud Model","framework":"sklearn","task_type":"classification"}'
```

### Upload File
```bash
echo "model" > model.pkl
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@model.pkl"
```
