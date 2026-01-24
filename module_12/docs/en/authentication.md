# Authentication Patterns Guide

## Overview

This guide explains all authentication methods covered in Module 12, from basic JWT to advanced patterns like OAuth2 and WebAuthn.

## 1. JWT (JSON Web Tokens) - Beginner Edition

### What is JWT?

A JWT is a self-contained token that can be used for authentication and information exchange.

**Structure**: `header.payload.signature`

Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOjEsImV4cCI6MTcwMzMwMDAwMH0.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Parts**:
1. **Header**: Algorithm and type
   ```json
   {
     "alg": "HS256",
     "typ": "JWT"
   }
   ```

2. **Payload**: User data and claims
   ```json
   {
     "sub": 1,              // Subject (user ID)
     "exp": 1703300000,     // Expiration time
     "type": "access"       // Token type
   }
   ```

3. **Signature**: HMAC-SHA256 signature
   - Created with: `HMAC(header.payload, secret_key)`
   - Ensures token wasn't modified

### JWT Flow in Module 12

**Registration & Login**:
```
1. User submits credentials
2. Application hashes password and stores in DB
3. On login, password verified against hash
4. If valid, generate two tokens:
   - Access Token (30 min expiry)
   - Refresh Token (7 day expiry)
5. Return both tokens to client
```

**Using Access Token**:
```
1. Client stores access token
2. For each API request, includes in header:
   Authorization: Bearer <access_token>
3. Server validates token:
   - Signature verification
   - Expiration check
   - User exists and is active
4. If valid, execute request
5. If expired, client uses refresh token
```

**Token Refresh**:
```
1. Access token expires
2. Client sends refresh token to /api/v1/auth/refresh
3. Server validates refresh token
4. If valid, issue new access + refresh tokens
5. Client updates local storage
6. Continue with new access token
```

### Code Implementation

**Create Token**:
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

**Validate Token**:
```python
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None  # Invalid or expired
```

**Use in Endpoint**:
```python
@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user info (requires valid access token)"""
    return current_user
```

### Advantages of JWT

✅ **Stateless**: No session storage needed
✅ **Scalable**: Works across multiple servers
✅ **Standards-based**: RFC 7519
✅ **Self-contained**: All info in token
✅ **Mobile-friendly**: Works with mobile apps

### Disadvantages

❌ **No revocation**: Can't revoke token before expiry
❌ **Payload visible**: Not encrypted (only signed)
❌ **Token size**: Larger than session IDs
❌ **Refresh required**: Access tokens must be refreshed

### Best Practices

1. **Secret Key**
   - Use strong, random key (256+ bits)
   - Store in environment variables
   - Never hardcode

2. **Expiry Times**
   - Access tokens: 15-30 minutes
   - Refresh tokens: 7-30 days
   - Adjust based on security needs

3. **HTTPS Only**
   - Always use HTTPS in production
   - Tokens are vulnerable to man-in-the-middle

4. **Secure Storage**
   - Client: HTTP-only cookies or secure local storage
   - Server: Environment variable (never in code)

---

## 2. OAuth2 - Advanced Edition (Planned)

### What is OAuth2?

OAuth2 is an authorization framework allowing users to login with third-party providers (Google, GitHub, etc.) without sharing passwords.

### Flow Overview

**Authorization Code Flow** (most common):

```
1. User clicks "Login with Google"
2. Redirect to Google login page
3. User grants permission
4. Google redirects back with authorization code
5. Backend exchanges code for access token
6. Backend queries Google for user info
7. Create/link user in our database
8. Issue our own JWT tokens
9. Redirect to frontend with tokens
```

### Benefits

✅ Users don't create new passwords
✅ Leverages existing accounts (Google, GitHub)
✅ Secure (authorization code, not password)
✅ Reduced password breach risk
✅ Better user experience

### Implementation Example (Planned)

```python
# authlib configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')

    # Create or link user
    user = await get_or_create_user(db, user_info)

    # Issue our tokens
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, ...}
```

---

## 3. API Keys - Advanced Edition (Planned)

### What is an API Key?

A long, unique string that identifies an application or user for programmatic access.

Format: `mlr_<32_random_bytes>`

### Use Cases

- Server-to-server communication
- CI/CD pipelines
- Third-party integrations
- Machine-to-machine access

### Properties

```python
class APIKey(Base):
    key_hash: str                    # SHA256 hash (stored)
    key_prefix: str                  # First 8 chars (for display)
    scopes: List[str]                # Permissions ["read:models", "write:models"]
    expires_at: Optional[datetime]   # Expiration
    is_active: bool                  # Can be revoked
```

### Validation Flow

```
1. Client sends API key in header or body
2. Hash the key: SHA256(key)
3. Look up key_hash in database
4. Verify is_active and not expired
5. Check request matches allowed scopes
6. Execute request or reject with 403
```

### Advantages vs JWT

| Feature | JWT | API Key |
|---------|-----|---------|
| Stateless | Yes | No |
| Revocation | Difficult | Easy |
| Scoping | Limited | Detailed |
| Rotation | Via refresh | Via rotation |
| Use Case | User auth | Service auth |

