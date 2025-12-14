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

    Database is seeded automatically on startup in development mode.
    """
    return await repository_service.get_all_repositories(db)


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
    if repo is None:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    return repo


if __name__ == "__main__":
    import sys

    from fastapi.testclient import TestClient

    from nexus_api.main import app
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()
    client = TestClient(app)

    # Test 1: GET /api/v1/repositories returns 200
    validator.add_test(
        "GET /repositories status",
        lambda: client.get("/api/v1/repositories").status_code,
        200,
    )

    # Test 2: Response is a list of 5 repositories
    def test_response_structure():
        response = client.get("/api/v1/repositories")
        data = response.json()
        return (isinstance(data, list), len(data))

    validator.add_test("Response structure", test_response_structure, (True, 5))

    # Test 3: First repository has correct fields
    def test_first_repo_fields():
        data = client.get("/api/v1/repositories").json()
        if data:
            first = data[0]
            required_fields = ["id", "name", "description", "activity", "topContributors"]
            missing = [f for f in required_fields if f not in first]
            return len(missing) == 0
        return False

    validator.add_test("First repo has required fields", test_first_repo_fields, True)

    # Test 4: First repository is reports-service
    validator.add_test(
        "First repo name",
        lambda: client.get("/api/v1/repositories").json()[0].get("name"),
        "reports-service",
    )

    sys.exit(validator.run())
