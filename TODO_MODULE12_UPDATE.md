# Module 12 - Updated TODO List Based on Audit

**Status:** Audit completed, gaps identified, implementation plan ready

---

## Current Status vs Requirements

### Original TODO:
```
Модуль 12. Авторизація та Аутентифікація
├─ Основи FastAPI для REST застосунків (CRUD)
├─ Докеризація FastAPI застосунків
├─ Авторизація у FastAPI (JWT)
├─ Додати авторизацію
└─ Додати ролі для авторизації
```

### Audit Result:
```
✅ Основи FastAPI для REST застосунків (CRUD)        - COMPLETE
✅ Докеризація FastAPI застосунків                   - COMPLETE
✅ Авторизація у FastAPI (JWT)                       - COMPLETE
✅ Додати авторизацію (JWT + ownership)              - COMPLETE
⚠️  Додати ролі для авторизації                       - PARTIAL (33%)
    ├─ ❌ Beginner Edition - NO roles
    ├─ ❌ Intermediate Edition - NO roles
    └─ ✅ Advanced Edition - RBAC exists but not fully used
```

---

## Gap Analysis

### Critical Gaps:

1. **No RBAC in Beginner Edition**
   - User model has no `role` field
   - No concept of admin/moderator
   - Students learn JWT but not RBAC
   - **Impact:** Students miss fundamental authorization pattern

2. **No RBAC in Intermediate Edition**
   - Blog API missing moderator role example
   - No admin functions (delete any post)
   - No role-based visibility
   - **Impact:** Students don't see RBAC progression, don't understand WHY roles matter

3. **Advanced Edition: Decorator Not Used**
   - `require_roles()` function defined but never called
   - Manual role checks in endpoints instead of using decorator pattern
   - **Impact:** Bad practice example, confusing for students learning from code

4. **OAuth2 Not Implemented**
   - Documentation exists (guide in docs/en/authentication.md)
   - No actual code implementation
   - No Google login
   - No GitHub login
   - **Impact:** Critical gap - modern apps MUST support social login

5. **No API Key Support**
   - Missing service-to-service authentication
   - **Impact:** Can't demonstrate API security for backend-backend communication

---

## Updated TODO: Implementation Plan

### PHASE 1: RBAC in Beginner & Intermediate (High Priority)
**Effort:** ~2 hours total

#### Task 1.1: Add Roles to Beginner Edition (30 min)
```
[ ] Update beginner_edition/todo_app/app/models.py
    [ ] Add role field to User model
    [ ] Create UserRole enum (user/admin)
    [ ] Set default role: "user"

[ ] Update beginner_edition/todo_app/app/auth.py
    [ ] Add role to JWT token payload
    [ ] Include role in get_current_user() response

[ ] Update beginner_edition/todo_app/README.md
    [ ] Document role-based access concept
    [ ] Show role in user creation example

[ ] Create beginner_edition/standalone_examples/5_roles_basics.py (NEW!)
    [ ] Demonstrate role checking
    [ ] Show admin vs user access patterns
```

#### Task 1.2: Add Moderator Role to Intermediate Edition (45 min)
```
[ ] Update intermediate_edition/blog_api/app/models.py
    [ ] Add role field to User model
    [ ] Create UserRole enum (user/moderator/admin)
    [ ] Set default role: "user"

[ ] Update intermediate_edition/blog_api/app/auth.py
    [ ] Add get_admin_user() dependency
    [ ] Add check_moderator() helper
    [ ] Include role in tokens

[ ] Update intermediate_edition/blog_api/app/main.py
    [ ] Moderators can edit ANY post (not just own)
    [ ] Admins can delete any post
    [ ] Regular users can only edit own
    [ ] Show role-based filtering in list_posts()

[ ] Add endpoint examples:
    [ ] PUT /posts/{post_id} - with moderator check
    [ ] DELETE /posts/{post_id} - with admin check
    [ ] GET /posts - filtered by role-based visibility

[ ] Update intermediate_edition/blog_api/README.md
    [ ] Document role system
    [ ] Show moderator and admin use cases
    [ ] Explain when to use roles

[ ] Add moderator test cases in tests/test_auth.py
```

---

