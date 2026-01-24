"""
5. RBAC (Role-Based Access Control) Basics
============================================

Demonstrates how to implement basic role-based access control in FastAPI.

Topics covered:
- User roles (user vs admin)
- Role checking in functions
- Different access levels based on roles
- Role field in JWT tokens

Run this file: python 5_rbac_basics.py
Then visit: http://localhost:8000/docs

CONCEPT: Different users have different permissions based on their role.
- Regular users can only manage their own resources
- Admins can manage everything
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime, timedelta, timezone
import jwt

app = FastAPI(title="RBAC Basics", version="1.0.0")

# ============================================================================
# STEP 1: Define roles
# ============================================================================

class UserRole(str, Enum):
    """Define available user roles."""
    user = "user"    # Regular user
    admin = "admin"  # Administrator


# ============================================================================
# STEP 2: Define schemas (validation models)
# ============================================================================

class UserCreate(BaseModel):
    """Schema for creating a user."""
    username: str
    password: str
    role: UserRole = UserRole.user  # Default to user role


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str
    role: str


# ============================================================================
# STEP 3: In-memory user database (for demo)
# ============================================================================

users_db = {
    "alice": {
        "user_id": 1,
        "username": "alice",
        "password": "pass123",  # In real app, store HASHED password
        "role": UserRole.user,
    },
    "bob": {
        "user_id": 2,
        "username": "bob",
        "password": "adminpass",
        "role": UserRole.admin,  # Bob is admin
    },
}

# JWT config
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


# ============================================================================
# STEP 4: Helper functions
# ============================================================================

def create_access_token_with_role(user_id: int, role: str) -> str:
    """Create JWT token with role information."""
    to_encode = {
        "sub": str(user_id),
        "role": role,  # 🔑 Include role in token
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    encoded = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded


def decode_token(token: str) -> dict:
    """Decode JWT token and get user info with role."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role", UserRole.user)  # 🔑 Get role from token
        return {"user_id": int(user_id), "role": role}
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# ============================================================================
# STEP 5: Authentication dependency
# ============================================================================

async def get_current_user(token: str = Depends(lambda: None)) -> dict:
    """Extract user info from token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return decode_token(token)


# ============================================================================
# STEP 6: RBAC dependency - check if user is admin
# ============================================================================

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires admin role."""
    if user["role"] != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """Login and get JWT token with role."""
    # Find user
    user = users_db.get(credentials.username)

    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create token with role
    token = create_access_token_with_role(user["user_id"], user["role"].value)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"].value,
    }


# ============================================================================
# EXAMPLE 1: Regular user endpoint
# ============================================================================

@app.get("/api/user/profile")
def get_user_profile(user: dict = Depends(get_current_user)):
    """
    Get current user's profile.

    ✅ ALLOWED FOR: user, admin

    Why? Both regular users and admins should see their own profile.
    """
    return {
        "user_id": user["user_id"],
        "role": user["role"],
        "message": f"Hello {user['role']} user #{user['user_id']}",
    }


# ============================================================================
# EXAMPLE 2: Admin-only endpoint
# ============================================================================

@app.get("/api/admin/users")
def list_all_users(admin_user: dict = Depends(require_admin)):
    """
    List all users in the system.

    ✅ ALLOWED FOR: admin only
    ❌ REJECTED FOR: user

    Why? Only admins should access other users' data.
    """
    return {
        "message": "Admin access granted",
        "admin_user_id": admin_user["user_id"],
        "all_users": [
            {"user_id": 1, "username": "alice", "role": "user"},
            {"user_id": 2, "username": "bob", "role": "admin"},
        ],
    }


# ============================================================================
# EXAMPLE 3: Role-based action
# ============================================================================

@app.post("/api/admin/delete-user/{user_id}")
def delete_user(user_id: int, admin_user: dict = Depends(require_admin)):
    """
    Delete a user (admin only).

    ✅ ALLOWED FOR: admin
    ❌ REJECTED FOR: user

    Why? Only admins should delete users.
    """
    if user_id == admin_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    return {
        "message": f"User {user_id} deleted by admin {admin_user['user_id']}",
        "deleted_user_id": user_id,
        "deleted_by_admin_id": admin_user["user_id"],
    }


# ============================================================================
# EXAMPLE 4: Role-based visibility
# ============================================================================

@app.get("/api/data")
def get_data(user: dict = Depends(get_current_user)):
    """
    Get data with different content based on role.

    ✅ ALLOWED FOR: user, admin (different content)
    """
    if user["role"] == UserRole.admin:
        # Admins see everything
        return {
            "message": "Admin sees all data",
            "user_role": user["role"],
            "public_data": ["item1", "item2", "item3"],
            "sensitive_data": ["secret1", "secret2", "secret3"],  # Only for admin
            "analytics": {"total_users": 2, "total_items": 100},  # Only for admin
        }
    else:
        # Regular users see limited data
        return {
            "message": "User sees limited data",
            "user_role": user["role"],
            "public_data": ["item1", "item2", "item3"],
            # sensitive_data NOT included for regular users
        }


# ============================================================================
# KEY CONCEPTS DEMONSTRATED
# ============================================================================
"""
1. ROLE ENUM: UserRole defines available roles
   - user: Regular user
   - admin: Administrator

2. ROLE IN TOKEN: JWT token includes role field
   - Token payload: {"sub": user_id, "role": "user"}
   - Used to check permissions without database lookup

3. RBAC DEPENDENCIES:
   - get_current_user(): Any authenticated user
   - require_admin(): Only admin users

4. ROLE-BASED ENDPOINTS:
   - Some endpoints: only for authenticated users (any role)
   - Some endpoints: only for admin
   - Some endpoints: different behavior based on role

5. SECURITY PATTERN:
   - Always check role before returning sensitive data
   - Never trust role from URL/query params, only from token
   - Use dependencies to enforce role requirements
"""


# ============================================================================
# TESTING INSTRUCTIONS
# ============================================================================
"""
1. RUN THIS FILE:
   python 5_rbac_basics.py

2. OPEN INTERACTIVE DOCS:
   http://localhost:8000/docs

3. TEST STEPS:

   STEP A: Login as regular user (alice)
   ├─ POST /auth/login
   ├─ Body: {"username": "alice", "password": "pass123"}
   ├─ Copy the access_token from response
   └─ Click "Authorize" and paste token

   STEP B: Test as regular user
   ├─ GET /api/user/profile → ✅ Works
   ├─ GET /api/data → ✅ Works but sees less data
   └─ GET /api/admin/users → ❌ 403 Forbidden

   STEP C: Logout and login as admin (bob)
   ├─ POST /auth/login
   ├─ Body: {"username": "bob", "password": "adminpass"}
   ├─ Copy the access_token from response
   └─ Click "Authorize" and paste token

   STEP D: Test as admin
   ├─ GET /api/user/profile → ✅ Works
   ├─ GET /api/data → ✅ Works and sees sensitive data
   ├─ GET /api/admin/users → ✅ Works (list all users)
   └─ POST /api/admin/delete-user/1 → ✅ Works
"""


if __name__ == "__main__":
    print("🔐 RBAC Basics - Role-Based Access Control")
    print("=" * 50)
    print("Users available:")
    print("  • alice (user role): pass123")
    print("  • bob (admin role): adminpass")
    print()
    print("Start server: uvicorn 5_rbac_basics:app --reload")
    print("Docs: http://localhost:8000/docs")
