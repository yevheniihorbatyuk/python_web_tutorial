# Module 12 Structure - Organization Guide

This document reflects the actual module layout and where each learning asset lives.

---

## Directory Tree

```
module_12/
│
├── README.md
├── Module12_Complete_Learning_Path.ipynb
├── MLModelRegistry.postman_collection.json
├── STRUCTURE_SUMMARY.txt
│
├── docs/
│   ├── LEARNING_PATH.md
│   ├── QUICKSTART.md
│   ├── NOTEBOOK_GUIDE.md
│   ├── CHECKLIST.md
│   ├── API_EXAMPLES.md
│   ├── STRUCTURE.md
│   └── en/
│       ├── architecture.md
│       ├── authentication.md
│       └── testing.md
│
├── beginner_edition/
│   ├── README.md
│   ├── standalone_examples/
│   │   ├── README.md
│   │   ├── 1_minimal_app.py
│   │   ├── 2_database_basics.py
│   │   ├── 3_auth_basics.py
│   │   └── 4_test_examples.py
│   └── todo_app/
│       ├── app/
│       ├── tests/
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── requirements.txt
│       └── README.md
│
├── intermediate_edition/
│   ├── README.md
│   └── blog_api/
│       ├── app/
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── requirements.txt
│       └── README.md
│
└── advanced_edition/
    ├── README.md
    ├── async_patterns.py
    └── ml_registry_app/
        ├── app/
        ├── tests/
        ├── notebooks/
        ├── alembic/
        ├── docker-compose.yml
        ├── Dockerfile
        ├── requirements.txt
        └── README.md
```

---

## Learning Progression (Concept → Application → Production)

```
Beginner
  ├─ standalone_examples/   (concepts in isolation)
  └─ todo_app/              (first full CRUD app)

Intermediate
  └─ blog_api/              (relationships, pagination, filters)

Advanced
  ├─ async_patterns.py      (async reference)
  └─ ml_registry_app/       (production-style system)
```

---

## Where to Start

- **New to FastAPI:** `docs/LEARNING_PATH.md` → Beginner Path
- **Already know basics:** `intermediate_edition/README.md`
- **Want production patterns:** `advanced_edition/README.md`
