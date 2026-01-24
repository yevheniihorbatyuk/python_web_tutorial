# Intermediate Edition - Real FastAPI Applications

Complete working applications demonstrating intermediate FastAPI concepts and patterns.

## 📚 What You'll Learn

- Database relationships (One-to-Many)
- Pagination and filtering
- Complex queries
- Multi-user authorization
- API design patterns
- Docker deployment

## 📁 Contents

### **Blog API** (`blog_api/`)
A complete blog application with users, posts, and comments.

**Features:**
- User registration and JWT authentication
- Create, read, update, delete blog posts
- Add comments to posts
- Filter posts by author and publication status
- Pagination support
- PostgreSQL with relationships
- Docker Compose setup

**Models:**
- User (authors and commenters)
- Post (blog posts)
- Comment (post comments)

**Complexity:** ⭐⭐⭐ (Intermediate+)

**Learning Focus:**
- Understanding relationships (User → Posts → Comments)
- Pagination and filtering
- Multi-user data separation
- Complex queries

---

## 🚀 Quick Start

### Run the Blog API

```bash
cd blog_api
docker-compose up
```

Visit: http://localhost:8001/docs

### API Examples

```bash
# Register user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"pass123"}'

# Login
TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -d "username=user&password=pass123" | jq -r '.access_token')

# Create post
curl -X POST http://localhost:8001/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Post","content":"Content here","published":true}'

# Get posts with comments
curl http://localhost:8001/posts/1
```

---

## 📖 Study Guide

### Understand the Structure

1. **Read:** `blog_api/app/main.py` - See all routes
2. **Read:** `blog_api/app/models.py` - Understand relationships
3. **Read:** `blog_api/app/schemas.py` - Request/response models
4. **Test:** Use http://localhost:8001/docs

### Key Concepts to Learn

1. **Database Relationships**
   - User has many Posts
   - User has many Comments
   - Post has many Comments
   - Cascade deletes

2. **Pagination**
   - Query parameters: `skip`, `limit`
   - Default and maximum limits
   - How to implement

3. **Filtering**
   - Filter by author
   - Filter by status
   - Combine multiple filters

4. **Authorization**
   - Users can only edit/delete their own posts
   - Users can only delete their own comments
   - Post author can't delete others' comments

---

## 🎯 Learning Milestones

After studying this app, you should be able to:

- [ ] Explain One-to-Many relationships
- [ ] Understand Foreign Key constraints
- [ ] Implement pagination
- [ ] Filter data with multiple criteria
- [ ] Handle multi-user authorization
- [ ] Design API endpoints
- [ ] Deploy with Docker

---

## 📝 Exercises

### Exercise 1: Add Categories
Add a Category model:
```python
class Category(Base):
    name: str
    posts: Mapped[List["Post"]]

class Post:
    category_id: int
    category: Mapped["Category"]
```

### Exercise 2: User Profiles
Add user profile:
```python
class User:
    bio: Optional[str]
    avatar_url: Optional[str]
```

### Exercise 3: Comment Reactions
Add upvotes/downvotes to comments:
```python
class Comment:
    upvotes: int = 0
    downvotes: int = 0
```

---

## 🔗 Comparison with Beginner Edition

| Aspect | Todo App (Beginner) | Blog API (Intermediate) |
|--------|-------------------|------------------------|
| Models | 2 (User, Todo) | 3 (User, Post, Comment) |
| Relationships | Simple | One-to-Many chains |
| Filtering | By status only | Multiple criteria |
| Pagination | No | Yes |
| Features | Basic CRUD | Advanced patterns |
| Complexity | ⭐⭐ | ⭐⭐⭐ |
| Study time | 2 hours | 2-3 hours |

---

## 📚 Next Steps

After mastering this application:

1. **Build Your Own**
   - Think of an idea
   - Design the database schema
   - Implement the API
   - Deploy it

2. **Move to Advanced**
   - Study `ml_registry_app/` in advanced_edition/
   - Learn production patterns
   - Understand complex applications

3. **Add Features**
   - Search functionality
   - Sorting options
   - Advanced filtering
   - File uploads

---

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Database
- **Docker** - Containerization
- **python-jose** - JWT handling
- **passlib** - Password hashing

---

## 📖 Related Documentation

- See [../README.md](../README.md) for module overview
- See [../docs/LEARNING_PATH.md](../docs/LEARNING_PATH.md) for learning paths and detailed schedules
- See [../docs/CHECKLIST.md](../docs/CHECKLIST.md) to track progress
- See [../docs/STRUCTURE.md](../docs/STRUCTURE.md) for complete module organization

---

**Ready to learn? Start with `/docs` endpoint after running Docker! 🚀**
