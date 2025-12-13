"""
Repositories router for Nexus API.

Provides endpoints for repository data with calculated metrics.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/
Docs: https://fastapi.tiangolo.com/tutorial/dependencies/

Sample input: GET /api/v1/repositories
Expected output: List of Repository objects as JSON
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.data import mock_data
from nexus_api.db.database import get_db
from nexus_api.models.repository import Repository
from nexus_api.services import repository_service

router = APIRouter(
    prefix="/repositories",
    tags=["repositories"],
)


@router.get("", response_model=list[Repository])
async def list_repositories(db: AsyncSession = Depends(get_db)) -> list[Repository]:
    """
    Get all repositories with calculated metrics.

    Returns a list of all repositories with their metrics,
    contributors, hotspots, and alerts.

    Falls back to mock data if database is empty.
    """
    repos = await repository_service.get_all_repositories(db)
    if not repos:
        # Fallback to mock data for development
        return mock_data.get_all_repositories()
    return repos


@router.get("/{repo_id}", response_model=Repository)
async def get_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> Repository:
    """
    Get a repository by ID with calculated metrics.

    Args:
        repo_id: The repository ID to look up.
        db: Database session from dependency injection.

    Returns:
        The repository with the given ID.

    Raises:
        HTTPException: 404 if repository not found.
    """
    repo = await repository_service.get_repository_by_id(db, repo_id)
    if repo is not None:
        return repo

    # Fallback to mock data
    mock_repo = mock_data.get_repository_by_id(repo_id)
    if mock_repo is None:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    return mock_repo


if __name__ == "__main__":
    import sys

    from fastapi.testclient import TestClient

    # Import the main app to test with full context
    from nexus_api.main import app

    all_validation_failures: list[str] = []
    total_tests = 0

    # Use main app with lifespan and database
    client = TestClient(app)

    # Test 1: GET /api/v1/repositories returns 200
    total_tests += 1
    response = client.get("/api/v1/repositories")
    if response.status_code != 200:
        all_validation_failures.append(
            f"GET /repositories status: Expected 200, got {response.status_code}"
        )

    # Test 2: Response is a list of 5 repositories (from mock data fallback)
    total_tests += 1
    data = response.json()
    if not isinstance(data, list) or len(data) != 5:
        all_validation_failures.append(
            f"GET /repositories data: Expected list of 5, got {type(data).__name__} of {len(data) if isinstance(data, list) else 'N/A'}"
        )

    # Test 3: First repository has correct fields
    total_tests += 1
    if data:
        first = data[0]
        required_fields = ["id", "name", "description", "activity", "topContributors"]
        missing = [f for f in required_fields if f not in first]
        if missing:
            all_validation_failures.append(f"First repo missing fields: {missing}")

    # Test 4: First repository is reports-service
    total_tests += 1
    if data and data[0].get("name") != "reports-service":
        all_validation_failures.append(
            f"First repo name: Expected 'reports-service', got '{data[0].get('name')}'"
        )

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
