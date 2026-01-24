# Module 12 Architecture Guide

## System Architecture Overview

Module 12 demonstrates two architectural approaches for building web applications:

### 1. Beginner Edition - Monolithic Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Client Applications                      │
│          (Web Browser, Mobile App, Python Client)         │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/HTTPS (REST API)
                     ↓
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Authentication Layer                    │ │
│  │  • JWT Token Generation/Validation                  │ │
│  │  • Password Hashing (bcrypt)                        │ │
│  │  • Bearer Token Authentication                      │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │            Business Logic Layer                      │ │
│  │  • ML Model CRUD Operations                         │ │
│  │  • Experiment Tracking                              │ │
│  │  • File Management                                  │ │
│  │  • Filtering & Pagination                           │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Data Access Layer (ORM)                    │ │
│  │  • SQLAlchemy async queries                         │ │
│  │  • Relationship management                          │ │
│  │  • Transaction handling                             │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────┬──────────────┬──────────────┬────────────────┘
             │              │              │
             ↓              ↓              ↓
         ┌────────┐  ┌──────────┐  ┌─────────┐
         │  Postgres  │  Redis   │  │  MinIO  │
         │ (Database) │ (Cache)  │  │(Storage)│
         └────────┘  └──────────┘  └─────────┘
```

**Characteristics:**
- Single codebase handling all concerns
- Tightly coupled components
- Simple deployment
- Shared database and resources
- Good for small to medium applications

**When to Use:**
- Learning web development
- MVP (Minimum Viable Product)
- Small teams
- Low complexity requirements

### 2. Advanced Edition - Microservices Architecture (Planned)

```
┌──────────────────────────────────────────────────────────┐
│                   Client Applications                      │
└────────────────────┬─────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ↓                     ↓
    ┌───────────────┐  ┌──────────────────┐
    │ Auth Service  │  │ ML Registry API  │
    │               │  │                  │
    │ • JWT         │  │ • Models CRUD    │
    │ • OAuth2      │  │ • Experiments    │
    │ • API Keys    │  │ • Analytics      │
    │ • WebAuthn    │  │ • WebSocket      │
    └───────┬───────┘  └────────┬─────────┘
            │                   │
            │ Service-to-Service Communication
            │ (Shared secret or mTLS)
            │
    ┌───────┴─────────────────────┐
    │                             │
    ↓                             ↓
┌─────────────────┐      ┌─────────────────┐
│ PostgreSQL      │      │ PostgreSQL      │
│ (Auth DB)       │      │ (Registry DB)   │
└─────────────────┘      └─────────────────┘
    │
    ↓
┌──────────────────────────────────────────┐
│  Shared Infrastructure                   │
│  • Redis (Cache, Message Queue)          │
│  • MinIO (Object Storage)                │
│  • Prometheus (Metrics)                  │
│  • Grafana (Visualization)               │
└──────────────────────────────────────────┘
```

**Characteristics:**
- Independent microservices
- Separate databases (database per service)
- Asynchronous communication
- Service discovery and orchestration
- Distributed tracing and logging

**When to Use:**
- Large teams
- High scalability needs
- Independent deployment cycles
- Complex business domains
- Enterprise applications

---

## Beginner Edition: Component Details

### 1. FastAPI Application Layer

**File**: `app/main.py`

Responsibilities:
- Route registration and middleware setup
- CORS configuration
- Lifespan management (startup/shutdown)
- Health check endpoint

```python
# Simplified flow
Request → CORS Middleware → Route Handler → Response
```

### 2. Authentication Layer

**Files**: `app/auth/`

Components:
- **jwt.py**: Token creation and validation
- **password.py**: Password hashing and verification
- **dependencies.py**: FastAPI dependency injection

**Token Flow**:
```
User Registration/Login
        ↓
Password Hash & Verification
        ↓
JWT Token Generation (Access + Refresh)
        ↓
Return Tokens to Client
        ↓
Client Uses Access Token in Bearer Header
        ↓
Dependency validates token and injects User
```

### 3. Database Layer

**Files**: `app/models/`, `app/database.py`

**Entity-Relationship Diagram**:
```
┌─────────┐
│ User    │
├─────────┤
│ id (PK) │
│ email   │
│ username│
└────┬────┘
     │ 1:N
     ├──→ MLModel
     │    ├─ id (PK)
     │    ├─ name
     │    ├─ framework
     │    ├─ lifecycle
     │    └─ owner_id (FK)
     │        │
     │        └──→ ModelVersion
     │             ├─ id (PK)
     │             ├─ version_number
     │             └─ model_id (FK)
     │
     └──→ Experiment
          ├─ id (PK)
          ├─ name
          ├─ parameters
          └─ owner_id (FK)