---

## 4. WebAuthn/Passkeys - Advanced Edition (Planned)

### What is WebAuthn?

Web Authentication (WebAuthn) allows passwordless login using biometrics (fingerprint, face) or hardware keys.

### Browser Support

✅ Chrome/Edge 67+
✅ Firefox 60+
✅ Safari 13+
✅ Mobile browsers

### Registration Flow

```
1. User clicks "Setup Passkey"
2. Browser/device prompts for biometric/PIN
3. Creates public-private key pair
4. Sends public key to server
5. Server stores public key
6. Device keeps private key (never sent)
```

### Authentication Flow

```
1. User clicks "Login with Passkey"
2. Server creates random challenge
3. Browser prompts for biometric
4. Device signs challenge with private key
5. Client sends signed challenge to server
6. Server verifies signature with stored public key
7. If valid, user is authenticated
```

### Benefits

✅ No passwords to remember
✅ Phishing resistant (device won't unlock)
✅ Fast (no password typing)
✅ Secure (cryptographic keys)
✅ Works across devices

### Implementation Overview (Planned)

```python
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response
)

@router.post("/webauthn/register/begin")
async def webauthn_register_begin(
    current_user: User = Depends(get_current_user)
):
    """Generate challenge for WebAuthn registration"""
    options = generate_registration_options(
        rp_id="example.com",
        rp_name="ML Registry",
        user_id=str(current_user.id),
        user_name=current_user.username
    )
    # Store challenge in session temporarily
    return options

@router.post("/webauthn/register/complete")
async def webauthn_register_complete(
    current_user: User,
    credential: dict,  # Response from browser
    db: AsyncSession
):
    """Complete WebAuthn registration"""
    # Verify credential with stored challenge
    verified = verify_registration_response(
        credential=credential,
        expected_challenge=session_challenge,
        expected_origin="https://example.com",
        expected_rp_id="example.com"
    )

    # Store public key
    new_credential = WebAuthnCredential(
        user_id=current_user.id,
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key
    )
    db.add(new_credential)
    await db.commit()
```

---

## Comparison Table

| Feature | JWT | OAuth2 | API Key | WebAuthn |
|---------|-----|--------|---------|----------|
| **Passwordless** | No | Yes | N/A | Yes |
| **3rd Party** | No | Yes | No | Yes |
| **Stateless** | Yes | No | No | No |
| **Revocable** | No | Yes | Yes | Yes |
| **User Friendly** | Moderate | Very | Low | Very |
| **Machine Readable** | Yes | Yes | Yes | No |
| **Phishing Resistant** | No | No | Yes | Yes |

---

## When to Use Each Method

### Use JWT When...
- Building API for own frontend
- Stateless scaling needed
- Standard token-based auth desired
- Short-lived sessions (< 1 hour)

### Use OAuth2 When...
- Want social login (Google, GitHub, etc.)
- Users expect familiar login
- Delegating authentication to provider
- B2C applications

### Use API Keys When...
- Service-to-service communication
- Developer API access
- Long-lived credentials needed
- Fine-grained permissions required

### Use WebAuthn When...
- Maximum security desired
- Phishing resistance important
- Modern user base (mobile + desktop)
- Passwordless experience needed

---

## Security Recommendations

### 1. Password Security
- Minimum 12 characters
- Require complexity (upper, lower, number, symbol)
- Never log passwords
- Use bcrypt with 12+ rounds

### 2. Token Security
- Generate from cryptographically secure source
- Use at least 256-bit entropy
- Store secrets in environment only
- Rotate keys periodically
- Use HTTPS always

### 3. Rate Limiting
- Limit failed login attempts
- Implement exponential backoff
- Block after threshold (e.g., 5 attempts)
- Log suspicious activity

### 4. Monitoring
- Log authentication events
- Alert on failed attempts
- Track token generation
- Monitor unusual patterns

---

## Troubleshooting

### Invalid Token Error
**Problem**: "Could not validate credentials"

**Solutions**:
- Token expired? → Use refresh endpoint
- Token tampered? → Invalid signature
- Wrong algorithm? → Check settings
- Secret key changed? → Re-login

### Expired Refresh Token
**Problem**: Cannot get new access token

**Solutions**:
- Refresh token expired (7 days)
- User was deleted
- Force re-login

### CORS Errors with OAuth
**Problem**: "No 'Access-Control-Allow-Origin' header"

**Solutions**:
- Ensure callback URL registered with provider
- CORS headers configured correctly
- Frontend and backend on same domain (dev) or whitelisted (prod)

---

## Further Reading

- [JWT.io - RFC 7519](https://jwt.io/)
- [OAuth2 Specification](https://oauth.net/2/)
- [WebAuthn Guide](https://webauthn.guide/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## Summary

| Edition | Methods | Goals |
|---------|---------|-------|
| **Beginner** | JWT | Learn authentication fundamentals |
| **Advanced** | JWT + OAuth2 + API Keys + WebAuthn | Understand modern auth patterns |

Module 12 provides hands-on experience with all these patterns, preparing you for real-world web development challenges.
