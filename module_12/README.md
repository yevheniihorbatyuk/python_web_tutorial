# Module 12: FastAPI Web Development

Learn modern async web development with FastAPI through practical examples organized by learning level.

---

## Start Here (Recommended Order)

1. **[docs/LEARNING_PATH.md](docs/LEARNING_PATH.md)** - Choose your path and timeline
2. **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Run any app in 5 minutes
3. **[docs/NOTEBOOK_GUIDE.md](docs/NOTEBOOK_GUIDE.md)** - How to use the interactive notebook
4. **Edition README**
   - Beginner: [beginner_edition/README.md](beginner_edition/README.md)
   - Intermediate: [intermediate_edition/README.md](intermediate_edition/README.md)
   - Advanced: [advanced_edition/README.md](advanced_edition/README.md)

---

## What's Inside

Three complete FastAPI applications plus standalone concept files:

| App | Level | Models | Focus | Typical Time |
|-----|-------|--------|-------|--------------|
| **Todo App** | Beginner ⭐⭐ | User, Todo | Routes, auth, tests | 2-3h |
| **Blog API** | Intermediate ⭐⭐⭐ | User, Post, Comment | Relationships, pagination | 2-3h |
| **ML Registry** | Advanced ⭐⭐⭐⭐ | 5+ models | Production patterns, migrations | 4-5h |

Standalone examples for single-concept practice (beginner_edition/standalone_examples/):
- 1_minimal_app.py - Routes and basics
- 2_database_basics.py - SQLAlchemy and CRUD
- 3_auth_basics.py - JWT authentication
- 4_test_examples.py - Testing with pytest

---

## Key Docs

- **[docs/STRUCTURE.md](docs/STRUCTURE.md)** - Module organization
- **[docs/CHECKLIST.md](docs/CHECKLIST.md)** - Track your progress
- **[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)** - API request examples for all apps
- **[docs/en/architecture.md](docs/en/architecture.md)** - System design concepts
- **[docs/en/authentication.md](docs/en/authentication.md)** - JWT explained
- **[docs/en/testing.md](docs/en/testing.md)** - Testing patterns

---

## Quick Commands

### Run Todo App (Beginner)
```bash
cd beginner_edition/todo_app
docker-compose up
# Visit http://localhost:8000/docs
```

### Run Blog API (Intermediate)
```bash
cd intermediate_edition/blog_api
docker-compose up
# Visit http://localhost:8001/docs
```

### Run ML Registry (Advanced)
```bash
cd advanced_edition/ml_registry_app
docker-compose up
# Visit http://localhost:8000/docs
```

---

## Directory Snapshot

```
module_12/
├── README.md
├── Module12_Complete_Learning_Path.ipynb
├── docs/
├── beginner_edition/
├── intermediate_edition/
└── advanced_edition/
```

---

## Tech Stack

All apps use:
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic 2.0** - Data validation
- **PostgreSQL** - Database
- **Docker** - Containerization
- **pytest** - Testing
