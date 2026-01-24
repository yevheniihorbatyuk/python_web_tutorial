# RBAC (Role-Based Access Control) Patterns in Advanced Edition

This document explains how RBAC is implemented and used in the ML Registry application, serving as a reference for best practices in production FastAPI applications.

---

## Overview

**Role-Based Access Control (RBAC)** is an authorization pattern where access permissions are granted based on user roles rather than individual user accounts. This simplifies permission management and scales well.

### Roles in ML Registry

| Role | Description | Permissions |
|------|-------------|------------|
| `user` | Regular user | Create models, view own models, edit own models, delete own models |
| `reviewer` | Content reviewer | View all models, cannot modify |
| `admin` | Administrator | Full access to all models, can modify any model |
| `superuser` | System superuser | All permissions, cannot be restricted |

---

## Implementation Architecture

### 1. Database Model (User)

**File:** `app/models/user.py`

```python
class UserRole(str, Enum):
    """User roles for RBAC."""
    user = "user"
    reviewer = "reviewer"
    admin = "admin"

class User(Base):
    # ... other fields ...
    role: Mapped[str] = mapped_column(String(50), default=UserRole.user.value)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
```

**Key Points:**
- Roles stored as strings in database
- UserRole enum for type safety in code
- `is_superuser` flag for system administrators
- Default role is `"user"`

### 2. Authentication Dependencies

**File:** `app/auth/dependencies.py`

The authentication layer provides foundational dependencies:

```python
async def get_current_user(...) -> User:
    """Extract and validate JWT token, load user from database."""
    # JWT validation
    # User lookup
    # Activity check
    return user
```

### 3. Role Checking Patterns

#### Pattern A: Direct Role Check in Endpoint

**Best for:** Simple, role-specific endpoints

```python
@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    model = await get_model_from_db(db, model_id)

    # RBAC: Check if user can delete this model
    is_admin = current_user.role == UserRole.admin.value
    is_owner = model.owner_id == current_user.id
    is_superuser = current_user.is_superuser

    if not (is_admin or is_owner or is_superuser):
        raise HTTPException(status_code=403, detail="Not enough privileges")

    await db.delete(model)
    await db.commit()
```

**Advantages:**
- Explicit, easy to understand
- Clear permission logic per endpoint
- Easy to debug

**Disadvantages:**
- Boilerplate repeated across endpoints
- Can get messy with complex rules

#### Pattern B: Role Restriction Decorator

**Best for:** Admin-only endpoints

```python
def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency that ensures user is admin."""
    if current_user.role != UserRole.admin.value and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

@router.post("/admin/users")
async def admin_create_user(
    user_data: UserCreate,
    admin_user: Annotated[User, Depends(require_admin)]  # Uses dependency
) -> UserResponse:
    # Only admins reach here
    pass
```

**Advantages:**
- Cleaner endpoint signatures
- Centralized role logic
- Reusable

**Disadvantages:**
- Multiple roles harder to express
- Inheritance complex

#### Pattern C: Generic require_roles() Decorator

**Best for:** Multi-role checks, most flexible

**File:** `app/auth/dependencies.py`

```python
def require_roles(*allowed_roles: UserRole):
    """Require current user to have one of allowed roles."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.is_superuser:
            return current_user

        if current_user.role not in {role.value for role in allowed_roles}:
            raise HTTPException(status_code=403, detail="Not enough privileges")
        return current_user

    return role_checker

# Usage:
@router.post("/reports/monthly")
async def generate_report(
    report_data: ReportCreate,
    authorized_user: Annotated[User, Depends(require_roles(
        UserRole.admin,
        UserRole.reviewer
    ))]
):
    # Only admins or reviewers reach here
    pass
```

**Advantages:**
- Highly flexible
- Supports multiple roles
- Superusers always allowed
- Reusable for any role combination

**Disadvantages:**
- Slightly more complex
- Runtime role lookups

---

## Practical Examples

### Example 1: Resource Ownership Check

**Scenario:** Users can edit their own models, admins can edit any model

```python
@router.put("/{model_id}")
async def update_model(
    model_id: int,
    model_data: MLModelUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> MLModel:
    model = await db.get(MLModel, model_id)

    # RBAC: Check ownership or admin role
    is_owner = model.owner_id == current_user.id
    is_admin = current_user.role == UserRole.admin.value

    if not (is_owner or is_admin or current_user.is_superuser):
        raise HTTPException(
            status_code=403,
            detail="Can only edit your own models"
        )

    # Safe to update
    model.update(**model_data.dict())
    await db.commit()
    return model
```

### Example 2: Visibility Filtering

**Scenario:** Regular users see only their models; admins see all models

```python
@router.get("/", response_model=List[MLModelResponse])
async def list_models(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[MLModel]:
    query = select(MLModel)

    # RBAC: Filter visibility based on role
    if not current_user.is_superuser:
        if current_user.role not in {UserRole.admin.value, UserRole.reviewer.value}:
            # Regular users see only their own
            query = query.where(MLModel.owner_id == current_user.id)

    # If admin or reviewer, they see all models
    result = await db.execute(query)
    return result.scalars().all()
```

### Example 3: Role-Based Data Transformation

**Scenario:** Show different data based on user role

