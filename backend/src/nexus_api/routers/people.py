"""
People router for Nexus API.

Provides endpoints for people data.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Sample input: GET /api/v1/people
Expected output: List of Person objects as JSON
"""

from fastapi import APIRouter

from nexus_api.data.mock_data import get_all_people
from nexus_api.models.person import Person

router = APIRouter(
    prefix="/people",
    tags=["people"],
)


@router.get("", response_model=list[Person])
def list_people() -> list[Person]:
    """
    Get all people.

    Returns a list of all team members with their expertise metrics,
    repositories, technologies, and alerts.
    """
    return get_all_people()


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

    # Test 1: GET /api/v1/people returns 200
    total_tests += 1
    response = client.get("/api/v1/people")
    if response.status_code != 200:
        all_validation_failures.append(
            f"GET /people status: Expected 200, got {response.status_code}"
        )

    # Test 2: Response is a list of 5 people
    total_tests += 1
    data = response.json()
    if not isinstance(data, list) or len(data) != 5:
        all_validation_failures.append(
            f"GET /people data: Expected list of 5, got {type(data).__name__} of {len(data) if isinstance(data, list) else 'N/A'}"
        )

    # Test 3: First person has correct fields
    total_tests += 1
    if data:
        first = data[0]
        required_fields = ["id", "name", "email", "avatar", "repositories", "technologies"]
        missing = [f for f in required_fields if f not in first]
        if missing:
            all_validation_failures.append(
                f"First person missing fields: {missing}"
            )

    # Test 4: First person is Ana Silva
    total_tests += 1
    if data and data[0].get("name") != "Ana Silva":
        all_validation_failures.append(
            f"First person name: Expected 'Ana Silva', got '{data[0].get('name')}'"
        )

    # Final validation result
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
