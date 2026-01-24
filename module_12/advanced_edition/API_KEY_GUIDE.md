# API Key Authentication Guide

API keys provide a way for external services, scripts, and applications to authenticate with your API without requiring user interaction.

---

## When to Use API Keys

### ✅ Good Use Cases

1. **Service-to-Service Communication**
   - Backend microservice calling another service
   - Your app calling third-party APIs

2. **Automated Systems**
   - CI/CD pipeline uploading models
   - Scheduled jobs processing data
   - Cron jobs refreshing reports

3. **Third-Party Integrations**
   - External SaaS platforms
   - Mobile app backend
   - Desktop application

4. **Command-Line Tools**
   - Scripts accessing the API
   - Developer tools

5. **Long-Running Services**
   - Services that run for days/weeks
   - Don't want to manually refresh tokens

### ❌ Don't Use API Keys For

- **User Authentication** - Use OAuth2 or username/password
- **Web Browsers** - Use JWT tokens from login
- **Short-Lived Sessions** - Use JWT with short expiration
- **Sensitive Operations** - Require multi-factor authentication

---

## API Key Lifecycle

### 1. Create API Key

User creates a key through the API:

```bash
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d {
    "name": "CI/CD Pipeline",
    "description": "Used for automated model uploads in GitHub Actions",
    "scopes": "models:read,models:write",
    "expires_in_days": 90,
    "rate_limit_requests": 100
  }
```

**Response:**
```json
{
  "id": 42,
  "name": "CI/CD Pipeline",
  "key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "scopes": "models:read,models:write",
  "expires_at": "2025-04-24T12:00:00Z",
  "created_at": "2025-01-24T12:00:00Z"
}
```

**⚠️ IMPORTANT:** Save the key immediately! It's shown only once.

### 2. Use API Key

Include in request headers:

```bash
curl http://localhost:8000/api/v1/models \
  -H "X-API-Key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

Or in query parameter (less secure):

```bash
curl "http://localhost:8000/api/v1/models?api_key=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

### 3. Monitor Usage

List API keys:

```bash
curl http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <jwt_token>"
```

**Response:**
```json
[
  {
    "id": 42,
    "name": "CI/CD Pipeline",
    "key_hash": "a1b2c3d4...",
    "scopes": "models:read,models:write",
    "is_active": true,
    "last_used_at": "2025-01-24T10:30:00Z",
    "total_requests": 245,
    "rate_limit_requests": 100,
    "expires_at": "2025-04-24T12:00:00Z"
  }
]
```

### 4. Rotate API Key

Periodically rotate keys for security:

```bash
curl -X POST http://localhost:8000/api/v1/api-keys/42/rotate \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d {
    "expires_in_days": 90
  }
```

**Response:**
```json
{
  "old_key_id": 42,
  "new_key_id": 43,
  "new_key": "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4",
  "message": "Old API key (ID: 42) has been deactivated. Update your applications to use the new key."
}
```

The old key becomes inactive immediately.

### 5. Revoke API Key

When no longer needed:

```bash
curl -X DELETE http://localhost:8000/api/v1/api-keys/42 \
  -H "Authorization: Bearer <jwt_token>"
```

---

## Scopes

Scopes control what operations an API key can perform.

### Scope Format

```
resource:action
```

Examples:
- `models:read` - Can read models
- `models:write` - Can create/update models
- `models:delete` - Can delete models
- `models:*` - All operations on models
- `*:read` - Can read any resource
- `*:*` - Full access

### Combining Scopes

Use comma-separated list:

```
models:read,models:write,experiments:read
```

### Wildcard Matching

| Scope | Can Access |
|-------|-----------|
| `models:read` | `models:read` only |
| `models:*` | `models:read`, `models:write`, `models:delete` |
| `*:read` | `models:read`, `experiments:read`, any `read` |
| `*:*` | Everything |

### Checking Scopes in Code

```python
# In API key auth module
api_key.has_scope("models:read")  # True if key has read scope on models
api_key.has_scope("models:write")  # True if key has models:* or *:*
```

### Using Scopes in Endpoints

```python
@router.post("/models")
async def create_model(
    model_data: MLModelCreate,
    current_user: Annotated[User, Depends(
        get_api_key_user_with_scope("models:write")
    )]
):
    # Only API keys with models:write scope reach here
    return create_model_in_db(model_data, current_user)
```

---

## Security Best Practices

### 1. Treat API Keys Like Passwords

- **Never** commit to version control
- **Never** log or display in output
- **Never** send over unencrypted connections (always use HTTPS)
- Store in secure vaults (GitHub Secrets, AWS Secrets Manager, etc.)

❌ **BAD:**
```bash
# Don't hardcode in scripts
API_KEY="a1b2c3d4e5f6g7h8..."
curl -H "X-API-Key: $API_KEY" ...
```

✅ **GOOD:**
```bash
# Use environment variables or secret management
API_KEY=$(aws secretsmanager get-secret-value --secret-id prod-api-key)
curl -H "X-API-Key: $API_KEY" ...
```

