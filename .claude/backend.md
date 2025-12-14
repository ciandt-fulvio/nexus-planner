# Backend Development Guide

**Python 3.11+ / FastAPI**

Este guia contém todas as informações específicas para desenvolvimento do backend. Sempre siga os princípios da constituição (`.specify/memory/constitution.md`) e o workflow TDD/BDD.

## Common Commands

```bash
# Setup and dependencies
cd backend && uv sync

# Development server (auto-reload on changes)
cd backend
uv run uvicorn src.nexus_api.main:app --reload --host 0.0.0.0 --port 8000

# Testing (MANDATORY before commits and PRs)
uv run pytest                              # Run all tests
uv run pytest -m unit                      # Fast battery (< 5s) - run before each commit
uv run pytest -m integration               # Slower integration tests
uv run pytest tests/unit/test_models.py    # Run single test file
uv run pytest --cov=src/nexus_api --cov-report=term-missing  # With coverage

# Code quality (run after tests pass, not before)
uv run mypy src/                           # Type checking
uv run ruff check src/                     # Linting
uv run ruff format src/                    # Formatting

# Validation function (each module's __main__ block)
uv run python -m nexus_api.main            # Validate main.py
```

## Backend Architecture

### API Design

- All routes use `/api/v1` prefix (configured in `settings.api_v1_prefix`)
- FastAPI automatic OpenAPI docs at `/docs` and `/openapi.json`
- Health check at `/health` (returns `{"status": "healthy"}`)

### Request/Response Flow

1. Request → FastAPI router (`routers/*.py`)
2. Router calls data source (currently `data/mock_data.py`)
3. Data validated through Pydantic models (`models/*.py`)
4. JSON response with camelCase fields (N815 ignored in ruff for API contract)

### CORS Configuration

- Configured via `settings.cors_origins_list` (comma-separated string from env)
- Default allows `http://localhost:8080` (frontend dev server)

### Logging

- Uses `loguru` library (not stdlib logging)
- Logs to `logs/nexus_api.log` with 10MB rotation, 7-day retention
- Debug level when `settings.debug=True`, else INFO

### Testing Pattern

- `tests/conftest.py` provides shared fixtures (`client`, `api_v1_prefix`)
- Integration tests use `TestClient` from FastAPI
- Unit tests marked with `@pytest.mark.unit`, integration with `@pytest.mark.integration`
- Every module has `if __name__ == "__main__"` validation block following CLAUDE.md validation standards

## Backend Standards

### Type Hints

- Required on all functions (enforced by mypy strict mode)
- Use native Python types (`list[str]`, not `List[str]`)

### Documentation

- Module docstring with: purpose, third-party docs links, sample input, expected output
- Google-style docstrings for public functions

### File Size

- Maximum 500 lines per file (enforced by constitution)
- Refactor if exceeding limit

### Validation Functions

- Every file needs `if __name__ == "__main__"` block testing with real data
- **USE ValidationHelper** from `testing.validation_helpers` module (consolidated pattern)
- Must track ALL failures, report count, exit with code 1 if any fail
- Never print "All Tests Passed" unless explicitly verified

**ValidationHelper Pattern (RECOMMENDED)**:
```python
if __name__ == "__main__":
    import sys
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Add tests using lambda or functions
    validator.add_test("Test name", lambda: some_function(test_data), expected_value)
    validator.add_test("Another test", test_function, expected_result)

    sys.exit(validator.run())  # Exits 0 if all pass, 1 if any fail
```

**Legacy Pattern (before ValidationHelper)**:
```python
if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: Basic functionality
    total_tests += 1
    result = some_function(test_data)
    expected = expected_value
    if result != expected:
        all_validation_failures.append(f"Test 1: Expected {expected}, got {result}")

    # Final validation result
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
```

## Testing Strategy

### Fast Test Battery (< 5s total, < 0.5s per test)

```bash
uv run pytest -m unit  # Must complete in < 5s
```

**What to include**:
- Unit tests for models, utilities, core logic
- Critical integration tests for main API endpoints
- Tests that prevent obvious regressions

**What to exclude** (move to slow battery):
- Tests requiring database setup
- Tests with external API calls
- Tests with complex fixtures

### Complete Test Battery (before PR)

```bash
uv run pytest                    # All tests
uv run pytest --cov=src/nexus_api --cov-report=term-missing  # With coverage
uv run mypy src/
uv run ruff check src/
```

## Adding a New Endpoint (TDD Workflow)

1. **Write tests** in `tests/integration/test_[router].py` (commit: `test: add tests for [endpoint]`)
2. **Verify tests fail** (document failure)
3. **Create Pydantic model** in `models/[domain].py`
4. **Create router function** in `routers/[domain].py`
5. **Register router** in `main.py` if new router file
6. **Add mock data** in `data/mock_data.py` (if needed)
7. **Verify tests pass**
8. **Run validation function** (`uv run python -m nexus_api.[module]`)
9. **Commit implementation** (commit: `feat: implement [endpoint]`)

## API Contract with Frontend

**Field Naming**: Backend uses `camelCase` in JSON responses (not `snake_case`) to match frontend TypeScript conventions.

**Example**:
```python
# Backend model (models/repository.py)
from pydantic import BaseModel, Field

class Repository(BaseModel):
    repository_id: str = Field(alias="repositoryId")  # API uses camelCase
    last_commit: str = Field(alias="lastCommit")
    contributor_count: int = Field(alias="contributorCount")

# Frontend expects:
# {
#   "repositoryId": "...",
#   "lastCommit": "...",
#   "contributorCount": 42
# }
```

## Common Patterns

### Pydantic Model with Aliases

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    internal_name: str = Field(alias="externalName")

    class Config:
        populate_by_name = True  # Allows both names in input
```

### Router with Dependency Injection

```python
from fastapi import APIRouter, HTTPException
from nexus_api.models.repository import Repository

router = APIRouter(tags=["repositories"])

@router.get("/repositories/{repo_id}", response_model=Repository)
def get_repository(repo_id: str) -> Repository:
    """Get repository by ID."""
    # Implementation
    if not found:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repository
```

### Loguru Logging

```python
from loguru import logger

def process_data(data: dict) -> dict:
    """Process incoming data."""
    logger.info(f"Processing data with {len(data)} items")
    try:
        result = perform_processing(data)
        logger.debug(f"Processing result: {result}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

## Environment Configuration

Create `backend/.env` based on `.env.example`:

```env
# API Settings
DEBUG=true
CORS_ORIGINS=http://localhost:8080,http://localhost:5173

# Logging
LOG_LEVEL=DEBUG
```

## Notes

- **Port**: Backend runs on `:8000` by default
- **API Prefix**: All routes use `/api/v1` prefix
- **Mock Data**: Currently in `backend/src/nexus_api/data/mock_data.py`
- **Logs**: Check `backend/logs/nexus_api.log` for debugging
- **OpenAPI Docs**: Available at `http://localhost:8000/docs`

## References

For global Python standards and validation requirements:
@~/.claude/CLAUDE.md
