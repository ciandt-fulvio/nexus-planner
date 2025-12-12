# Nexus Planner API

Backend API for the Git Intelligence Platform.

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run development server
uv run uvicorn src.nexus_api.main:app --reload --port 8000

# Run tests
uv run pytest
```

## API Documentation

When the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
