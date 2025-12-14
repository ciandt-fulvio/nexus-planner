# Research: Code Duplication Analysis

**Feature**: Code Review & Refactoring for Maintainability (002-code-review)
**Date**: 2025-12-14
**Purpose**: Document identified duplication patterns and consolidation strategies

---

## Overview

Nexus Planner codebase analysis identified 4 primary duplication patterns affecting 13-15 files across backend and frontend. This research consolidates findings and defines refactoring strategies for each pattern.

---

## Pattern 1: Duplicated `__main__` Validation Blocks

### Current State

**Affected Files** (8+ modules):
- `backend/src/nexus_api/models/repository.py` (80-100 lines)
- `backend/src/nexus_api/models/person.py` (80-100 lines)
- `backend/src/nexus_api/models/analysis.py` (80-100 lines)
- `backend/src/nexus_api/routers/repositories.py` (50-80 lines)
- `backend/src/nexus_api/routers/people.py` (50-80 lines)
- `backend/src/nexus_api/routers/analysis.py` (50-80 lines)
- `backend/src/nexus_api/main.py` (60-80 lines)
- 2+ additional modules with similar validation patterns

**Total Duplicated Lines**: 400-640 lines of nearly identical code

**Code Pattern**:
```python
if __name__ == "__main__":
    import sys
    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1, 2, 3... (20-40 test cases per module)
    total_tests += 1
    try:
        result = some_function()
        if result != expected:
            all_validation_failures.append(f"Test failed: {details}")
    except Exception as e:
        all_validation_failures.append(f"Error: {e}")

    # Print results
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)}/{total_tests} tests failed")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests successful")
        sys.exit(0)
```

### Analysis

**Why This Is Duplication**:
- Core validation logic is identical across all files
- Only the test cases differ (which tests to run)
- Same output format repeated in every file
- Changes to validation format require edits in 8+ places

**Maintenance Cost**:
- High: Any change to validation output format requires 8+ file edits
- Error-prone: Risk of inconsistent updates across files
- Testing burden: Each module must be tested independently

**Dependencies**:
- All modules with `__main__` blocks use this pattern
- No external dependencies on this code pattern
- Safe to refactor without API impact

### Consolidation Strategy: Validation Helper Module

**Approach**: Create `backend/src/nexus_api/testing/validation_helpers.py` with reusable `ValidationHelper` class

**New Module Structure**:
```python
# validation_helpers.py

class ValidationHelper:
    """Consolidates __main__ validation logic from 8+ modules."""

    def __init__(self):
        self.tests: list[tuple[str, Callable, Any]] = []
        self.failures: list[str] = []
        self.total_tests = 0

    def add_test(self, name: str, test_func: Callable, expected: Any):
        """Register a test case."""
        self.tests.append((name, test_func, expected))

    def run(self) -> int:
        """Execute all tests and return exit code (0 = pass, 1 = fail)."""
        self.total_tests = len(self.tests)
        for name, test_func, expected in self.tests:
            try:
                result = test_func()
                if result != expected:
                    self.failures.append(f"{name}: Expected {expected}, got {result}")
            except Exception as e:
                self.failures.append(f"{name}: {type(e).__name__}: {e}")

        self._print_results()
        return 1 if self.failures else 0

    def _print_results(self):
        """Print validation results in consistent format."""
        if self.failures:
            print(f"❌ VALIDATION FAILED - {len(self.failures)}/{self.total_tests} tests failed:")
            for failure in self.failures:
                print(f"  - {failure}")
            return 1
        else:
            print(f"✅ VALIDATION PASSED - All {self.total_tests} tests successful")
            return 0
```

**Updated `__main__` Block Usage**:
```python
# In repository.py, person.py, analysis.py, etc.
if __name__ == "__main__":
    from src.nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()
    validator.add_test("test_name_1", lambda: function_call(), expected_value_1)
    validator.add_test("test_name_2", lambda: function_call(), expected_value_2)
    # ... add more tests
    sys.exit(validator.run())
```

**Benefits**:
- ✅ Eliminates 400-640 lines of duplication
- ✅ Single source of truth for validation format
- ✅ Changes to validation format affect only 1 file
- ✅ Reduces each `__main__` block from 80+ lines to ~5 lines
- ✅ Minimal boilerplate for adding new tests

**Refactoring Order**: Create helper FIRST, then refactor each module to use it

---

## Pattern 2: FastAPI Router CRUD Boilerplate

### Current State

**Affected Files**:
- `backend/src/nexus_api/routers/repositories.py` (~120-150 lines)
- `backend/src/nexus_api/routers/people.py` (~120-150 lines)
- `backend/src/nexus_api/routers/analysis.py` (~120-150 lines)

**Total Duplicated Code**: ~40-50% of each router (same endpoints, same patterns)

