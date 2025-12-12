# Research: Backend API with Mocked Data

**Date**: 2025-12-11
**Feature**: 001-backend-api

## Technology Decisions

### 1. FastAPI Project Structure

**Decision**: Use modular structure with routers, models, and data separation

**Rationale**:
- FastAPI's router system enables clean separation of concerns
- Pydantic models provide automatic validation and OpenAPI schema generation
- Separate data module allows easy swap to real database later
- Follows FastAPI best practices from official documentation

**Alternatives Considered**:
- Single file app: Rejected - doesn't scale, violates <500 line rule
- Flask: Rejected - no built-in OpenAPI/Swagger, async support requires extensions

### 2. Configuration Management

**Decision**: Use pydantic-settings with `.env` file at `backend/.env`

**Rationale**:
- Type-safe configuration with validation
- Automatic environment variable loading
- Supports default values for development
- Native Pydantic integration

**Alternatives Considered**:
- Plain python-dotenv: Rejected - no type safety or validation
- dynaconf: Rejected - overkill for this scope

### 3. CORS Configuration

**Decision**: Configure FastAPI CORS middleware for localhost:8080

**Rationale**:
- Frontend runs on port 8080 (Vite)
- Development-only CORS; production would use reverse proxy
- FastAPI's CORSMiddleware is standard approach

**Configuration**:
```python
origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Frontend API Integration

**Decision**: TanStack Query with custom hooks in `services/` directory

**Rationale**:
- Already in frontend dependencies (`@tanstack/react-query`)
- Provides caching, refetching, loading/error states
- Custom hooks encapsulate API calls cleanly
- Components remain unchanged - hooks return same data shape

**Pattern**:
```typescript
// services/repositories.ts
export function useRepositories() {
  return useQuery({
    queryKey: ['repositories'],
    queryFn: () => api.get('/repositories').then(r => r.data)
  });
}
```

### 5. API Client Configuration

**Decision**: Use environment variable for API base URL with axios

**Rationale**:
- axios already in frontend dependencies
- Environment variable allows easy switch between dev/prod
- Centralized configuration in `lib/api.ts`

**Configuration**:
```typescript
// lib/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const api = axios.create({ baseURL: API_BASE_URL });
```

### 6. Mocked Data Strategy

**Decision**: Port exact data structure from `frontend/src/data/mockData.ts` to Python

**Rationale**:
- Ensures 1:1 compatibility with existing frontend types
- Frontend components already render this data correctly
- No risk of breaking existing UI behavior

**Implementation**:
- Copy TypeScript interfaces → Pydantic models
- Copy mock data values → Python dictionaries
- Validate with mypy and pytest

### 7. Testing Strategy

**Decision**: pytest with TestClient for API testing

**Rationale**:
- FastAPI's TestClient enables synchronous API testing
- pytest markers separate unit (`@pytest.mark.unit`) from integration tests
- Follows constitution testing requirements

**Structure**:
- `tests/unit/test_models.py`: Pydantic model validation
- `tests/integration/test_api.py`: Full endpoint testing with TestClient

### 8. Swagger UI Access

**Decision**: Enable at `/docs` (default FastAPI behavior)

**Rationale**:
- FastAPI auto-generates OpenAPI schema from Pydantic models
- Interactive testing without external tools
- Documents API for frontend developers

**Access**: `http://localhost:8000/docs`

## Dependencies

### Backend (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",  # For TestClient
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]
```

### Frontend (package.json additions)

No new dependencies needed - `@tanstack/react-query` and `axios` already present.

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Database needed for MVP? | No - mocked data only, SQLite prepared for future |
| Authentication needed? | No - MVP phase, add later |
| How to handle feature analysis? | Return static `exampleAnalysis` regardless of input |
| Frontend component changes? | None - only add service layer hooks |
