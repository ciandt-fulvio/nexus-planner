# Quickstart Guide: Refactored Code Patterns

**Feature**: Code Review & Refactoring for Maintainability (002-code-review)
**Date**: 2025-12-14
**Purpose**: Quick reference for using refactored patterns in Nexus Planner

---

## ValidationHelper Pattern

**Location**: `backend/src/nexus_api/testing/validation_helpers.py`

**When to Use**: All `if __main__ == "__main__"` validation blocks in modules

**Benefits**:
- Eliminates 80-100 lines of boilerplate per module
- Consistent validation output format
- Single source of truth for validation logic

### Example: Using ValidationHelper in a New Module

**Before ValidationHelper**:
```python
if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: Basic functionality
    total_tests += 1
    try:
        result = some_function(test_data)
        if result != expected:
            all_validation_failures.append(f"Test failed: {result}")
    except Exception as e:
        all_validation_failures.append(f"Error: {e}")

    # Test 2: Edge case
    total_tests += 1
    try:
        result2 = another_function(edge_case)
        if result2 != expected2:
            all_validation_failures.append(f"Edge case failed: {result2}")
    except Exception as e:
        all_validation_failures.append(f"Error: {e}")

    # Print results
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)}/{total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests successful")
        sys.exit(0)
```

**After ValidationHelper**:
```python
if __name__ == "__main__":
    import sys
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: Basic functionality
    validator.add_test(
        "Basic function test",
        lambda: some_function(test_data),
        expected,
    )

    # Test 2: Edge case
    validator.add_test(
        "Edge case test",
        lambda: another_function(edge_case),
        expected2,
    )

    sys.exit(validator.run())
```

### Example: Using ValidationHelper with Complex Tests

```python
if __name__ == "__main__":
    import sys
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: Simple assertion
    validator.add_test(
        "Returns correct value",
        lambda: calculate_total([1, 2, 3]),
        6,
    )

    # Test 2: Using a test function for complex logic
    def test_complex_validation():
        result = complex_function(data)
        # Perform multiple checks
        if not result.is_valid:
            return False
        if result.count != 5:
            return False
        return True

    validator.add_test(
        "Complex validation",
        test_complex_validation,
        True,
    )

    # Test 3: Testing exceptions
    def test_error_handling():
        try:
            invalid_function(None)
            return "Should have raised ValueError"
        except ValueError:
            return "Correct exception"
        except Exception as e:
            return f"Wrong exception: {type(e).__name__}"

    validator.add_test(
        "Error handling",
        test_error_handling,
        "Correct exception",
    )

    sys.exit(validator.run())
```

### Running ValidationHelper Tests

```bash
# Run a single module's validation
uv run python src/nexus_api/models/repository.py

# Run all module validations (if needed)
for file in src/nexus_api/**/*.py; do
    uv run python "$file"
done
```

---

## Router Patterns (NOT REFACTORED)

**Decision**: Router factory was **NOT created** - current routers are already simple and readable.

**Rationale**:
- Routers are ~60 lines of logic each (only 2 endpoints)
- Factory would reduce line count but make code LESS readable
- Current implementation has clear docstrings, explicit function names, and type hints

**Recommendation**: Keep existing router pattern when creating new routers.

### Example: Creating a New Router (Current Pattern)

```python
"""
Your Entity router for Nexus API.

Provides endpoints for your entity data with calculated metrics.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Sample input: GET /api/v1/your-entities
Expected output: List of YourEntity objects as JSON
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.database import get_db
from nexus_api.models.your_entity import YourEntity
from nexus_api.services import your_entity_service

router = APIRouter(
    prefix="/your-entities",
    tags=["your-entities"],
)


@router.get("", response_model=list[YourEntity])
async def list_your_entities(
    db: AsyncSession = Depends(get_db)
) -> list[YourEntity]:
    """
    Get all your entities with calculated metrics.

    Returns a list of all your entities with their metrics.
    Database is seeded automatically on startup in development mode.
    """
    return await your_entity_service.get_all_your_entities(db)


@router.get("/{entity_id}", response_model=YourEntity)
async def get_your_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
) -> YourEntity:
    """
    Get a your entity by ID with calculated metrics.

    Args:
        entity_id: The entity ID to look up.
        db: Database session from dependency injection.

    Returns:
        The entity with the given ID.

    Raises:
        HTTPException: 404 if entity not found.
    """
    entity = await your_entity_service.get_your_entity_by_id(db, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=f"YourEntity {entity_id} not found"
        )
    return entity
```

---

## Service Patterns (NOT REFACTORED)

**Decision**: BaseService class was **NOT created** - services are domain-specific.

**Rationale**:
- Service `_build_*_model` methods are domain-specific, not generic
- repository_service and person_service have fundamentally different logic
- Creating BaseService would introduce unnecessary abstraction

**Recommendation**: Keep existing service pattern when creating new services.