### PHASE 2: Fix Advanced Edition RBAC Usage (Medium Priority)
**Effort:** ~45 min

#### Task 2.1: Use require_roles() Decorator Properly
```
[ ] Refactor advanced_edition/ml_registry_app/app/api/v1/models.py
    [ ] Replace manual role checks with @require_roles() decorator
    [ ] Update @router.get("/") - add visibility filtering
    [ ] Update @router.put("/{model_id}") - use require_roles()
    [ ] Update @router.delete("/{model_id}") - admin only
    [ ] Remove manual if/else role checking

[ ] Refactor advanced_edition/ml_registry_app/app/api/v1/experiments.py
    [ ] Add role-based access to experiments
    [ ] Only admins/creators can access

[ ] Update advanced_edition/ml_registry_app/app/api/v1/users.py
    [ ] Add @require_roles(UserRole.admin) for user management
    [ ] Show admin-only endpoints

[ ] Update advanced_edition/ml_registry_app/README.md
    [ ] Document @require_roles() decorator usage
    [ ] Show before/after comparison
    [ ] Explain decorator pattern benefits

[ ] Add tests for RBAC in tests/test_auth.py
    [ ] Test require_roles() decorator
    [ ] Test role enforcement
```

---

### PHASE 3: Implement OAuth2 Social Login (High Priority) 🔥
**Effort:** ~4 hours

This is CRITICAL for modern applications!

#### Task 3.1: Create OAuth2 Base Implementation
```
[ ] Add authlib to requirements.txt (all 3 editions)

[ ] Create advanced_edition/ml_registry_app/app/auth/oauth2.py
    [ ] Implement OAuth2 base class
    [ ] Token exchange logic
    [ ] User creation from OAuth2 data
    [ ] User linking if already exists

[ ] Create OAuth2 configuration
    [ ] Google OAuth2 client setup
    [ ] GitHub OAuth2 client setup
    [ ] Generic OAuth2 provider support

[ ] Create /root/goit/python_web/module_12/advanced_edition/examples/oauth2_google.py
    [ ] Working example with Google login
    [ ] Complete flow from start to finish
    [ ] Environment variables setup
```

#### Task 3.2: Add OAuth2 Endpoints
```
[ ] Add advanced_edition/ml_registry_app/app/api/v1/auth.py
    [ ] POST /auth/google - Google login endpoint
    [ ] POST /auth/github - GitHub login endpoint
    [ ] POST /auth/callback - OAuth2 callback handler
    [ ] GET /auth/me/providers - Show linked accounts

[ ] Add OAuth2 models
    [ ] OAuthAccount model (track social accounts)
    [ ] Link OAuth2 account to User
    [ ] Support multiple social accounts per user
```

#### Task 3.3: Create Jupyter Notebook for OAuth2
```
[ ] Create Module12_OAuth2_Integration.ipynb
    [ ] Part 1: Theory - How OAuth2 works
    [ ] Part 2: Google login flow (runnable example)
    [ ] Part 3: GitHub login flow (runnable example)
    [ ] Part 4: Best practices and security
    [ ] Part 5: Linking multiple OAuth2 accounts
```

#### Task 3.4: Update Documentation
```
[ ] Create docs/en/oauth2_integration.md
    [ ] Setup instructions
    [ ] Google console setup
    [ ] GitHub app setup
    [ ] Implementation steps
    [ ] Security considerations

[ ] Add OAuth2 section to docs/en/authentication.md
    [ ] Replace pseudocode with actual code
    [ ] Link to implementation

[ ] Update advanced_edition/README.md
    [ ] Document OAuth2 support
    [ ] Link to oauth2_integration.md
```

---

### PHASE 4: Add API Key Authentication (Medium Priority)
**Effort:** ~2.5 hours

#### Task 4.1: API Key Models & Generation
```
[ ] Create advanced_edition/ml_registry_app/app/models/api_key.py
    [ ] APIKey model
    [ ] Key generation logic
    [ ] Expiration support
    [ ] Scopes/permissions per key

[ ] Add to advanced_edition/ml_registry_app/app/models/__init__.py
```

