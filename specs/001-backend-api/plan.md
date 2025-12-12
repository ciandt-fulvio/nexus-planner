# Implementation Plan: Backend API with Mocked Data

**Branch**: `001-backend-api` | **Date**: 2025-12-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-api/spec.md`

## Summary

Create a Python FastAPI backend serving mocked data for the Git Intelligence Platform frontend. The API provides endpoints for repositories, people, and feature analysis - all returning static data that matches the existing frontend TypeScript interfaces. Additionally, create a frontend API service layer using TanStack Query to consume these endpoints.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend services)
**Primary Dependencies**: FastAPI, Pydantic, uvicorn, python-dotenv (backend); TanStack Query (frontend)
**Storage**: SQLite (prepared for future use, not required for mocked data phase)
**Testing**: pytest with markers (backend), Vitest (frontend)
**Target Platform**: Local development server (macOS/Linux)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <1s response time for all endpoints (per SC-001, SC-002, SC-003)
**Constraints**: CORS enabled for frontend port 8080, API on port 8000 with `/api/v1` prefix
**Scale/Scope**: 5 repositories, 5 people, 1 static feature analysis (mocked data)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. TDD (Non-Negotiable) | ✅ PASS | Tests written before implementation; pytest markers for unit/integration |
| II. Type Safety | ✅ PASS | Pydantic models for API contracts; mypy strict mode |
| III. Module Size (<500 lines) | ✅ PASS | Small focused modules planned |
| IV. Real Data Validation | ✅ PASS | Each module has `if __name__ == "__main__":` validation block |
| V. Repository Pattern | ⚠️ DEFERRED | Not needed for mocked data phase; no database operations |
| VI. Observability | ✅ PASS | loguru for structured logging |

**Gate Result**: PASS - All applicable principles satisfied. Repository pattern deferred as no database operations in MVP.

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── .env                     # Environment configuration
├── pyproject.toml           # Python project config (uv)
├── src/
│   └── nexus_api/
│       ├── __init__.py
│       ├── main.py          # FastAPI app entry point
│       ├── config.py        # Settings from .env
│       ├── models/          # Pydantic models
│       │   ├── __init__.py
│       │   ├── repository.py
│       │   ├── person.py
│       │   └── analysis.py
│       ├── routers/         # API route handlers
│       │   ├── __init__.py
│       │   ├── repositories.py
│       │   ├── people.py
│       │   └── analysis.py
│       └── data/            # Mocked data
│           ├── __init__.py
│           └── mock_data.py
└── tests/
    ├── conftest.py          # Shared fixtures
    ├── unit/
    │   └── test_models.py
    └── integration/
        └── test_api.py

frontend/
├── src/
│   ├── lib/
│   │   └── api.ts           # API client configuration
│   ├── services/            # NEW: API service layer
│   │   ├── repositories.ts  # Repository API hooks
│   │   ├── people.ts        # People API hooks
│   │   └── analysis.ts      # Analysis API hooks
│   └── ... (existing structure unchanged)
└── .env                     # API URL configuration
```

**Structure Decision**: Web application structure with separate `backend/` and `frontend/` directories. Backend follows FastAPI best practices with routers, models, and data separation. Frontend adds a `services/` directory for TanStack Query hooks without modifying existing components.

## Complexity Tracking

> No constitution violations requiring justification. Repository pattern deferred (not violated) as mocked data phase has no database operations.
