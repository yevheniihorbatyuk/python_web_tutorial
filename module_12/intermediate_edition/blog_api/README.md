# Blog API - FastAPI Application with Posts and Comments

An intermediate-level FastAPI application demonstrating database relationships, pagination, and more complex CRUD operations.

## 📋 Features

- User registration and JWT authentication
- Create, read, update, delete blog posts
- Add comments to posts
- Filter posts by author and publication status
- Pagination support
- PostgreSQL with async SQLAlchemy
- Docker Compose deployment

## 🚀 Quick Start

### With Docker Compose

```bash
docker-compose up -d
sleep 10
```

App available at: `http://localhost:8001/docs`

### Local Development

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export DATABASE_URL=postgresql://user:password@localhost:5432/blog_db
uvicorn app.main:app --reload
```

## 🔐 Authentication

Register and login (same as Todo App):

```bash
# Register
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@example.com",
    "username": "author",
    "full_name": "Jane Doe",
    "password": "securepass123"
  }'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "author", "password": "securepass123"}'
```

## 📝 Post Operations

### Create a Post

```bash
curl -X POST http://localhost:8001/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI",
    "content": "FastAPI is a modern web framework...",
    "published": true
  }'
```

### List Posts

```bash
# All posts
curl http://localhost:8001/posts

# Filter by author
curl "http://localhost:8001/posts?author_id=1"

# Filter by publication status
curl "http://localhost:8001/posts?published=true"

# Pagination
curl "http://localhost:8001/posts?skip=0&limit=10"
```

### Get Post with Comments

```bash
curl http://localhost:8001/posts/1
```

### Update Post

```bash
curl -X PUT http://localhost:8001/posts/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"published": true}'
```

### Delete Post

```bash
curl -X DELETE http://localhost:8001/posts/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 💬 Comment Operations

### Add Comment

```bash
curl -X POST http://localhost:8001/posts/1/comments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great article! Thanks for sharing."}'
```

### Delete Comment

```bash
curl -X DELETE http://localhost:8001/comments/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Project Structure

```
blog_api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # SQLAlchemy models (User, Post, Comment)
│   ├── schemas.py        # Pydantic validation schemas
│   ├── database.py       # Database configuration
│   └── auth.py           # JWT and password utilities
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 Key Concepts

### Database Relationships
- **User has many Posts** (One-to-Many)
- **User has many Comments** (One-to-Many)
- **Post has many Comments** (One-to-Many)
- **Comment belongs to User and Post** (Foreign Keys)

### Advanced Features
- Pagination with `skip` and `limit` parameters
- Filtering by multiple criteria
- Authorization checks (users can only modify their own posts/comments)
- Cascading deletes (delete user → delete all their posts/comments)

### Model Relationships
```python
User.posts → List[Post]
User.comments → List[Comment]
Post.author → User
Post.comments → List[Comment]
Comment.post → Post
Comment.author → User
```

## 📖 Learning Resources

Compare with Todo App to see the differences:
- Todo App: Simple 2-model application
- Blog API: Complex 3-model application with relationships

See documentation for more details.

## 📝 License

Educational project.
