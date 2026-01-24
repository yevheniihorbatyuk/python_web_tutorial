# Module12_Complete_Learning_Path.ipynb - User Guide

## Overview

This notebook provides an **interactive, hands-on learning experience** across all three levels of Module 12:

- Beginner (Todo App)
- Intermediate (Blog API)
- Advanced (ML Registry)

**Location:** `python_web/module_12/Module12_Complete_Learning_Path.ipynb`

---

## What's Inside

### 40+ Learning Cells

The notebook is organized into three major sections:

1. **Beginner Level - Todo App**
   - Registration, login, and CRUD operations
   - Theory explanations for each concept

2. **Intermediate Level - Blog API**
   - Posts, comments, pagination, filtering
   - One-to-many relationships

3. **Advanced Level - ML Registry**
   - Auth flow with access + refresh tokens
   - Model creation and file upload
   - Advanced comparison notes

---

## Requirements

```bash
# Python 3.9+
python3 --version

# Jupyter
pip install jupyter ipython

# Python packages for the notebook
pip install requests
```

---

## Start the Applications

Todo App and ML Registry both use port 8000. Run them **one at a time** or change ports in docker-compose.

```bash
# Terminal 1 - Todo App
cd python_web/module_12/beginner_edition/todo_app
docker-compose up

# Terminal 2 - Blog API
cd python_web/module_12/intermediate_edition/blog_api
docker-compose up

# Terminal 3 - ML Registry (start after stopping Todo App)
cd python_web/module_12/advanced_edition/ml_registry_app
docker-compose up
```

Health checks:
```bash
curl http://localhost:8000/health  # Todo App / ML Registry
curl http://localhost:8001/health  # Blog API
```

---

## Open the Notebook

```bash
cd /root/goit/python_web/module_12
jupyter notebook Module12_Complete_Learning_Path.ipynb
```

Browser opens at: `http://localhost:8888`

---

## How to Use

- Read the markdown cells first
- Run code cells in order
- Modify parameters and re-run

---

## Common Issues

### Connection refused
Make sure the corresponding app is running and the port matches the section.

### 401 Unauthorized
Re-run the login cell to refresh the token.

### 404 Not Found
Check `API_URL` for the current section.