### 2. Use Minimal Scopes

Only grant needed permissions:

❌ **BAD:**
```python
# Too much access
scopes="*:*"  # Can do anything
```

✅ **GOOD:**
```python
# Just what's needed
scopes="models:read,experiments:read"  # Only read operations
```

### 3. Rotate Regularly

- Rotate every 90 days minimum
- Rotate immediately if compromised
- Keep audit trail of rotations

### 4. Use Expiration

```python
# Create with expiration
"expires_in_days": 90
```

Don't use keys that never expire (except for critical system services).

### 5. Rate Limiting

Set reasonable limits:

```python
# Limit to 100 requests per hour
"rate_limit_requests": 100
```

### 6. Monitor Usage

```bash
# Check when key was last used
curl http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <jwt_token>" | jq '.[] | {name, last_used_at}'
```

Alert on unusual activity:
- Key used after expected rotation
- Key used from unexpected location
- Sudden spike in requests

### 7. Revoke Immediately if Compromised

```bash
curl -X DELETE http://localhost:8000/api/v1/api-keys/42 \
  -H "Authorization: Bearer <jwt_token>"
```

### 8. Use Different Keys for Different Services

```python
# CI/CD key (limited scope, short-lived)
ci_key = create_key(
    name="GitHub Actions",
    scopes="models:write",
    expires_in_days=30
)

# Monitoring key (read-only, long-lived)
monitoring_key = create_key(
    name="DataDog Monitoring",
    scopes="models:read,experiments:read",
    expires_in_days=365
)
```

---

## Common Integration Patterns

### Python Script

```python
import requests
from datetime import datetime

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def list_models(self):
        response = self.session.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()

    def create_model(self, name, description):
        data = {"name": name, "description": description}
        response = self.session.post(f"{self.base_url}/models", json=data)
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient("http://localhost:8000/api/v1", api_key)
models = client.list_models()
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class APIClient {
  constructor(baseURL, apiKey) {
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'X-API-Key': apiKey
      }
    });
  }

  async listModels() {
    const response = await this.client.get('/models');
    return response.data;
  }

  async createModel(name, description) {
    const response = await this.client.post('/models', {
      name,
      description
    });
    return response.data;
  }
}

// Usage
const client = new APIClient('http://localhost:8000/api/v1', apiKey);
const models = await client.listModels();
```

### CI/CD (GitHub Actions)

```yaml
name: Upload Model
on: [push]

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Upload model to ML Registry
        env:
          API_KEY: ${{ secrets.ML_REGISTRY_API_KEY }}
        run: |
          curl -X POST http://registry.example.com/api/v1/models \
            -H "X-API-Key: $API_KEY" \
            -H "Content-Type: application/json" \
            -d @model_metadata.json
```

### Docker Environment

```dockerfile
FROM python:3.11

RUN pip install requests

# Store API key in environment
ENV ML_REGISTRY_API_KEY=${ML_REGISTRY_API_KEY}
ENV ML_REGISTRY_URL=http://ml-registry:8000/api/v1

COPY sync_models.py .

CMD ["python", "sync_models.py"]
```

---

## Troubleshooting

### "Invalid or expired API key"

1. **Check key is correct** - Copy-paste carefully
2. **Check key is active** - List keys to verify `is_active: true`
3. **Check key hasn't expired** - Verify `expires_at` is in future
4. **Check header name** - Should be `X-API-Key` (case-sensitive in some systems)

### "API key does not have required scope"

1. **List your keys** - Check current scopes
2. **Update scopes** - PATCH endpoint to add needed scope
3. **Create new key** - If can't update, create key with needed scopes

### "Rate limit exceeded"

1. **Check rate limit** - See `rate_limit_requests` in key info
2. **Wait for window** - Limit resets every hour
3. **Request increase** - Update key with higher `rate_limit_requests`

### High API Key Usage

Monitor usage to detect issues:

```python
# Check key stats
keys = list_api_keys()
for key in keys:
    if key['total_requests'] > 10000:
        print(f"High usage: {key['name']} ({key['total_requests']} requests)")
```

---

## Audit & Compliance

### Audit Trail Questions

Track for compliance:

- When was each key created? (`created_at`)
- Who created it? (user_id)
- When was it rotated? (old_key_id → new_key_id)
- When was it revoked? (`is_active: false`)
- How often is it used? (`last_used_at`, `total_requests`)

### Log All Access

```python
# In api_key_auth.py - log successful authentication
async def get_user_by_api_key(api_key: str, db: AsyncSession):
    result = await get_user_by_api_key(api_key, db)
    user, api_key_record = result

    # Log successful use
    logger.info(
        f"API key accessed",
        extra={
            "api_key_id": api_key_record.id,
            "user_id": user.id,
            "timestamp": datetime.now()
        }
    )

    return user, api_key_record
```

---

## References

- [OAuth 2.0 Bearer Token](https://tools.ietf.org/html/rfc6750)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
