# Web Basics: HTTP, REST, WebSockets

---

## HTTP — як це працює

HTTP (HyperText Transfer Protocol) — протокол запит/відповідь поверх TCP.

### Запит (Request)

```
POST /api/users HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer eyJ...

{"name": "Alice", "email": "alice@example.com"}
│─── Method ───│ │── Path ──│   │──── Headers ────│   │── Body ──│
```

### Відповідь (Response)

```
HTTP/1.1 201 Created
Content-Type: application/json

{"id": 42, "name": "Alice", "email": "alice@example.com"}
│─── Status ──│   │──── Headers ────│   │────── Body ──────│
```

### Методи та їх семантика

| Метод | Дія | Тіло? | Ідемпотентний? |
|-------|-----|-------|----------------|
| GET | Отримати | Ні | Так |
| POST | Створити | Так | Ні |
| PUT | Замінити | Так | Так |
| PATCH | Частково оновити | Так | Так |
| DELETE | Видалити | Ні | Так |

### Статус коди

| Код | Значення |
|-----|---------|
| 200 OK | Успіх (GET, PATCH, PUT) |
| 201 Created | Ресурс створено (POST) |
| 204 No Content | Успіх без тіла (DELETE) |
| 400 Bad Request | Помилка клієнта (невалідний JSON) |
| 401 Unauthorized | Потрібна авторизація |
| 403 Forbidden | Авторизований але не дозволено |
| 404 Not Found | Ресурс не існує |
| 422 Unprocessable | Валідація не пройшла (FastAPI) |
| 429 Too Many Requests | Rate limit |
| 500 Internal Error | Помилка сервера |

---

## REST — архітектурний стиль

REST (Representational State Transfer) — не протокол, а набір принципів.

**Ресурси** адресуються через URL:
```
/users          → колекція
/users/42       → конкретний ресурс
/users/42/posts → підресурс
```

**Операції** через HTTP методи:
```
GET    /contacts       → список контактів
POST   /contacts       → новий контакт
GET    /contacts/5     → контакт #5
PUT    /contacts/5     → замінити контакт #5
PATCH  /contacts/5     → частково оновити контакт #5
DELETE /contacts/5     → видалити контакт #5
```

**Stateless:** кожен запит містить всю необхідну інформацію (токен у заголовку).

---

## BaseHTTPRequestHandler vs FastAPI

```python
# Python stdlib — вручну
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/hello":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"message": "Hello"}')

# FastAPI (Module 12) — автоматично
@app.get("/hello")
def hello():
    return {"message": "Hello"}   # FastAPI сам серіалізує в JSON і ставить заголовки
```

BaseHTTPRequestHandler показує що відбувається "під капотом" — корисно для розуміння.

---

## Postman — тестування API

**Основні дії:**

1. **Новий запит** → вибрати метод (GET/POST/...) → ввести URL
2. **Headers** → `Content-Type: application/json`
3. **Body** → raw → JSON → `{"key": "value"}`
4. **Send** → подивитись Response

**Корисні функції:**
- Collections — зберігати набори запитів
- Environment variables — `{{base_url}}` замість `http://localhost:8000`
- Tests tab — автоматичні перевірки (`pm.response.to.have.status(200)`)

**Альтернатива через curl:**
```bash
# GET
curl http://localhost:8080/hello

# POST з JSON
curl -X POST http://localhost:8080/echo \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'

# З авторизацією (Module 12)
curl http://localhost:8000/api/v1/contacts \
     -H "Authorization: Bearer eyJ..."
```

---

## WebSockets

HTTP: клієнт запитує → сервер відповідає → з'єднання закривається.

WebSocket: одне постійне двостороннє з'єднання.

```
Client ──── HTTP Upgrade ────→ Server
       ←──────────────────────
       ←── server push ────────  (сервер може надсилати без запиту!)
       ──── client message ───→
       ←──────────────────────
```

**Коли потрібен WebSocket:**
- Чат
- Realtime-нотифікації
- Онлайн-гра
- Live-оновлення dashboard

**Python:**
```python
import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

asyncio.run(websockets.serve(handler, "localhost", 8765))
```

У Module 06 є `async_examples/03_websockets_demo.py` з повним прикладом.
