"""
FastAPI application entry point for Nexus API.

Docs: https://fastapi.tiangolo.com/

Sample input: HTTP requests to /api/v1/* endpoints
Expected output: JSON responses with repository, people, and analysis data
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from nexus_api.config import settings
from nexus_api.db.database import Base, async_session, engine
from nexus_api.routers import analysis, people, repositories

# Configure loguru
logger.add(
    "logs/nexus_api.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG" if settings.debug else "INFO",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Create database tables
    # Import tables to register them with Base.metadata
    from nexus_api.db import tables  # noqa: F401
    from nexus_api.services import seed_service

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    # Seed database with development data if auto_seed is enabled and database is empty
    if settings.auto_seed:
        async with async_session() as db:
            result = await seed_service.seed_database(db)
            if result.get("skipped"):
                logger.info("Database already has data, skipping seed")
            else:
                logger.info(
                    f"Database seeded: {result['repositories']} repos, "
                    f"{result['people']} people, {result['commits']} commits"
                )
    else:
        logger.info("Auto-seed disabled (AUTO_SEED=false), database will start empty")

    yield

    # Shutdown: Dispose engine
    await engine.dispose()
    logger.info("Database connection closed")


app = FastAPI(
    title="Nexus API",
    description="Backend API for Git Intelligence Platform",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(repositories.router, prefix=settings.api_v1_prefix)
app.include_router(people.router, prefix=settings.api_v1_prefix)
app.include_router(analysis.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import sys

    from fastapi.testclient import TestClient

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()
    client = TestClient(app)

    # Test 1: Health check endpoint returns 200
    validator.add_test(
        "Health check status",
        lambda: client.get("/health").status_code,
        200,
    )

    # Test 2: Health check returns correct body
    validator.add_test(
        "Health check body",
        lambda: client.get("/health").json(),
        {"status": "healthy"},
    )

    # Test 3: CORS headers present
    def test_cors_headers():
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET",
            },
        )
        return "access-control-allow-origin" in response.headers

    validator.add_test("CORS headers present", test_cors_headers, True)

    # Test 4: OpenAPI docs accessible
    validator.add_test(
        "OpenAPI status",
        lambda: client.get("/openapi.json").status_code,
        200,
    )

    # Test 5: OpenAPI has correct title
    validator.add_test(
        "OpenAPI title",
        lambda: client.get("/openapi.json").json().get("info", {}).get("title"),
        "Nexus API",
    )

    sys.exit(validator.run())
