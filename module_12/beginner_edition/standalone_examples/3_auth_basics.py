"""
Authentication Basics - JWT & Password Hashing

Learn:
- Password hashing with bcrypt
- JWT token generation and validation
- Protected routes
- Token refresh

No database needed - everything in memory for learning.
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# ============================================================================
# CONFIGURATION
# ============================================================================

# Secret key for signing JWTs (should be in .env file in production)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserRegister(BaseModel):
    """User registration request."""
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str
    expires_in: int

class User(BaseModel):
    """User model."""
    username: str
    email: str

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Example
if __name__ == "__main__":
    password = "secret123"
    hashed = hash_password(password)
    print(f"\nPassword: {password}")
    print(f"Hash: {hashed}")
    print(f"Verify correct: {verify_password(password, hashed)}")
    print(f"Verify wrong: {verify_password('wrong', hashed)}")

# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_access_token(
    username: str,
    expires_delta: Optional[timedelta] = None
) -> Token:
    """
    Create a JWT access token.

    Args:
        username: The username to encode in token
        expires_delta: Optional expiration time (default: 30 minutes)

    Returns:
        Token object with token, type, and expiration
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Calculate expiration time
    expire = datetime.utcnow() + expires_delta

    # Payload to encode
    to_encode = {
        "sub": username,  # "subject" - who the token is for
        "exp": expire,    # expiration time
        "iat": datetime.utcnow()  # issued at
    }

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return Token(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds())
    )

def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and extract the username.

    Args:
        token: The JWT token to verify

    Returns:
        The username if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

# Example token usage
if __name__ == "__main__":
    print("\n=== TOKEN CREATION ===")
    token_data = create_access_token("alice")
    print(f"Token: {token_data.access_token[:50]}...")
    print(f"Type: {token_data.token_type}")
    print(f"Expires in: {token_data.expires_in} seconds")

    print("\n=== TOKEN VERIFICATION ===")
    username = verify_token(token_data.access_token)
    print(f"Verified username: {username}")

    print("\n=== INVALID TOKEN ===")
    username = verify_token("invalid.token.here")
    print(f"Invalid token result: {username}")

# ============================================================================
# IN-MEMORY USER STORE (for demo)
# ============================================================================

users_db = {}  # username -> {"password_hash": "...", "email": "..."}

def register_user(username: str, password: str, email: str) -> bool:
    """Register a new user."""
    if username in users_db:
        return False  # User exists

    users_db[username] = {
        "password_hash": hash_password(password),
        "email": email
    }
    print(f"✅ Registered user: {username}")
    return True

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials."""
    if username not in users_db:
        return False

    user = users_db[username]
    return verify_password(password, user["password_hash"])

# ============================================================================
# FASTAPI APP WITH AUTHENTICATION
# ============================================================================

app = FastAPI(title="Auth Basics")
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Extract and verify JWT token from Authorization header.

    Expected header: Authorization: Bearer <token>
    """
    token = credentials.credentials
    username = verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return username

# ============================================================================
# ROUTES
# ============================================================================

@app.post("/register", response_model=dict)
def register(user_data: UserRegister):
    """
    Register a new user.

    Request body:
    {
        "username": "alice",
        "password": "secret123",
        "email": "alice@example.com"
    }
    """
    if register_user(user_data.username, user_data.password, user_data.email):
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/login", response_model=Token)
def login(credentials: UserLogin):
    """
    Login with username and password.

    Request body:
    {
        "username": "alice",
        "password": "secret123"
    }

    Returns: JWT access token
    """
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Generate token
    token = create_access_token(credentials.username)
    return token

@app.get("/me", response_model=User)
async def get_me(username: str = Depends(get_current_user)):
    """
    Get current user info (requires valid token).

    Header:
    Authorization: Bearer <token>
    """
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = users_db[username]
    return User(username=username, email=user_data["email"])

@app.get("/protected", response_model=dict)
async def protected_route(username: str = Depends(get_current_user)):
    """
    Protected endpoint - requires valid JWT token.

    Usage:
    curl http://localhost:8000/protected \
      -H "Authorization: Bearer <token>"
    """
    return {
        "message": f"Hello, {username}! You have a valid token.",
        "user": username
    }

# ============================================================================
# EXAMPLE FLOW
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("AUTH BASICS - EXAMPLE FLOW")
    print("="*60)

    # Step 1: Register user
    print("\n1️⃣ REGISTER USER")
    register_user("alice", "secret123", "alice@example.com")
    register_user("bob", "password456", "bob@example.com")

    # Step 2: Generate token
    print("\n2️⃣ LOGIN & GET TOKEN")
    token = create_access_token("alice")
    print(f"Token type: {token.token_type}")
    print(f"Expires in: {token.expires_in} seconds")
    print(f"Token (truncated): {token.access_token[:50]}...")

    # Step 3: Verify token
    print("\n3️⃣ VERIFY TOKEN")
    username = verify_token(token.access_token)
    print(f"Token verified for user: {username}")

    # Step 4: Show API usage
    print("\n4️⃣ START SERVER")
    print("Run: python auth_basics.py")
    print("\nThen try:")
    print("  1. Register: curl -X POST http://localhost:8000/register \\")
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"username":"alice","password":"secret123","email":"alice@example.com"}\'')
    print()
    print("  2. Login: curl -X POST http://localhost:8000/login \\")
    print("       -d 'username=alice&password=secret123'")
    print()
    print("  3. Get token and use it:")
    print("       curl http://localhost:8000/protected \\")
    print("         -H 'Authorization: Bearer <token>'")
    print()

    # Uncomment to start server
    # uvicorn.run(app, host="0.0.0.0", port=8000)