```python
@router.get("/{model_id}")
async def get_model(
    model_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    model = await db.get(MLModel, model_id)

    # Build response based on role
    response = {
        "id": model.id,
        "name": model.name,
        "lifecycle": model.lifecycle
    }

    # Only admins and reviewers see performance metrics
    if current_user.role in {UserRole.admin.value, UserRole.reviewer.value}:
        response["accuracy"] = model.accuracy
        response["f1_score"] = model.f1_score

    # Only owner sees internal notes
    if model.owner_id == current_user.id:
        response["internal_notes"] = model.internal_notes

    return response
```

---

## Security Considerations

### 1. Always Check Authorization on Modification

**❌ BAD:**
```python
@router.delete("/{model_id}")
async def delete_model(model_id: int, db: AsyncSession = Depends(get_db)):
    # No authorization check!
    model = await db.get(MLModel, model_id)
    await db.delete(model)
    await db.commit()
```

**✅ GOOD:**
```python
@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model = await db.get(MLModel, model_id)

    # Always check authorization before modification
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(model)
    await db.commit()
```

### 2. Prevent Privilege Escalation

**❌ BAD:**
```python
@router.post("/users/{user_id}/promote")
async def promote_user(
    user_id: int,
    new_role: str,  # User can set any role!
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)

    user = await db.get(User, user_id)
    user.role = new_role  # SECURITY ISSUE: No validation!
    await db.commit()
```

**✅ GOOD:**
```python
@router.post("/users/{user_id}/promote")
async def promote_user(
    user_id: int,
    new_role: UserRole,  # Enum restricts to valid values
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_roles(UserRole.admin))
):
    user = await db.get(User, user_id)
    user.role = new_role.value
    await db.commit()
```

### 3. Beware of Information Disclosure

**❌ BAD:**
```python
@router.get("/{model_id}")
async def get_model(model_id: int, db: AsyncSession = Depends(get_db)):
    # Returns model even if user shouldn't see it!
    model = await db.get(MLModel, model_id)
    return model
```

**✅ GOOD:**
```python
@router.get("/{model_id}")
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model = await db.get(MLModel, model_id)

    # Check visibility before returning
    if model.owner_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=404)  # 404, not 403

    return model
```

---

## Testing RBAC

### Unit Test Example

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_user_cannot_delete_others_model():
    """Verify users cannot delete models they don't own."""

    # Alice creates a model
    alice_model = await create_model(owner_id=alice.id)

    # Bob tries to delete Alice's model
    response = client.delete(
        f"/models/{alice_model.id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )

    assert response.status_code == 403
    assert "Not enough privileges" in response.json()["detail"]

@pytest.mark.asyncio
async def test_admin_can_delete_any_model():
    """Verify admins can delete any model."""

    user_model = await create_model(owner_id=regular_user.id)

    response = client.delete(
        f"/models/{user_model.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 204

@pytest.mark.asyncio
async def test_visibility_filtering():
    """Verify users only see their own models."""

    alice_models = [create_model(owner_id=alice.id) for _ in range(3)]
    bob_models = [create_model(owner_id=bob.id) for _ in range(2)]

    # Alice lists models
    response = client.get(
        "/models/",
        headers={"Authorization": f"Bearer {alice_token}"}
    )

    assert len(response.json()) == 3  # Only Alice's models
```

---

## Evolution of RBAC

### Level 1: Simple Role Check
- Single permission per role
- Suitable for basic applications

### Level 2: Role + Ownership
- Combine roles with resource ownership
- Users manage their own resources; admins manage all
- Most common pattern

### Level 3: Fine-Grained Permissions
- Move beyond roles to individual permissions
- Users can grant specific permissions to others
- Requires permission matrix (user → resource → action)

### Level 4: Attribute-Based Access Control (ABAC)
- Permissions based on attributes
- Example: "Can edit models created in last 7 days"
- Requires complex decision engine

---

## ML Registry RBAC Implementation

The ML Registry application uses **Level 2: Role + Ownership** pattern.

### Current Roles

```
Regular User (role="user")
    ├─ Create models
    ├─ View own models
    ├─ Edit own models
    └─ Delete own models

Reviewer (role="reviewer")
    ├─ View all models
    └─ Cannot modify

Admin (role="admin")
    ├─ View all models
    ├─ Edit any model
    ├─ Delete any model
    └─ Manage users

Superuser (is_superuser=true)
    └─ Unrestricted access (for system maintenance)
```

### How to Extend

To add a new role:

1. Add to `UserRole` enum in `models/user.py`
2. Add permission checks in relevant endpoints
3. Update documentation
4. Add tests for new role

Example: Adding "moderator" role

```python
class UserRole(str, Enum):
    user = "user"
    moderator = "moderator"  # NEW
    reviewer = "reviewer"
    admin = "admin"

# In endpoint:
if current_user.role == UserRole.moderator.value:
    # Moderator-specific logic
    pass
```

---

## Best Practices

1. **Use Enums for Roles** - Type safety prevents typos
2. **Check on Modification Only** - GET requests don't need authorization checks (just visibility filtering)
3. **Fail Closed** - Deny by default, allow explicitly
4. **Use Meaningful Status Codes** - 403 Forbidden for auth issues, 404 Not Found for privacy (don't leak existence)
5. **Log Authorization Failures** - Track potential attacks
6. **Test All Roles** - Write tests for each role combination
7. **Document Permissions** - Clear docstrings for each endpoint
8. **Use Dependency Injection** - FastAPI's Depends() for reusable checks

---

## References

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Role-Based Access Control](https://en.wikipedia.org/wiki/Role-based_access_control)