```

**Table Descriptions**:

**users**
- Stores user accounts
- Unique constraints on email and username
- Tracks active status and superuser flag
- Timestamps for auditing

**ml_models**
- Core entity storing ML model metadata
- Framework (sklearn, pytorch, tensorflow, xgboost, etc.)
- Task type (classification, regression, clustering, anomaly_detection)
- Lifecycle (development, staging, production, archived)
- Performance metrics (accuracy, precision, recall, f1_score)
- Hyperparameters stored as JSON
- File path pointing to MinIO

**experiments**
- Tracks ML experiments that produced models
- Parameters and tags as JSON
- Links multiple models to experiments

**model_versions**
- Version history for each model
- Metrics snapshot at each version
- Enables rollback and comparison

### 4. API Endpoints

**Authentication Routes** (`/api/v1/auth/`):
```
POST   /register          - Create new user
POST   /login             - User login (get tokens)
POST   /refresh           - Refresh access token
GET    /me                - Get current user info
```

**Model Routes** (`/api/v1/models/`):
```
GET    /                  - List models (filtered, paginated)
POST   /                  - Create new model
GET    /{id}              - Get model details
PUT    /{id}              - Update model
DELETE /{id}              - Delete model
PATCH  /{id}/lifecycle    - Update model lifecycle
```

**File Routes** (`/api/v1/files/`):
```
POST   /upload                    - Upload model file
GET    /download/{path}           - Download file
GET    /presigned-url/{path}      - Get temporary URL
```

### 5. Storage Layer

**MinIO Integration** (`app/storage/minio_client.py`)

File Organization:
```
ml-models/
├── users/
│   ├── 1/
│   │   ├── models/
│   │   │   ├── model_v1.pkl
│   │   │   └── model_v2.pkl
│   └── 2/
│       └── models/
│           └── model.joblib
```

**Operations**:
- Upload with metadata
- Download with streaming
- Presigned URLs (temporary access)
- File deletion

### 6. Request/Response Flow

**Example: Create ML Model**

```
1. Client sends POST /api/v1/models/
   {
     "name": "My Model",
     "framework": "sklearn",
     "task_type": "classification",
     "accuracy": 0.95
   }

2. FastAPI validates with Pydantic (MLModelCreate schema)

3. Dependency injection provides:
   - Database session (from get_db)
   - Current user (from get_current_user)

4. Route handler:
   - Creates MLModel object
   - Sets owner_id from current_user
   - Writes to database
   - Commits transaction
   - Returns MLModelResponse

5. Client receives:
   {
     "id": 123,
     "name": "My Model",
     "framework": "sklearn",
     "task_type": "classification",
     "lifecycle": "development",
     "accuracy": 0.95,
     "owner_id": 1,
     ...
   }
```

### 7. Dependency Injection Pattern

FastAPI's dependency system enables:

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Validate JWT and fetch user
    # Return User object to route handler
    pass

# Usage in route:
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Benefits**:
- Reusable logic (DRY)
- Automatic validation
- Easy testing (mock dependencies)
- Clear dependency graph

---

## Database Design Principles

### 1. Normalization
- Separate concerns into different tables
- Avoid data redundancy
- Maintain referential integrity

### 2. Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_ml_models_owner_id ON ml_models(owner_id);
CREATE INDEX idx_ml_models_lifecycle ON ml_models(lifecycle);
```

### 3. Relationships
- **One-to-Many**: User → MLModels
- **One-to-Many**: MLModel → ModelVersions
- **One-to-Many**: User → Experiments

### 4. Cascading
- Delete user → Delete all user's models
- Delete model → Delete all versions
- Delete model version → Set experiment reference to NULL

---

## Security Considerations

### 1. Authentication
- **JWT**: Stateless token-based auth
- **Access tokens**: Short expiry (30 min)
- **Refresh tokens**: Longer expiry (7 days)
- **Secret key**: From environment (not hardcoded)

### 2. Password Security
- **Bcrypt**: Modern password hashing
- **Rounds**: 12 (configurable)
- **Salting**: Automatic with bcrypt

### 3. Authorization
- **Role-based access**: superuser flag
- **Ownership validation**: Users can only modify their own models
- **Bearer tokens**: In Authorization header

### 4. API Security
- **CORS**: Configurable origins
- **HTTPS**: Required in production
- **Rate limiting**: Can be added
- **Input validation**: Pydantic schemas

---

## Performance Considerations

### 1. Database Queries
- Use async/await for non-blocking I/O
- Add indexes for frequently queried columns
- Pagination prevents large result sets
- Query optimization with select()

### 2. File Storage
- Presigned URLs avoid re-uploading
- Streaming downloads reduce memory
- User-namespaced paths enable multi-tenancy
- S3-compatible API enables scalability

### 3. Caching (Redis)
- Session management
- Token blacklisting (future)
- Computed results
- Rate limiting counters

---

## Testing Architecture

### 1. Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### 2. Integration Tests
- Test endpoint-to-endpoint
- Use test database (SQLite in-memory)
- Verify complete workflows

### 3. Test Fixtures
```python
@pytest_asyncio.fixture
async def async_engine():
    # Create test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine

@pytest_asyncio.fixture
async def client(async_session):
    # Create test client with DB override
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app)) as ac:
        yield ac
```

---

## Deployment Readiness

### 1. Docker Containerization
- Multi-stage builds
- Health checks
- Volume management
- Environment variables

### 2. Docker Compose
- Orchestrates 4 services
- Named volumes for persistence
- Health checks for startup ordering
- Network isolation

### 3. Configuration Management
- `.env` file for secrets
- Pydantic Settings for validation
- Environment-specific configurations

---

## Future: Advanced Edition Architecture

### Service Separation
```
Auth Service (Port 8001)
├── User Management
├── JWT Generation
├── OAuth2 Integration
├── API Key Management
└── WebAuthn/Passkeys

ML Registry API (Port 8002)
├── Model Management
├── Experiment Tracking
├── File Operations
├── Analytics
└── WebSocket Updates
```

### Communication
- REST API for synchronous calls
- Message queue (Celery) for async tasks
- Service discovery
- Circuit breakers for resilience

### Observability
- Structured logging (structlog)
- Distributed tracing
- Prometheus metrics
- Grafana dashboards

---

## Conclusion

The Beginner Edition provides a solid foundation with:
- ✅ Modern async patterns
- ✅ Type-safe code
- ✅ Clear architecture
- ✅ Production patterns
- ✅ Comprehensive testing

The Advanced Edition (planned) will showcase:
- ✅ Microservices patterns
- ✅ Enterprise authentication
- ✅ Distributed systems
- ✅ Observability at scale
- ✅ Kubernetes deployment

Both editions use real-world patterns applicable to production systems.
