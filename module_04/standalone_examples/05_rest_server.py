"""
Модуль 04.5: REST-сервер на BaseHTTPRequestHandler
====================================================

Що вивчається:
  1. BaseHTTPRequestHandler — HTTP без фреймворків
  2. Роутинг вручну: if self.path == "/..."
  3. Читання тіла POST-запиту через Content-Length
  4. Відповіді: статус + заголовки + тіло
  5. Порівняння з FastAPI — що робиться "під капотом"

Запуск:   python 05_rest_server.py
Тестування:
  curl http://localhost:8080/hello
  curl http://localhost:8080/echo -X POST -H "Content-Type: application/json" -d '{"msg": "test"}'
  curl http://localhost:8080/contacts
  curl http://localhost:8080/contacts -X POST -H "Content-Type: application/json" -d '{"name": "Alice", "email": "alice@example.com"}'
  curl http://localhost:8080/contacts/1
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080

# Простий in-memory "storage" (замість БД)
_contacts: list[dict] = []
_next_id: int = 1
_lock = threading.Lock()   # захист від race condition при POST


# ─── Хелпери ──────────────────────────────────────────────────────────────────

def _send_json(handler: "ContactsHandler", status: int, data: object) -> None:
    """Надсилає JSON-відповідь з правильними заголовками."""
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json_body(handler: "ContactsHandler") -> dict | None:
    """Читає тіло запиту і парсить JSON. Повертає None при помилці."""
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return None
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return None


# ─── Обробник запитів ────────────────────────────────────────────────────────

class ContactsHandler(BaseHTTPRequestHandler):
    """
    Кожен метод do_GET / do_POST відповідає HTTP методу.
    Маршрутизація — вручну через self.path.

    У FastAPI це замінюється на:
      @app.get("/contacts")
      @app.post("/contacts")
    """

    # ─── GET ──────────────────────────────────────────────────────────────────

    def do_GET(self) -> None:
        if self.path == "/hello":
            self._handle_hello()

        elif self.path == "/contacts":
            self._handle_list_contacts()

        elif self.path.startswith("/contacts/"):
            contact_id = self._parse_id(self.path[len("/contacts/"):])
            if contact_id is None:
                _send_json(self, 400, {"error": "Invalid ID"})
            else:
                self._handle_get_contact(contact_id)

        else:
            _send_json(self, 404, {"error": f"Route not found: {self.path}"})

    def _handle_hello(self) -> None:
        _send_json(self, 200, {
            "message": "Hello from Python stdlib server!",
            "endpoints": {
                "GET /hello": "this page",
                "GET /contacts": "list all contacts",
                "GET /contacts/:id": "get contact by id",
                "POST /contacts": "create contact",
            }
        })

    def _handle_list_contacts(self) -> None:
        _send_json(self, 200, {"contacts": _contacts, "total": len(_contacts)})

    def _handle_get_contact(self, contact_id: int) -> None:
        contact = next((c for c in _contacts if c["id"] == contact_id), None)
        if contact is None:
            _send_json(self, 404, {"error": f"Contact {contact_id} not found"})
        else:
            _send_json(self, 200, contact)

    # ─── POST ─────────────────────────────────────────────────────────────────

    def do_POST(self) -> None:
        if self.path == "/echo":
            self._handle_echo()

        elif self.path == "/contacts":
            self._handle_create_contact()

        else:
            _send_json(self, 404, {"error": f"Route not found: {self.path}"})

    def _handle_echo(self) -> None:
        """Повертає те саме тіло що й прийняло."""
        data = _read_json_body(self)
        if data is None:
            _send_json(self, 400, {"error": "Invalid or empty JSON body"})
            return
        _send_json(self, 200, {"echo": data})

    def _handle_create_contact(self) -> None:
        global _next_id

        data = _read_json_body(self)
        if data is None:
            _send_json(self, 400, {"error": "Invalid or empty JSON body"})
            return

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        if not name or not email:
            _send_json(self, 422, {"error": "Fields 'name' and 'email' are required"})
            return

        with _lock:
            contact = {"id": _next_id, "name": name, "email": email}
            _contacts.append(contact)
            _next_id += 1

        _send_json(self, 201, contact)

    # ─── Допоміжні ────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_id(raw: str) -> int | None:
        try:
            return int(raw)
        except (ValueError, TypeError):
            return None

    def log_message(self, format: str, *args: object) -> None:
        """Власний формат логів замість стандартного."""
        print(f"  [{self.command}] {self.path} → {args[1]}")


# ─── Порівняння з FastAPI ─────────────────────────────────────────────────────

FASTAPI_EQUIVALENT = """
# Те саме на FastAPI (Module 12+):

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ContactIn(BaseModel):
    name: str
    email: str

@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

@app.get("/contacts")
def list_contacts():
    return {"contacts": _contacts, "total": len(_contacts)}

@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int):
    contact = next((c for c in _contacts if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Not found")
    return contact

@app.post("/contacts", status_code=201)
def create_contact(body: ContactIn):
    # валідація — автоматично через Pydantic
    # JSON серіалізація — автоматично
    # заголовки Content-Type — автоматично
    ...
"""


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    server = HTTPServer(("", PORT), ContactsHandler)

    print(f"Сервер запущено на http://localhost:{PORT}")
    print("Зупинити: Ctrl+C\n")
    print("Тестування (вставте в інший термінал або Postman):")
    print(f"  curl http://localhost:{PORT}/hello")
    print(f"  curl http://localhost:{PORT}/contacts")
    print(
        f"  curl http://localhost:{PORT}/contacts -X POST "
        f"-H 'Content-Type: application/json' "
        f"-d '{{\"name\": \"Alice\", \"email\": \"alice@example.com\"}}'"
    )
    print(f"  curl http://localhost:{PORT}/contacts/1")
    print(f"\n--- FastAPI еквівалент ---{FASTAPI_EQUIVALENT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер зупинено.")
        server.server_close()