#### Task 4.2: API Key Authentication
```
[ ] Create advanced_edition/ml_registry_app/app/auth/api_key.py
    [ ] Validate API key header
    [ ] Load user from API key
    [ ] Check expiration

[ ] Update advanced_edition/ml_registry_app/app/api/v1/auth.py
    [ ] POST /auth/api-keys - create new key
    [ ] GET /auth/api-keys - list keys
    [ ] DELETE /auth/api-keys/{key_id} - revoke key
    [ ] POST /auth/api-keys/{key_id}/rotate - rotate key
```

#### Task 4.3: API Key Usage Examples
```
[ ] Create advanced_edition/examples/api_key_usage.py
    [ ] Generate key
    [ ] Use key for requests
    [ ] Handle expiration
    [ ] Rotate key

[ ] Update docs/en/authentication.md
    [ ] API key section
    [ ] When to use API keys vs OAuth2
```

---

### PHASE 5: Update Learning Materials (Medium Priority)
**Effort:** ~2 hours

#### Task 5.1: Update Jupyter Notebooks
```
[ ] Update Module12_Complete_Learning_Path.ipynb
    [ ] Add RBAC section to intermediate part
    [ ] Add moderator role examples
    [ ] Add comparison of auth patterns across levels
    [ ] Update advanced section with decorator usage

[ ] Create Module12_OAuth2_Guide.ipynb (new)
    [ ] Complete OAuth2 walkthrough
    [ ] Google + GitHub implementation
    [ ] Practical examples with code
```

#### Task 5.2: Update Learning Path Documentation
```
[ ] Update docs/LEARNING_PATH.md
    [ ] Add RBAC learning path
    [ ] Add OAuth2 learning path
    [ ] Show progression from JWT → RBAC → OAuth2

[ ] Create docs/AUTHORIZATION_PROGRESSION.md (new)
    [ ] Beginner: JWT + Ownership
    [ ] Intermediate: RBAC + Moderators
    [ ] Advanced: Full RBAC + OAuth2 + API Keys
    [ ] Diagram showing progression

[ ] Update docs/CHECKLIST.md
    [ ] Add RBAC verification items
    [ ] Add OAuth2 verification items
    [ ] Add API key verification items
```

#### Task 5.3: Create Standalone RBAC Example
```
[ ] Create beginner_edition/standalone_examples/5_rbac_basics.py (new!)
    [ ] Demonstrate role concept
    [ ] Show role checking patterns
    [ ] User vs Admin operations
    [ ] Can be run and modified like others

[ ] Create beginner_edition/standalone_examples/README.md update
    [ ] Document 5_rbac_basics.py
    [ ] Explain progression
```

---

### PHASE 6: Optional Extensions (Low Priority)
**Effort:** ~10 hours (optional)

#### Task 6.1: MFA/2FA Support
```
[ ] Implement TOTP (Time-based One-Time Password)
[ ] Google Authenticator support
[ ] Backup codes
[ ] Recovery options
```

#### Task 6.2: WebAuthn/Passkeys
```
[ ] Implement WebAuthn registration
[ ] WebAuthn authentication
[ ] Fallback to password + security key
```

#### Task 6.3: Audit Logging
```
[ ] Log all authentication events
[ ] Log all authorization events
[ ] Create audit trail
[ ] Query audit logs
```

---

## Implementation Order (Recommended)

### Week 1: RBAC Progression
1. ✓ Phase 1: Add RBAC to beginner/intermediate (2h)
2. ✓ Phase 2: Fix advanced RBAC decorator usage (45m)

### Week 2: OAuth2 Implementation
3. ✓ Phase 3: Implement OAuth2 (4h)

### Week 3: Additional Features & Documentation
4. ✓ Phase 4: Add API keys (2.5h)
5. ✓ Phase 5: Update learning materials (2h)

### Total: ~11 hours for complete professional implementation

---

## Testing Checklist

### RBAC Testing
```
[ ] Beginner: User can see own todos, admin can see all
[ ] Intermediate: Moderators can edit any post, admins can delete any
[ ] Advanced: require_roles() decorator works correctly
[ ] Verify token includes role field
[ ] Verify JWT validation includes role checks
```

