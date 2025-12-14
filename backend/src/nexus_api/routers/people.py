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

    from nexus_api.main import app
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()
    client = TestClient(app)

    # Test 1: GET /api/v1/people returns 200
    validator.add_test(
        "GET /people status",
        lambda: client.get("/api/v1/people").status_code,
        200,
    )

    # Test 2: Response is a list of 5 people
    def test_response_structure():
        response = client.get("/api/v1/people")
        data = response.json()
        return (isinstance(data, list), len(data))

    validator.add_test("Response structure", test_response_structure, (True, 5))

    # Test 3: First person has correct fields
    def test_first_person_fields():
        data = client.get("/api/v1/people").json()
        if data:
            first = data[0]
            required_fields = ["id", "name", "email", "avatar", "repositories", "technologies"]
            missing = [f for f in required_fields if f not in first]
            return len(missing) == 0
        return False

    validator.add_test("First person has required fields", test_first_person_fields, True)

    # Test 4: First person is Ana Silva
    validator.add_test(
        "First person name",
        lambda: client.get("/api/v1/people").json()[0].get("name"),
        "Ana Silva",
    )

    sys.exit(validator.run())