### Example: Creating a New Service (Current Pattern)

```python
"""
Your Entity service for querying entities with calculated metrics.

Provides async functions for getting entities with all calculated fields.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Entity ID or no filter
Expected output: YourEntity Pydantic models with calculated metrics
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings
from nexus_api.data import mock_data
from nexus_api.db.tables import YourEntityTable
from nexus_api.models.your_entity import YourEntity
from nexus_api.services import alert_service


async def _build_your_entity_model(
    db: AsyncSession,
    entity: YourEntityTable,
) -> YourEntity:
    """
    Build a YourEntity model with all calculated fields.

    Args:
        db: Async database session
        entity: YourEntityTable instance

    Returns:
        YourEntity Pydantic model with calculated metrics
    """
    # Get related data
    related_data = await _get_related_data(db, entity.id)

    # Calculate metrics
    metrics = _calculate_metrics(related_data)

    # Generate alerts
    alerts = await alert_service.generate_alerts_for_your_entity(db, entity.id)

    return YourEntity(
        id=entity.id,
        name=entity.name,
        description=entity.description or "",
        metrics=metrics,
        alerts=alerts,
    )


async def get_all_your_entities(db: AsyncSession) -> list[YourEntity]:
    """
    Get all your entities with calculated metrics.

    Returns mock data if USE_MOCK_DATA is true, otherwise queries database.

    Args:
        db: Async database session

    Returns:
        List of YourEntity models with calculated metrics
    """
    if settings.use_mock_data:
        return mock_data.get_all_your_entities()

    stmt = select(YourEntityTable).order_by(YourEntityTable.name)
    result = await db.execute(stmt)
    entities = result.scalars().all()

    return [await _build_your_entity_model(db, entity) for entity in entities]


async def get_your_entity_by_id(
    db: AsyncSession,
    entity_id: str,
) -> YourEntity | None:
    """
    Get a your entity by ID with calculated metrics.

    Args:
        db: Async database session
        entity_id: Entity ID to retrieve

    Returns:
        YourEntity model or None if not found
    """
    if settings.use_mock_data:
        return mock_data.get_your_entity_by_id(entity_id)

    stmt = select(YourEntityTable).where(YourEntityTable.id == entity_id)
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()

    if entity is None:
        return None

    return await _build_your_entity_model(db, entity)
```

---

## Dashboard Components (NOT REFACTORED)

**Decision**: DashboardTemplate was **NOT created** - dashboards are domain-specific.

**Rationale**:
- Dashboard components are ~260 lines each, but most is domain-specific rendering
- Creating a generic template would introduce complex prop drilling
- Current implementation is readable and maintainable

**Recommendation**: Keep existing dashboard pattern when creating new dashboards.

### Example: Creating a New Dashboard (Current Pattern)

Use `RepositoryDashboard.tsx` or `PersonDashboard.tsx` as a template:

```typescript
// YourEntityDashboard.tsx
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useYourEntities } from "@/services/your-entities";
import { Loader2, AlertTriangle, Info } from "lucide-react";

const YourEntityDashboard = () => {
  const { data: entities, isLoading, error } = useYourEntities();
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  const selectedEntity = entities?.find(e => e.id === selectedEntityId) || entities?.[0];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Carregando entidades...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="w-4 h-4" />
        <AlertDescription>
          Erro ao carregar entidades: {error instanceof Error ? error.message : 'Erro desconhecido'}
        </AlertDescription>
      </Alert>
    );
  }

  if (!entities || entities.length === 0) {
    return (
      <Alert>
        <Info className="w-4 h-4" />
        <AlertDescription>Nenhuma entidade encontrada.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Grid of entities */}
      <div className="lg:col-span-2">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {entities.map(entity => (
            <Card
              key={entity.id}
              className={`cursor-pointer transition-all ${
                selectedEntityId === entity.id
                  ? "ring-2 ring-blue-500 shadow-lg"
                  : "hover:shadow-md"
              }`}
              onClick={() => setSelectedEntityId(entity.id)}
            >
              <CardHeader>
                <CardTitle>{entity.name}</CardTitle>
                <CardDescription>{entity.description}</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Entity-specific content */}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Details panel */}
      <div className="lg:col-span-1">
        {selectedEntity && (
          <Card>
            <CardHeader>
              <CardTitle>Detalhes</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Entity details */}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default YourEntityDashboard;
```

---

## Summary

**What WAS Refactored**:
- ✅ ValidationHelper pattern (recommended for all new modules)

**What was NOT Refactored** (and why):
- ❌ Router Factory - routers already simple and readable
- ❌ Service Base Class - services are domain-specific
- ❌ Dashboard Template - dashboards are domain-specific

**Key Principle**: **KISS (Keep It Simple, Stupid)** - don't create abstractions unless there's real duplication, not just similarity.

---

**Last Updated**: 2025-12-14
**Feature**: 002-code-review
