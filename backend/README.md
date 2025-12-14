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

## Database

The API uses SQLite with async support (aiosqlite). The database file is created automatically at `backend/nexus.db`.

### Automatic Seeding

On startup, the application automatically seeds the database with development data if empty:

- **5 repositories** with realistic metrics (commits, contributors, hotspots)
- **5 people** with expertise data (technologies, domains, activity)
- **Synthetic commits** linking people to repositories

This allows immediate use of all API endpoints without manual setup. The seed is skipped if the database already contains data.

To reset the database, simply delete `nexus.db` and restart the server:

```bash
rm nexus.db
uv run uvicorn src.nexus_api.main:app --reload --port 8000
```

## API Documentation

When the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
