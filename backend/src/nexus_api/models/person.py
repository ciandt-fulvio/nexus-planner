"""
Person models for Nexus API.

Defines Pydantic models for Person and related entities.
Mirrors TypeScript interfaces from frontend/src/data/mockData.ts.

Docs: https://docs.pydantic.dev/latest/

Sample input: Person data from mock_data.py
Expected output: Validated Person model instances
"""

from pydantic import BaseModel, ConfigDict

from nexus_api.models import Alert


class PersonRepository(BaseModel):
    """Repository info for a person."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    commits: int
    lastActivity: str  # Date string
    expertise: int  # 0-100


class Technology(BaseModel):
    """Technology skill with proficiency level."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    level: int  # 0-100


class Person(BaseModel):
    """Team member with expertise metrics."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    id: str
    name: str
    email: str
    avatar: str  # Initials (e.g., "AS")
    repositories: list[PersonRepository]
    technologies: list[Technology]
    domains: list[str]  # Business domain names
    recentActivity: int  # Commits in last 30 days
    alerts: list[Alert]


if __name__ == "__main__":
    import sys

    from nexus_api.models import AlertType
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: PersonRepository creation
    validator.add_test(
        "PersonRepository creation",
        lambda: (
            repo := PersonRepository(
                name="test-repo",
                commits=100,
                lastActivity="2024-01-15",
                expertise=85,
            ),
            (repo.name, repo.expertise),
        )[1],
        ("test-repo", 85),
    )

    # Test 2: Technology creation
    validator.add_test(
        "Technology creation",
        lambda: (
            tech := Technology(name="Python", level=90),
            (tech.name, tech.level),
        )[1],
        ("Python", 90),
    )

    # Test 3: Person creation with all fields
    validator.add_test(
        "Person creation",
        lambda: (
            person := Person(
                id="1",
                name="Ana Silva",
                email="ana.silva@company.com",
                avatar="AS",
                repositories=[
                    PersonRepository(
                        name="repo", commits=10, lastActivity="2024-01-01", expertise=80
                    )
                ],
                technologies=[Technology(name="TypeScript", level=95)],
                domains=["Relatórios"],
                recentActivity=47,
                alerts=[Alert(type=AlertType.INFO, message="Test")],
            ),
            (person.id, person.name),
        )[1],
        ("1", "Ana Silva"),
    )

    # Test 4: Person serialization
    validator.add_test(
        "Person serialization",
        lambda: (
            data := Person(
                id="1",
                name="Test",
                email="test@example.com",
                avatar="TE",
                repositories=[],
                technologies=[],
                domains=[],
                recentActivity=0,
                alerts=[],
            ).model_dump(),
            (data["id"], data["email"]),
        )[1],
        ("1", "test@example.com"),
    )

    sys.exit(validator.run())