**Code Pattern**:
```python
@router.get("", response_model=list[Repository])
async def list_repositories(db: AsyncSession = Depends(get_db)):
    return await repository_service.get_all_repositories(db)

@router.get("/{repo_id}", response_model=Repository)
async def get_repository(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await repository_service.get_repository_by_id(db, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Not found")
    return repo

@router.post("", response_model=Repository)
async def create_repository(data: RepositoryCreate, db: AsyncSession = Depends(get_db)):
    return await repository_service.create_repository(db, data)

# ... repeated for person, analysis, etc.
```

### Analysis

**Why This Is Duplication**:
- CRUD operations are identical across all entities
- Only the entity names, service references, and response models differ
- Same error handling pattern repeated 3+ times
- Same dependency injection pattern repeated 3+ times

**Maintenance Cost**:
- Medium: Adding a new router requires copying existing code
- Error-prone: Easy to miss validation or error handling details
- Cognitive burden: Pattern is clear but repetitive

**Dependencies**:
- Service layer (e.g., `repository_service`, `person_service`)
- Pydantic models for validation
- Database session dependency

### Consolidation Strategy: CRUD Router Factory

**Approach**: Create `backend/src/nexus_api/routers/factory.py` with `create_crud_router` function

**New Module Structure**:
```python
# routers/factory.py

from typing import Type, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

def create_crud_router(
    prefix: str,
    tags: List[str],
    entity_model: Type,
    create_model: Type,
    list_model: Type,
    service,
    db_dependency = Depends(get_db),
) -> APIRouter:
    """Generate standard CRUD router for an entity."""
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=list[list_model])
    async def list_all(db: AsyncSession = db_dependency):
        return await service.get_all(db)

    @router.get("/{item_id}", response_model=entity_model)
    async def get_one(item_id: str, db: AsyncSession = db_dependency):
        item = await service.get_by_id(db, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Not found")
        return item

    @router.post("", response_model=entity_model)
    async def create_one(data: create_model, db: AsyncSession = db_dependency):
        return await service.create(db, data)

    # PUT, DELETE endpoints follow same pattern

    return router
```

**Updated Router Usage**:
```python
# routers/repositories.py
from src.nexus_api.routers.factory import create_crud_router

router = create_crud_router(
    prefix="/repositories",
    tags=["repositories"],
    entity_model=Repository,
    create_model=RepositoryCreate,
    list_model=Repository,
    service=repository_service,
)

# Add any custom endpoints specific to repositories
@router.get("/repositories/{repo_id}/metrics", response_model=RepositoryMetrics)
async def get_metrics(...):
    ...
```

**Benefits**:
- ✅ Reduces each router from 120-150 lines to ~30-40 lines
- ✅ 30-40% boilerplate elimination per router
- ✅ Standardizes endpoint behavior across entities
- ✅ New routers can be created in 5 lines instead of 120 lines

**Refactoring Order**: Create factory, then refactor each router one at a time

---

## Pattern 3: Service Builder Methods

### Current State

**Affected Files**:
- `backend/src/nexus_api/services/repository_service.py` (~150-180 lines)
- `backend/src/nexus_api/services/person_service.py` (~150-180 lines)

**Pattern**:
```python
# repository_service.py
async def _build_repository_model(db: AsyncSession, db_row) -> Repository:
    """Build complete Repository model from database row + computed metrics."""
    # 80-100 lines of:
    # 1. Query relationships
    # 2. Calculate metrics
    # 3. Assemble Pydantic model
    # 4. Return instance
```

### Analysis

**Why This Is Duplication**:
- Both services follow identical builder pattern
- 80-100 lines of nearly identical logic (different only in entity names)
- Same database query → compute → assemble cycle

**Maintenance Cost**:
- Low-Medium: Only 2 files affected, but logic is complex
- Pattern adds 80-100 lines that could be abstracted

### Consolidation Strategy: Base Service Class

**Approach**: Create `backend/src/nexus_api/services/base_service.py` with `BaseService` class

**Benefits**:
- ✅ Eliminates 160-200 lines of builder pattern duplication
- ✅ Services inherit common behavior
- ✅ Changes to builder logic affect only one place

**Refactoring Order**: After validator and router refactoring (lower priority, P2)

---

## Pattern 4: Dashboard Components (Frontend)

### Current State

**Affected Files**:
- `frontend/src/components/RepositoryDashboard.tsx` (~200-250 lines)
- `frontend/src/components/PersonDashboard.tsx` (~200-250 lines)

