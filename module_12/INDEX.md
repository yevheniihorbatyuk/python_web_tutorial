# Module 12: Authentication & Authorization - Complete Index

**Last Updated:** January 24, 2026
**Status:** ✅ Core Features Complete (85-90%)

---

## 📋 Quick Navigation

### For Learners
- **Beginner:** Start with [beginner_edition/standalone_examples/5_rbac_basics.py](#-teaching-examples)
- **Intermediate:** Check [intermediate_edition/blog_api/README.md](#beginner-edition)
- **Advanced:** Review [RBAC_PATTERNS.md](#-rbac-implementation-guide) and [API_KEY_GUIDE.md](#-api-key-authentication)

### For Developers
- **RBAC Guide:** [advanced_edition/RBAC_PATTERNS.md](#-rbac-implementation-guide)
- **API Key Implementation:** [advanced_edition/API_KEY_GUIDE.md](#-api-key-authentication)
- **OAuth2 Setup:** [advanced_edition/oauth2_integration_example.py](#-oauth2-integration)

### Implementation Details
- **What Changed:** [IMPLEMENTATION_SUMMARY.md](#-implementation-summary)
- **Audit Results:** [AUTHORIZATION_AUDIT.md](#-audit-results)
- **Implementation Plan:** [TODO_MODULE12_UPDATE.md](#-implementation-plan)

---

## 📚 Documentation Files

### 🔐 RBAC Implementation Guide
**Location:** `advanced_edition/RBAC_PATTERNS.md`

Comprehensive guide covering:
- Role hierarchy explanation
- 4 authorization patterns (direct check, admin dependency, role decorator, generic decorator)
- Practical examples from ML Registry
- Security best practices
- Testing strategies
- Evolution of RBAC systems
- How to extend with custom roles

**Key Sections:**
- Pattern A: Direct role check in endpoint
- Pattern B: Role restriction decorator
- Pattern C: Generic require_roles() decorator
- ML Registry implementation details
- Testing RBAC (pytest examples)

**Audience:** Developers learning RBAC patterns

**Read Time:** 30-40 minutes

---

### 🔑 API Key Authentication Guide
**Location:** `advanced_edition/API_KEY_GUIDE.md`

Complete guide for API key implementation:
- When to use API keys (vs OAuth2, JWT)
- API key lifecycle (create → use → rotate → revoke)
- Scope system with examples
- Security best practices
- Integration patterns (Python, JavaScript, CI/CD, Docker)
- Troubleshooting guide
- Audit & compliance

**Key Sections:**
- When to use API keys
- API key lifecycle
- Scope format and matching
- Security best practices (treat like passwords, minimal scope, rotation)
- Python client example
- JavaScript client example
- GitHub Actions CI/CD example
- Troubleshooting common issues

**Audience:** Developers implementing API key systems

**Read Time:** 25-35 minutes

---

### 🔐 OAuth2 Integration Example
**Location:** `advanced_edition/oauth2_integration_example.py`

Complete, runnable OAuth2 example:
- Google OAuth2 implementation
- GitHub OAuth2 implementation
- Authorization code flow
- Token exchange
- User information retrieval
- Frontend HTML/JavaScript example
- Setup instructions for Google and GitHub
- 800+ lines of well-documented code

**Key Classes:**
- `GoogleOAuth2` - Google-specific implementation
- `GitHubOAuth2` - GitHub-specific implementation
- `OAuthUserInfo` - Standardized user data model

**Key Functions:**
- `get_auth_url()` - Generate authorization URL
- `exchange_code_for_token()` - Convert auth code to access token
- `get_user_info()` - Fetch user data
- `handle_callback()` - Complete OAuth2 flow

**Audience:** Developers integrating OAuth2

**Run Example:**
```bash
python advanced_edition/oauth2_integration_example.py
```

**Read Time:** 20-30 minutes

---

### 📊 Implementation Summary
**Location:** `IMPLEMENTATION_SUMMARY.md`

High-level overview of all changes:
- What's new in each edition
- Phase-by-phase implementation details
- Files created and modified
- Learning progression
- Security considerations
- Testing strategy
- Future extensions

**Key Sections:**
- Executive summary
- Phase 1: RBAC Addition
- Phase 2: OAuth2 Integration
- Phase 3: API Key Authentication
- Files created/modified summary
- Learning progression

**Audience:** Project managers, instructors, students wanting overview

**Read Time:** 15-20 minutes

---

### 📋 Authorization Audit
**Location:** `AUTHORIZATION_AUDIT.md`

Initial audit identifying gaps (19KB document):
- Gap analysis
- Current status of RBAC
- OAuth2 implementation status
- API key support status
- Detailed findings for each edition

**Audience:** Developers wanting to understand what was missing

**Read Time:** 10-15 minutes

---

### 📝 TODO & Implementation Plan
**Location:** `TODO_MODULE12_UPDATE.md`

Detailed 6-phase implementation plan (15KB):
- Phase 1: RBAC in Beginner & Intermediate
- Phase 2: Fix Advanced Edition RBAC
- Phase 3: OAuth2 Implementation
- Phase 4: API Key Authentication
- Phase 5: Learning Materials
- Phase 6: Optional Extensions

**Audience:** Developers understanding implementation approach

**Read Time:** 15-20 minutes

---

## 🎓 Teaching Examples

### Beginner Edition: RBAC Basics
**Location:** `beginner_edition/standalone_examples/5_rbac_basics.py`

Comprehensive teaching example (350+ lines):
- Complete working FastAPI app
- `UserRole` enum (user, admin)
- In-memory user database
- JWT token creation with role
- `require_admin()` dependency
- 4 example endpoints showing different access patterns
- Fully runnable with test users (alice: user, bob: admin)
- Docstrings explaining each concept

**Key Concepts Taught:**
1. Role-based access control
2. JWT tokens with role information
3. Dependency injection for auth checks
4. Different access patterns per role
5. Admin-only operations
6. Role-based data visibility

**Run Example:**
```bash
python beginner_edition/standalone_examples/5_rbac_basics.py
```

**Interactive Testing:**
```bash
# Run with uvicorn
uvicorn beginner_edition.standalone_examples.5_rbac_basics:app --reload

# Visit http://localhost:8000/docs
# Try endpoints as different users
```

**Audience:** Beginners learning RBAC

---

### Intermediate Edition: Blog API
**Location:** `intermediate_edition/blog_api/`

Blog application demonstrating:
- 3-role system (user, moderator, admin)
- Different permissions per role
- Post creation and editing
- Comment moderation

**Key Improvements:**
- Added `UserRole` enum with 3 roles
- Updated `User` model with role field
- Updated JWT tokens to include role
- Ready for endpoint-level role checking

**Audience:** Intermediate learners

---

### Advanced Edition: ML Registry Application
**Location:** `advanced_edition/ml_registry_app/`

Full production-grade application featuring:
- JWT authentication with refresh tokens
- RBAC (user, reviewer, admin, superuser)
- OAuth2 social login (Google, GitHub)
- API key management
- PostgreSQL with async SQLAlchemy 2.0
- MinIO for file storage
- Redis integration
- Alembic migrations
- Comprehensive test suite
- Docker Compose stack

**Key Components:**
1. **Authentication:**
   - JWT with refresh tokens
   - OAuth2 (Google, GitHub)
   - API key authentication

2. **Authorization:**
   - Role-based access control
   - Ownership-based access (users manage own resources)
   - Visibility filtering
   - Scope-based permissions (for API keys)

3. **Features:**
   - User registration and login
   - Model management (CRUD)
   - Experiment tracking
   - File uploads (MinIO)
   - Caching (Redis)
   - Database migrations (Alembic)

**Audience:** Advanced learners, production developers

---

## 📁 File Organization

### Beginner Edition
```
beginner_edition/
├── todo_app/
│   ├── app/
│   │   ├── models.py          [Modified: Added role field]
│   │   ├── auth.py            [Modified: Added role to JWT]
│   │   └── main.py            [Modified: Pass role in login]
│   └── ...
├── standalone_examples/
│   ├── 5_rbac_basics.py       [NEW: Teaching example]
│   └── ...
└── ...
```

### Intermediate Edition
```
intermediate_edition/
├── blog_api/
│   ├── app/
│   │   ├── models.py          [Modified: Added 3-role system]
│   │   ├── auth.py            [Modified: Added role to JWT]
│   │   └── main.py            [Modified: Pass role in login]
│   └── ...
└── ...
```

### Advanced Edition
```
advanced_edition/
├── ml_registry_app/
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py        [Modified: Added api_keys relationship]
│   │   │   ├── api_key.py     [NEW: API key model]
│   │   │   └── ...
│   │   ├── auth/
│   │   │   ├── api_key_auth.py [NEW: API key validation]
│   │   │   ├── oauth2.py       [Existing: OAuth2 implementation]
│   │   │   ├── dependencies.py
│   │   │   └── ...
│   │   ├── schemas/
│   │   │   ├── api_key.py      [NEW: API key Pydantic models]
│   │   │   ├── token.py        [Modified: Added OAuth2 schemas]
│   │   │   └── ...
│   │   ├── api/v1/
│   │   │   ├── api_keys.py     [NEW: API key endpoints]
│   │   │   ├── auth.py         [Modified: Added OAuth2 endpoints]
│   │   │   ├── models.py       [Modified: Refactored RBAC checks]
│   │   │   └── ...
│   │   └── ...
│   ├── RBAC_PATTERNS.md        [NEW: RBAC guide]
│   ├── oauth2_integration_example.py [NEW: OAuth2 example]
│   ├── API_KEY_GUIDE.md        [NEW: API key guide]
│   ├── README.md               [Modified: Updated features]
│   └── ...
├── async_patterns.py
└── ...

Module 12 Root
├── INDEX.md                    [NEW: This file]
├── IMPLEMENTATION_SUMMARY.md   [NEW: Overview of changes]
├── AUTHORIZATION_AUDIT.md      [Existing: Gap analysis]
├── TODO_MODULE12_UPDATE.md     [Existing: Implementation plan]
└── ...
```

---

## 🔍 Quick Links to Code

### RBAC in Different Editions

**Beginner - Simple RBAC:**
- Model: `beginner_edition/todo_app/app/models.py` (UserRole enum, role field)
- Auth: `beginner_edition/todo_app/app/auth.py` (role in JWT)
- Example: `beginner_edition/standalone_examples/5_rbac_basics.py` (full working example)

**Intermediate - 3-Role System:**
- Model: `intermediate_edition/blog_api/app/models.py` (user, moderator, admin)
- Auth: `intermediate_edition/blog_api/app/auth.py` (role in JWT)

**Advanced - Production RBAC:**
- Model: `advanced_edition/ml_registry_app/app/models/user.py` (role + superuser)
- Dependencies: `advanced_edition/ml_registry_app/app/auth/dependencies.py` (require_roles decorator)
- Endpoints: `advanced_edition/ml_registry_app/app/api/v1/models.py` (RBAC in action)
- Guide: `advanced_edition/RBAC_PATTERNS.md` (complete patterns guide)

### OAuth2 Implementation

- Core: `advanced_edition/ml_registry_app/app/auth/oauth2.py`
- Endpoints: `advanced_edition/ml_registry_app/app/api/v1/auth.py` (callback endpoints)
- Schemas: `advanced_edition/ml_registry_app/app/schemas/token.py` (OAuth2Callback)
- Example: `advanced_edition/oauth2_integration_example.py` (complete runnable example)

### API Key Implementation

- Model: `advanced_edition/ml_registry_app/app/models/api_key.py` (APIKey model)
- Auth: `advanced_edition/ml_registry_app/app/auth/api_key_auth.py` (validation & hashing)
- Endpoints: `advanced_edition/ml_registry_app/app/api/v1/api_keys.py` (CRUD operations)
- Schemas: `advanced_edition/ml_registry_app/app/schemas/api_key.py` (Pydantic models)
- Guide: `advanced_edition/API_KEY_GUIDE.md` (usage & integration)

---

## 🚀 Getting Started

### For Beginners
1. Read: `beginner_edition/standalone_examples/5_rbac_basics.py` docstring
2. Run: `python beginner_edition/standalone_examples/5_rbac_basics.py`
3. Explore: Visit http://localhost:8000/docs and test endpoints
4. Learn: Study the code comments explaining each concept

### For Intermediate Learners
1. Review: Changes to `intermediate_edition/blog_api/app/models.py`
2. Check: 3-role system (user, moderator, admin)
3. Understand: How role is added to JWT tokens
4. Next: Add endpoint-level role checking

### For Advanced Developers
1. Read: `RBAC_PATTERNS.md` for design patterns
2. Read: `API_KEY_GUIDE.md` for API key system
3. Review: `oauth2_integration_example.py` for OAuth2
4. Study: `ml_registry_app/app/api/v1/models.py` for real implementation
5. Extend: Add API key support to your endpoints

---

## ✅ Verification Checklist

### Can You...

- [ ] Explain what RBAC is?
  → Read: `RBAC_PATTERNS.md` Overview section

- [ ] Create a role-based FastAPI app?
  → Follow: `beginner_edition/standalone_examples/5_rbac_basics.py`

- [ ] Understand 4 RBAC patterns?
  → Read: `RBAC_PATTERNS.md` Implementation Architecture

- [ ] Implement OAuth2 social login?
  → Study: `oauth2_integration_example.py` + `API_KEY_GUIDE.md`

- [ ] Create and validate API keys?
  → Review: `ml_registry_app/app/auth/api_key_auth.py`

- [ ] Use scope-based permissions?
  → Read: `API_KEY_GUIDE.md` Scopes section

- [ ] Test authorization?
  → See: `RBAC_PATTERNS.md` Testing RBAC section

---

## 📈 Learning Path

```
Start Here
    ↓
Beginner: JWT + Simple RBAC
    ↓ (5_rbac_basics.py)
    ↓
Understand 2-role system (user, admin)
    ↓
Intermediate: Multiple Roles
    ↓ (blog_api with 3 roles)
    ↓
See role progression (user → moderator → admin)
    ↓
Advanced: Production Patterns
    ↓ (RBAC_PATTERNS.md)
    ↓
Learn 4 authorization patterns
    ↓
Understand OAuth2
    ↓ (oauth2_integration_example.py)
    ↓
Implement API Keys
    ↓ (API_KEY_GUIDE.md)
    ↓
Master service-to-service auth
    ↓
Production Ready
```

---

## 🔗 Cross-Module Integration

### How Module 12 Integrates with Other Modules

#### Previous Modules (Used by Module 12)
- **Module 11:** Database design (SQLAlchemy models)
- **Module 10:** API design (FastAPI endpoints)
- **Module 9:** Async patterns (async/await)

#### Following Modules (Should Use Module 12)
- **Module 13+:** All applications should use auth patterns from Module 12
- **Project:** Student projects must include proper authentication

---

## 📞 Support & Questions

### If you want to understand...

| Topic | Resource |
|-------|----------|
| What RBAC is | `RBAC_PATTERNS.md` Overview |
| How to implement RBAC | `5_rbac_basics.py` or `models.py` in ML Registry |
| Authorization patterns | `RBAC_PATTERNS.md` Implementation Architecture |
| OAuth2 flow | `oauth2_integration_example.py` |
| API key system | `API_KEY_GUIDE.md` |
| Security best practices | `RBAC_PATTERNS.md` Security Considerations + `API_KEY_GUIDE.md` Best Practices |
| How to test auth | `RBAC_PATTERNS.md` Testing RBAC |
| Real working code | `ml_registry_app/` (complete application) |
| Scope-based permissions | `API_KEY_GUIDE.md` Scopes section |
| Integration examples | `API_KEY_GUIDE.md` Common Integration Patterns |

---

## 🎯 Summary

Module 12 has been significantly enhanced with:
- **RBAC** across all three editions (beginner → intermediate → advanced)
- **OAuth2** social login implementation (Google, GitHub)
- **API Keys** for service-to-service authentication
- **Comprehensive guides** for each pattern
- **Working examples** at every level
- **Production-ready code** in ML Registry

**Status:** ✅ Ready for learning and integration

---

**Last Updated:** January 24, 2026
**Completeness:** 85-90% (core features done, optional extensions pending)
