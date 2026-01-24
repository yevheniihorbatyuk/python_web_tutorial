"""
Minimal FastAPI Application - Start Here!

This is the simplest FastAPI app showing core concepts:
- Route handlers
- Path and query parameters
- Request/response models
- Automatic API documentation at /docs

Run: python minimal_app.py
Then visit: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Minimal Todo API",
    description="Simplest possible FastAPI app",
    version="1.0.0"
)

# ============================================================================
# PYDANTIC MODELS - Define request/response data structure
# ============================================================================

class TodoCreate(BaseModel):
    """Data model for creating a todo."""
    title: str
    description: Optional[str] = None

class TodoResponse(BaseModel):
    """Data model for todo response."""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

# ============================================================================
# IN-MEMORY DATABASE - Simple storage (not persistent)
# ============================================================================

todos_db = []
next_id = 1

# ============================================================================
# ROUTES - Define API endpoints
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint - shows available operations."""
    return {
        "message": "Welcome to Minimal Todo API",
        "endpoints": {
            "list_todos": "GET /todos/",
            "get_todo": "GET /todos/{todo_id}",
            "create_todo": "POST /todos/",
            "update_todo": "PUT /todos/{todo_id}",
            "delete_todo": "DELETE /todos/{todo_id}",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/todos/", response_model=list[TodoResponse])
def list_todos(completed: Optional[bool] = None):
    """
    Get all todos, optionally filtered by completion status.

    Query parameters:
    - completed: Filter by true/false (optional)

    Example: GET /todos/?completed=false
    """
    if completed is None:
        return todos_db
    return [t for t in todos_db if t["completed"] == completed]

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """
    Get a specific todo by ID.

    Path parameters:
    - todo_id: The ID of the todo

    Returns: 404 if not found
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

@app.post("/todos/", response_model=TodoResponse, status_code=201)
def create_todo(todo_create: TodoCreate):
    """
    Create a new todo.

    Request body:
    {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }

    Returns: Created todo with ID
    """
    global next_id

    # Create new todo
    todo = {
        "id": next_id,
        "title": todo_create.title,
        "description": todo_create.description,
        "completed": False
    }

    todos_db.append(todo)
    next_id += 1

    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoCreate):
    """
    Update an existing todo.

    Path parameters:
    - todo_id: The ID of the todo to update

    Request body:
    {
        "title": "Updated title",
        "description": "Updated description"
    }
    """
    for i, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            todos_db[i]["title"] = todo_update.title
            todos_db[i]["description"] = todo_update.description
            return todos_db[i]

    raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int):
    """
    Toggle completion status of a todo.

    Path parameters:
    - todo_id: The ID of the todo to toggle
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            return todo

    raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """
    Delete a todo.

    Path parameters:
    - todo_id: The ID of the todo to delete

    Returns: 204 No Content on success
    """
    for i, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            todos_db.pop(i)
            return

    raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n✅ Starting Minimal Todo API...")
    print("📖 Visit http://localhost:8000/docs for interactive API documentation")
    print("🧪 Try: curl http://localhost:8000/todos/\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
