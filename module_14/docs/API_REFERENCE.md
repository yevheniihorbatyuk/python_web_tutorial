# API Reference

Base URL (local): `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Auth

### POST /api/v1/auth/register

Create a new user account. Sends a verification email.

**Rate limit:** 5 per minute per IP.

```json
// Request body
{ "email": "user@example.com", "password": "secret123" }

// 201 Created
{ "id": 1, "email": "user@example.com", "is_verified": false, "avatar_url": null, "created_at": "..." }

// 409 Conflict — email already registered
{ "detail": "An account with this email already exists." }
```

---

### GET /api/v1/auth/verify/{token}

Confirm email address. Token comes from the verification email (24h TTL).

```
// 200 OK
{ "message": "Email verified. You can now log in." }

// 400 Bad Request — expired or wrong-purpose token
{ "detail": "Invalid or expired verification link." }
```

---

### POST /api/v1/auth/login

Exchange credentials for JWT tokens. Requires a verified email.

**Rate limit:** 10 per minute per IP.
**Content-Type:** `application/x-www-form-urlencoded` (OAuth2 form)

```
username=user@example.com&password=secret123

// 200 OK
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }

// 401 Unauthorized — wrong password
// 403 Forbidden   — email not verified
```

---

### POST /api/v1/auth/refresh

Exchange a refresh token for a new access token.

```json
// Request
{ "refresh_token": "eyJ..." }

// 200 OK
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }

// 401 — invalid or expired refresh token
```

---

### POST /api/v1/auth/logout

Blacklist the refresh token in Redis (JWT invalidation pattern).

```json
// Request
{ "refresh_token": "eyJ..." }

// 204 No Content
```

---

## Contacts

All endpoints require `Authorization: Bearer <access_token>` and a **verified** account.

### GET /api/v1/contacts/

List contacts with optional search and pagination.

| Query param | Default | Description |
|-------------|---------|-------------|
| `search`    | —       | Filter by first name, last name, or email (case-insensitive) |
| `skip`      | 0       | Pagination offset |
| `limit`     | 20      | Max results (1–100) |

```json
// 200 OK
[
  { "id": 1, "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com",
    "phone": null, "birthday": "1990-05-15", "notes": null, "created_at": "..." }
]
```

---

### POST /api/v1/contacts/

Create a new contact.

```json
// Request
{
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com",
  "phone": "+380501234567",
  "birthday": "1990-05-15",
  "notes": "Met at conference"
}

// 201 Created — contact object
```

---

### GET /api/v1/contacts/birthdays

Return contacts with birthdays in the **next 7 days** (inclusive).

Result is cached per user per day in Redis (TTL = 1 hour).

```json
// 200 OK
[
  { "id": 3, "first_name": "Bob", "last_name": "Jones",
    "birthday": "1985-10-14", "days_until": 2 }
]
```

> **Note:** This route is declared before `/{contact_id}` in the code so FastAPI
> doesn't try to parse "birthdays" as an integer ID.

---

### GET /api/v1/contacts/{id}

Get a single contact (owner only).

```
// 200 OK — contact object
// 404 Not Found
```

---

### PUT /api/v1/contacts/{id}

Full replacement of a contact (all fields required).

---

### PATCH /api/v1/contacts/{id}

Partial update — only send fields to change.

```json
{ "phone": "+380509999999" }
```

---

### DELETE /api/v1/contacts/{id}

Delete a contact.

```
// 204 No Content
// 404 Not Found
```

---

## Users

### GET /api/v1/users/me

Return the current user's profile.

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_verified": true,
  "avatar_url": "https://res.cloudinary.com/demo/image/upload/...",
  "created_at": "..."
}
```

---

### PATCH /api/v1/users/me

Update profile fields (currently: email only).

```json
{ "email": "new@example.com" }
```

---

### POST /api/v1/users/me/avatar

Upload a profile photo. Replaces the previous avatar.

**Content-Type:** `multipart/form-data`
**Accepted formats:** JPEG, PNG, GIF, WebP
**Max size:** 5 MB

```
// 200 OK — user object with updated avatar_url
// 422 — invalid file type or file too large
```

File type is validated by inspecting the first bytes (magic bytes), not by
file extension. A `.txt` file renamed to `.jpg` will be rejected.

---

## Error responses

All errors follow the same structure:

```json
{ "detail": "Human-readable error message." }
```

| Status | Meaning |
|--------|---------|
| 400    | Bad request (invalid token, validation error) |
| 401    | Missing or invalid access token |
| 403    | Authenticated but not authorised (email not verified) |
| 404    | Resource not found |
| 409    | Conflict (duplicate email) |
| 422    | Validation error (invalid file type, bad request body) |
| 429    | Rate limit exceeded |
