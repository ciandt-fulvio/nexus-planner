# Quickstart: Backend API with Mocked Data

**Feature**: 001-backend-api
**Date**: 2025-12-11

## Prerequisites

- Python 3.11+
- uv (Python package manager)
- Node.js 18+ with pnpm
- Git

## Backend Setup

### 1. Initialize Backend Project

```bash
cd backend
uv init
uv add fastapi uvicorn pydantic pydantic-settings loguru
uv add --dev pytest pytest-cov httpx mypy ruff
```

### 2. Create Environment File

Create `backend/.env`:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS Configuration
CORS_ORIGINS=http://localhost:8080

# API Configuration
API_V1_PREFIX=/api/v1
```

### 3. Run Backend Server

```bash
cd backend
uv run uvicorn src.nexus_api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Backend

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health check: `curl http://localhost:8000/api/v1/repositories`

## Frontend Setup

### 1. Create Environment File

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 2. Install Dependencies (if needed)

```bash
cd frontend
pnpm install
```

### 3. Run Frontend

```bash
cd frontend
pnpm dev
```

Frontend runs at http://localhost:8080

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/nexus_api --cov-report=term-missing

# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration
```

### Frontend Tests (future)

```bash
cd frontend
pnpm test
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/repositories` | List all repositories |
| GET | `/api/v1/repositories/{id}` | Get repository by ID |
| GET | `/api/v1/people` | List all people |
| GET | `/api/v1/people/{id}` | Get person by ID |
| POST | `/api/v1/analysis` | Analyze feature (mocked) |

## Development Workflow

### TDD Cycle (Required by Constitution)

1. **Write test first** (must fail)
   ```bash
   uv run pytest tests/unit/test_models.py::test_repository_model -v
   ```

2. **Implement minimal code** (make test pass)

3. **Refactor** (keep tests passing)

4. **Validate module**
   ```bash
   uv run python -m src.nexus_api.models.repository
   ```

### Code Quality Checks

```bash
cd backend

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/
```

## Troubleshooting

### CORS Errors

If frontend can't reach backend:
1. Verify backend is running on port 8000
2. Check `CORS_ORIGINS` in `backend/.env` includes `http://localhost:8080`
3. Restart backend server after .env changes

### Port Conflicts

- Backend default: 8000 (change with `PORT` env var)
- Frontend default: 8080 (change in `vite.config.ts`)

### Module Not Found

Ensure you're in the correct directory:
```bash
cd backend
uv run python -c "from src.nexus_api.main import app; print('OK')"
```
