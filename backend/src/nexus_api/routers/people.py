"""
People router for Nexus API.

Provides endpoints for people data with calculated metrics.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/
Docs: https://fastapi.tiangolo.com/tutorial/dependencies/

Sample input: GET /api/v1/people
Expected output: List of Person objects as JSON
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.database import get_db
from nexus_api.models.person import Person
from nexus_api.services import person_service

router = APIRouter(
    prefix="/people",
    tags=["people"],
)


@router.get("", response_model=list[Person])
async def list_people(db: AsyncSession = Depends(get_db)) -> list[Person]:
    """
    Get all people with calculated metrics.

    Returns a list of all team members with their expertise metrics,
    repositories, technologies, and alerts.

    Database is seeded automatically on startup in development mode.
    """
    return await person_service.get_all_people(db)


@router.get("/{person_id}", response_model=Person)
async def get_person(
    person_id: str,
    db: AsyncSession = Depends(get_db),
) -> Person:
    """
    Get a person by ID with calculated metrics.

    Args:
        person_id: The person ID to look up.
        db: Database session from dependency injection.

    Returns:
        The person with the given ID.

    Raises:
        HTTPException: 404 if person not found.
    """
    person = await person_service.get_person_by_id(db, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
    return person


if __name__ == "__main__":
    import sys

    from fastapi.testclient import TestClient

    # Import the main app to test with full context
    from nexus_api.main import app

    all_validation_failures: list[str] = []
    total_tests = 0

    # Use main app with lifespan and database
    client = TestClient(app)

    # Test 1: GET /api/v1/people returns 200
    total_tests += 1
    response = client.get("/api/v1/people")
    if response.status_code != 200:
        all_validation_failures.append(
            f"GET /people status: Expected 200, got {response.status_code}"
        )

    # Test 2: Response is a list of 5 people (from mock data fallback)
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
            all_validation_failures.append(f"First person missing fields: {missing}")

    # Test 4: First person is Ana Silva
    total_tests += 1
    if data and data[0].get("name") != "Ana Silva":
        all_validation_failures.append(
            f"First person name: Expected 'Ana Silva', got '{data[0].get('name')}'"
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