### OAuth2 Testing
```
[ ] Google login flow works end-to-end
[ ] GitHub login flow works end-to-end
[ ] User created on first OAuth2 login
[ ] User linked on subsequent OAuth2 login with same account
[ ] Multiple OAuth2 accounts can be linked to single user
[ ] Token refresh works for OAuth2 users
[ ] Logout works properly
```

### API Key Testing
```
[ ] API key can be generated
[ ] API key grants access
[ ] Expired API key is rejected
[ ] Key rotation works
[ ] Revoked key no longer grants access
[ ] API key scopes are respected
```

---

## Files to Create/Modify Summary

### New Files:
- [ ] `beginner_edition/standalone_examples/5_rbac_basics.py`
- [ ] `advanced_edition/examples/oauth2_google.py`
- [ ] `advanced_edition/examples/api_key_usage.py`
- [ ] `Module12_OAuth2_Integration.ipynb`
- [ ] `docs/AUTHORIZATION_PROGRESSION.md`
- [ ] `docs/en/oauth2_integration.md`
- [ ] `advanced_edition/ml_registry_app/app/auth/oauth2.py`
- [ ] `advanced_edition/ml_registry_app/app/models/api_key.py`
- [ ] `advanced_edition/ml_registry_app/app/auth/api_key.py`

### Modified Files:
- [ ] `beginner_edition/todo_app/app/models.py` (add role)
- [ ] `beginner_edition/todo_app/app/auth.py` (add role to JWT)
- [ ] `beginner_edition/todo_app/README.md`
- [ ] `intermediate_edition/blog_api/app/models.py` (add role)
- [ ] `intermediate_edition/blog_api/app/auth.py` (add role checking)
- [ ] `intermediate_edition/blog_api/app/main.py` (add moderator/admin logic)
- [ ] `intermediate_edition/blog_api/README.md`
- [ ] `advanced_edition/ml_registry_app/app/api/v1/models.py` (use decorator)
- [ ] `advanced_edition/ml_registry_app/app/api/v1/experiments.py` (add RBAC)
- [ ] `advanced_edition/ml_registry_app/app/api/v1/users.py` (add admin endpoints)
- [ ] `advanced_edition/ml_registry_app/requirements.txt` (add authlib)
- [ ] `advanced_edition/README.md`
- [ ] `Module12_Complete_Learning_Path.ipynb` (update)
- [ ] `docs/LEARNING_PATH.md` (add RBAC/OAuth2 sections)
- [ ] `docs/CHECKLIST.md` (add new items)
- [ ] `docs/en/authentication.md` (update with actual code)

---

## Success Criteria

### For RBAC:
- ✅ Beginner students understand role concept
- ✅ Intermediate students see RBAC benefits via moderator example
- ✅ Advanced students follow decorator pattern best practices
- ✅ Clear progression: basic → roles → permissions

### For OAuth2:
- ✅ Students can implement Google social login
- ✅ Students can implement GitHub social login
- ✅ Working end-to-end examples
- ✅ Documentation covers setup and security

### For API Keys:
- ✅ Students understand service-to-service auth
- ✅ Can generate, use, and rotate API keys
- ✅ Understand scopes and permissions

### Overall:
- ✅ Module 12 covers modern authentication patterns
- ✅ Progressive complexity: JWT → RBAC → OAuth2 → API Keys
- ✅ Practical working examples in all editions
- ✅ Students can build production-ready auth systems

---

## Effort Estimate Summary

| Phase | Task | Time | Priority | Status |
|-------|------|------|----------|--------|
| 1 | RBAC in Beginner | 30 min | HIGH | Not Started |
| 1 | RBAC in Intermediate | 45 min | HIGH | Not Started |
| 2 | Fix Advanced RBAC Decorator | 45 min | MEDIUM | Not Started |
| 3 | OAuth2 Implementation | 4h | HIGH | Not Started |
| 4 | API Keys | 2.5h | MEDIUM | Not Started |
| 5 | Learning Materials | 2h | MEDIUM | Not Started |
| 6 | Optional Extensions | 10h | LOW | Not Started |
| | **TOTAL ESSENTIAL** | **~8 hours** | | |

---

**Audit Completed:** 2026-01-24
**Status:** Ready for implementation
**Confidence Level:** High - Clear requirements and implementation path