**Duplicated Code** (~40-50%):
```typescript
// Both components have:
const { data, isLoading, error } = useRepositories() // or usePeople()
const [selectedId, setSelectedId] = useState<string | null>(null)
const selectedItem = data?.find(item => item.id === selectedId) || data?.[0]

if (isLoading) return <Loader2 className="h-8 w-8 animate-spin" />
if (error) return <Alert>Failed to load data</Alert>
if (!data?.length) return <Alert>No data available</Alert>

return (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {data.map(item => (
      <Card
        key={item.id}
        onClick={() => setSelectedId(item.id)}
        className={selectedId === item.id ? "ring-2" : ""}
      >
        {/* Render item card */}
      </Card>
    ))}
  </div>
  // Details panel, etc.
)
```

### Consolidation Strategy: DashboardTemplate Component

**Approach**: Extract reusable `DashboardTemplate<T>` component

**New Component Structure**:
```typescript
// components/DashboardTemplate.tsx

interface DashboardTemplateProps<T> {
  data?: T[]
  isLoading: boolean
  error?: Error | null
  selectedId: string | null
  onSelect: (id: string) => void
  renderCard: (item: T) => ReactNode
  renderDetails?: (item: T | null) => ReactNode
}

export function DashboardTemplate<T extends { id: string }>({
  data,
  isLoading,
  error,
  selectedId,
  onSelect,
  renderCard,
  renderDetails,
}: DashboardTemplateProps<T>) {
  const selectedItem = data?.find(item => item.id === selectedId) || data?.[0]

  if (isLoading) return <Loader2 className="h-8 w-8 animate-spin" />
  if (error) return <Alert>Failed to load data</Alert>
  if (!data?.length) return <Alert>No data available</Alert>

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Grid */}
      <div className="lg:col-span-2">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.map(item => (
            <Card key={item.id} onClick={() => onSelect(item.id)}>
              {renderCard(item)}
            </Card>
          ))}
        </div>
      </div>

      {/* Details */}
      {renderDetails && (
        <div className="lg:col-span-1">
          {renderDetails(selectedItem)}
        </div>
      )}
    </div>
  )
}
```

**Updated Dashboard Usage**:
```typescript
// RepositoryDashboard.tsx
export function RepositoryDashboard() {
  const { data, isLoading, error } = useRepositories()
  const [selectedId, setSelectedId] = useState<string | null>(null)

  return (
    <DashboardTemplate
      data={data}
      isLoading={isLoading}
      error={error}
      selectedId={selectedId}
      onSelect={setSelectedId}
      renderCard={(repo) => (
        <>
          <h3>{repo.name}</h3>
          <p>{repo.contributors?.length || 0} contributors</p>
        </>
      )}
      renderDetails={(repo) => repo ? <RepositoryDetails repo={repo} /> : null}
    />
  )
}
```

**Benefits**:
- ✅ Reduces each dashboard from 200-250 lines to 50-60 lines
- ✅ 60-70% boilerplate elimination per dashboard
- ✅ Makes adding new dashboards trivial (just pass renderCard and renderDetails)
- ✅ Consistent layout and interaction across all dashboards

**Refactoring Order**: Lower priority (P3), after backend refactoring complete

---

## Summary: Refactoring Roadmap

| Priority | Pattern | Lines | Approach | Benefit |
|----------|---------|-------|----------|---------|
| **P1 (HIGH)** | `__main__` validation | 400-640 | ValidationHelper class | Consolidate duplicated infrastructure |
| **P2 (MEDIUM)** | Router CRUD | ~360 | CRUDRouterFactory function | Reduce boilerplate by 30-40% |
| **P2 (MEDIUM)** | Service builders | 160-200 | BaseService class | Consolidate builder pattern |
| **P3 (LOW)** | Dashboard components | 300+ | DashboardTemplate component | 60% reduction per dashboard |

---

## Test Impact Assessment

**CRITICAL**: All refactoring must maintain 100% test pass rate (FR-000, SC-001)

### Validation Helper Refactoring
- ✅ Tests validate validation output format (must match exactly)
- ✅ Current tests should pass without modification
- ✅ New helper reduces test boilerplate but doesn't change test semantics

### Router Factory Refactoring
- ✅ Existing API tests must pass without modification
- ✅ Endpoints must behave identically after refactoring
- ✅ No changes to request/response contracts

### Service Builder Refactoring
- ✅ Service tests must pass (output models unchanged)
- ✅ Database queries must return same results

### Dashboard Refactoring
- ✅ Component tests must verify same visual output
- ✅ Props interface changes (to generic template), but component tests validate rendering
- ✅ Hook integration unchanged

---

## Implementation Sequence

1. **Validation Helper**: Create module, refactor one file at a time, commit after each file
2. **Router Factory**: Create factory, refactor routers one-by-one (repositories.py first)
3. **Service Builder**: Extract base class, refactor services
4. **Dashboard Template**: Extract component, update dashboards

**Each step runs full test battery**: `uv run pytest tests/unit/` + `uv run pytest tests/integration/`

If ANY test fails → revert, diagnose, fix
