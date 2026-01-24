# Module 12 Learning Checklist

Use this checklist to track progress. Pick one path and mark items as you complete them.

---

## Beginner Path

### Standalone Concepts (beginner_edition/standalone_examples/)
- [ ] Run `1_minimal_app.py` and explore `/docs`
- [ ] Add a new route and query parameter
- [ ] Run `2_database_basics.py` and modify a model
- [ ] Run `3_auth_basics.py` and test protected routes
- [ ] Run `4_test_examples.py` with pytest

### Todo App (beginner_edition/todo_app/)
- [ ] Run with Docker Compose
- [ ] Register and login via `/docs`
- [ ] Create, update, and delete a todo
- [ ] Read `app/main.py`, `models.py`, `schemas.py`, `auth.py`
- [ ] Run `pytest tests/ -v`
- [ ] Add one small feature (e.g., priority or tags)

---

## Intermediate Path

### Blog API (intermediate_edition/blog_api/)
- [ ] Run with Docker Compose
- [ ] Register and login
- [ ] Create posts and comments
- [ ] Test pagination and filtering in `/posts`
- [ ] Read `app/models.py` for relationships
- [ ] Add one extension (e.g., categories or search)

---

## Advanced Path

### Async Patterns
- [ ] Read `advanced_edition/async_patterns.py`
- [ ] Identify one async pattern you can reuse

### ML Registry App (advanced_edition/ml_registry_app/)
- [ ] Run with Docker Compose
- [ ] Register/login and create a model
- [ ] Upload a file to MinIO via API
- [ ] Explore `app/models/` and `app/api/v1/`
- [ ] Review tests in `tests/`
- [ ] Run `pytest tests/ -v`

---

## Optional Capstone

- [ ] Add OAuth login (Google/GitHub)
- [ ] Add role-based access control (RBAC)
- [ ] Add API key auth for service clients
