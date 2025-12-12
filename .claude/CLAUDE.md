# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

Nexus Planner is a Git Intelligence Platform designed to help development teams make informed planning decisions. It provides repository analysis, team expertise mapping, and AI-powered feature impact analysis.

**Architecture**: Full-stack web application with separated backend (Python/FastAPI) and frontend (React/TypeScript/Vite).

**Current Status**: Prototype phase with mocked data serving three dashboards: Repository Dashboard, Person Dashboard, and Planning Assistant.

## Constitution

**CRITICAL**: All development MUST follow `.specify/memory/constitution.md`. The constitution defines non-negotiable principles:

1. **Test-First Development (TDD/BDD)** - Tests written before code, must fail first
2. **Fast Test Battery** - Unit/integration tests < 5s total (each test < 0.5s), run before every commit
3. **Complete Test Battery** - All tests pass before opening PR
4. **Frequent Commits** - Commit at each task phase or small objective completion
5. **Simplicity** - Functions < 30 lines, files < 500 lines (except HTML/TSX up to 1000 lines)
6. **Language** - Code in English, documentation in Portuguese, i18n ready (EN/PT)

**Enforcement**: Violations of Principle I (TDD/BDD) are grounds for immediate PR rejection.

## Context-Aware Behavior

**Quando trabalhar em arquivos dentro de `/backend`**: Siga as diretrizes em @.claude/backend.md
**Quando trabalhar em arquivos dentro de `/frontend`**: Siga as diretrizes em @.claude/frontend.md

Esses arquivos contêm comandos específicos, padrões arquiteturais, e workflows de desenvolvimento para cada contexto.

## Project Structure

```
nexus-planner/
├── backend/              # Python FastAPI backend
│   ├── src/nexus_api/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── config.py    # Settings via pydantic-settings
│   │   ├── models/      # Pydantic models (repository, person, analysis)
│   │   ├── routers/     # API route handlers (repositories, people, analysis)
│   │   └── data/        # Mock data generators
│   └── tests/
│       ├── unit/        # Fast unit tests (< 0.5s each)
│       └── integration/ # Integration tests with TestClient
│
├── frontend/            # React + Vite + shadcn/ui frontend
│   ├── src/
│   │   ├── components/  # React components (3 dashboards + shadcn/ui)
│   │   ├── services/    # API client functions (repositories, people, analysis)
│   │   ├── lib/         # API utilities (api.ts with apiFetch/apiGet/apiPost)
│   │   ├── pages/       # Route components (Index, NotFound)
│   │   └── hooks/       # Custom hooks (use-mobile, use-toast)
│   └── public/
│
├── .specify/            # Spec-Kit workflow templates and constitution
│
└── specs/               # Feature specifications and plans
```

## Testing Strategy (MANDATORY)

### Test-First Workflow (Constitution Principle I)

**Red-Green-Refactor Cycle**:
1. Write test (commit: `test: add tests for [feature]`)
2. Verify test FAILS (document failure)
3. Implement minimum code to pass test
4. Commit implementation (commit: `feat: implement [feature]`)
5. Refactor if needed (commit: `refactor: improve [aspect]`)

### Fast Test Battery (< 5s total, < 0.5s per test)

**Backend**:
```bash
cd backend
uv run pytest -m unit  # Must complete in < 5s
```

**Frontend**:
```bash
cd frontend
# (Add test commands when frontend tests are implemented)
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

**Backend**:
```bash
cd backend
uv run pytest                    # All tests
uv run pytest --cov=src/nexus_api --cov-report=term-missing  # With coverage
uv run mypy src/
uv run ruff check src/
```

**Frontend**:
```bash
cd frontend
pnpm lint
# (Add test commands when frontend tests are implemented)
```

## Development Workflow

### Commit Strategy (Constitution Principle IV)

**When to Commit**:
- After each task phase completion
- After each small logical objective (e.g., one function implemented and tested)
- Before switching context or tasks

**Commit Message Format**:
- `test: add tests for [feature]` - Test commits (before implementation)
- `feat: implement [feature]` - Feature implementation
- `fix: resolve [issue]` - Bug fixes
- `refactor: improve [aspect]` - Code improvements without behavior change
- `docs: update [documentation]` - Documentation updates
- `chore: [maintenance task]` - Build, dependencies, tooling

**Commit Requirements**:
- Each commit represents working code
- Fast test battery passes before commit
- Commits are atomic (single logical change)

### Pull Request Process (Constitution Principle III)

**Before Opening PR**:
1. Run complete test battery (all tests must pass)
2. Run linting and type checking
3. Verify acceptance criteria from user stories
4. Update documentation if needed

**PR Description Must Include**:
- Summary of changes
- Test results confirmation
- Links to related specs/issues
- Breaking changes (if any)

## MCP Tools Integration

**DevTools (Chrome)**:
- Always use DevTools to smoke test when a new frontend feature is added
- Verify: UI rendering, API calls in Network tab, console errors, responsive behavior

**Context7**:
- Use Context7 to look up current library documentation
- Especially helpful for FastAPI, TanStack Query, shadcn/ui, Pydantic

## API Contract (Backend ↔ Frontend)

**Field Naming**: Backend uses `camelCase` in JSON responses (not `snake_case`) to match frontend TypeScript conventions.

**Example**:
```python
# Backend model (models/repository.py)
from pydantic import BaseModel, Field

class Repository(BaseModel):
    repository_id: str = Field(alias="repositoryId")  # API uses camelCase
    last_commit: str = Field(alias="lastCommit")

# Frontend type (services/repositories.ts)
interface Repository {
  repositoryId: string;
  lastCommit: string;
}
```

## Quick Start

### Running the Application

**Backend** (Port 8000):
```bash
cd backend
uv sync
uv run uvicorn src.nexus_api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (Port 8080):
```bash
cd frontend
pnpm install
pnpm dev
```

**Access**:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Notes

- **API Base URL**: Backend runs on `:8000`, frontend on `:8080` (avoid conflicts)
- **CORS**: Configured for `localhost:8080` by default
- **Mock Data**: Currently all data is mocked in `backend/src/nexus_api/data/mock_data.py`
- **Logging**: Backend uses loguru (check `logs/nexus_api.log` for debugging)
- **Environment Variables**: Backend uses `.env` in `backend/` directory, frontend uses `frontend/.env`

## Imports and References

**Guias específicos por contexto**:
- Backend development: @.claude/backend.md
- Frontend development: @.claude/frontend.md

**Padrões globais de desenvolvimento Python**:
- @~/.claude/CLAUDE.md

**Constituição do projeto (NON-NEGOTIABLE)**:
- @.specify/memory/constitution.md
