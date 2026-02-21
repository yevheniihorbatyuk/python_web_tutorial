# Module 02: Python Development

> **Prerequisite:** Basic Python syntax. This module covers the tools and patterns you'll use in every subsequent module.

---

## What's Covered

| Topic | File | Key Ideas |
|-------|------|-----------|
| OOP + ABC | `01_abc_and_oop.py` | Abstract interfaces, `breathe()`, LSP violation |
| SOLID | `02_solid_principles.py` | All 5 principles with the Human hierarchy |
| Design Patterns | `03_design_patterns.py` | Singleton, Factory, Adapter |
| Dev Tools | `04_dev_tools.py` | pipenv vs poetry vs pip; generates config files |
| Chatbot Demo | `05_chatbot_demo.py` | Bot using the Human interface |
| Docker | `06_docker_intro.py` | Image vs container; generates Dockerfile |

---

## Quick Start

```bash
cd standalone_examples

# Run each example independently
python 01_abc_and_oop.py
python 02_solid_principles.py
python 03_design_patterns.py

# Generate project config files
python 04_dev_tools.py

# Interactive chatbot demo
python 05_chatbot_demo.py

# Generate Dockerfile
python 06_docker_intro.py > Dockerfile
```

---

## Key Concepts

### ABC — Abstract Base Classes

Python's `abc` module lets you define **interfaces** — contracts that subclasses must fulfill.
Unlike Java/C# interfaces, Python ABCs can include concrete methods too.

```python
from abc import ABC, abstractmethod

class Human(ABC):
    @abstractmethod
    def walk(self) -> str: ...   # subclasses MUST implement

    def breathe(self) -> str:    # concrete — subclasses INHERIT this
        return "inhale → exhale"
```

### SOLID in Python

| Principle | Short form | Python idiom |
|-----------|-----------|--------------|
| Single Responsibility | One class, one job | Small classes, services |
| Open/Closed | Extend, don't modify | ABC + subclasses |
| Liskov Substitution | Subclass works where parent works | Don't break contracts |
| Interface Segregation | Small interfaces | Protocol / ABC per concern |
| Dependency Inversion | Depend on abstractions | Inject via constructor |

### Design Patterns a Junior Should Know

1. **Singleton** — one instance only (DB connection pool, logger)
2. **Factory** — create objects without specifying exact class
3. **Adapter** — make incompatible interfaces work together

---

## Tools Comparison

| Tool | Lock file | Virtual env | Use when |
|------|-----------|-------------|----------|
| `pip + requirements.txt` | No (manual) | `venv` manually | Simple scripts |
| `pipenv` | `Pipfile.lock` | Auto | Team projects |
| `poetry` | `poetry.lock` | Auto | Libraries + publishing |

---

## Connection to Later Modules

| This module | → Used in |
|-------------|----------|
| ABC interfaces | Module 08 (SQLAlchemy models), Module 12 (FastAPI dependencies) |
| Design patterns | Module 12 (Singleton for DB engine), Module 14 (Factory for services) |
| Docker basics | All modules with `docker-compose.yml` |
| poetry/pipenv | Module 10 (Django), Module 12 (FastAPI) |
