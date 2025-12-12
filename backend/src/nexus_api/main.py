"""
FastAPI application entry point for Nexus API.

Docs: https://fastapi.tiangolo.com/

Sample input: HTTP requests to /api/v1/* endpoints
Expected output: JSON responses with repository, people, and analysis data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from nexus_api.config import settings
from nexus_api.routers import analysis, people, repositories

# Configure loguru
logger.add(
    "logs/nexus_api.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG" if settings.debug else "INFO",
)

app = FastAPI(
    title="Nexus API",
    description="Backend API for Git Intelligence Platform",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
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

    all_validation_failures: list[str] = []
    total_tests = 0

    client = TestClient(app)

    # Test 1: Health check endpoint
    total_tests += 1
    try:
        response = client.get("/health")
        if response.status_code != 200:
            all_validation_failures.append(
                f"Health check status: Expected 200, got {response.status_code}"
            )
        expected_body = {"status": "healthy"}
        if response.json() != expected_body:
            all_validation_failures.append(
                f"Health check body: Expected {expected_body}, got {response.json()}"
            )
    except Exception as e:
        all_validation_failures.append(f"Health check failed: {e}")

    # Test 2: CORS headers present
    total_tests += 1
    try:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET",
            },
        )
        if "access-control-allow-origin" not in response.headers:
            all_validation_failures.append("CORS: Missing access-control-allow-origin header")
    except Exception as e:
        all_validation_failures.append(f"CORS test failed: {e}")

    # Test 3: OpenAPI docs accessible
    total_tests += 1
    try:
        response = client.get("/openapi.json")
        if response.status_code != 200:
            all_validation_failures.append(
                f"OpenAPI status: Expected 200, got {response.status_code}"
            )
        openapi = response.json()
        if openapi.get("info", {}).get("title") != "Nexus API":
            all_validation_failures.append(
                f"OpenAPI title: Expected 'Nexus API', got {openapi.get('info', {}).get('title')}"
            )
    except Exception as e:
        all_validation_failures.append(f"OpenAPI test failed: {e}")

    # Final validation result
    if all_validation_failures:
        print(
            f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:"
        )
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
