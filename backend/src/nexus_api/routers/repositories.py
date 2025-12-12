"""
Repositories router for Nexus API.

Provides endpoints for repository data.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Sample input: GET /api/v1/repositories
Expected output: List of Repository objects as JSON
"""

from fastapi import APIRouter, HTTPException

from nexus_api.data.mock_data import get_all_repositories, get_repository_by_id
from nexus_api.models.repository import Repository

router = APIRouter(
    prefix="/repositories",
    tags=["repositories"],
)


@router.get("", response_model=list[Repository])
def list_repositories() -> list[Repository]:
    """
    Get all repositories.

    Returns a list of all repositories with their metrics,
    contributors, hotspots, and alerts.
    """
    return get_all_repositories()


@router.get("/{repo_id}", response_model=Repository)
def get_repository(repo_id: str) -> Repository:
    """
    Get a repository by ID.

    Args:
        repo_id: The repository ID to look up.

    Returns:
        The repository with the given ID.

    Raises:
        HTTPException: 404 if repository not found.
    """
    repo = get_repository_by_id(repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    return repo


if __name__ == "__main__":
    import sys

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    all_validation_failures: list[str] = []
    total_tests = 0

    # Create test app
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    client = TestClient(app)

    # Test 1: GET /api/v1/repositories returns 200
    total_tests += 1
    response = client.get("/api/v1/repositories")
    if response.status_code != 200:
        all_validation_failures.append(
            f"GET /repositories status: Expected 200, got {response.status_code}"
        )

    # Test 2: Response is a list of 5 repositories
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
