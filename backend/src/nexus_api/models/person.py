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

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: PersonRepository creation
    total_tests += 1
    try:
        repo = PersonRepository(
            name="test-repo",
            commits=100,
            lastActivity="2024-01-15",
            expertise=85,
        )
        if repo.name != "test-repo" or repo.expertise != 85:
            all_validation_failures.append(
                f"PersonRepository: Expected test-repo/85, got {repo.name}/{repo.expertise}"
            )
    except Exception as e:
        all_validation_failures.append(f"PersonRepository test failed: {e}")

    # Test 2: Technology creation
    total_tests += 1
    try:
        tech = Technology(name="Python", level=90)
        if tech.name != "Python" or tech.level != 90:
            all_validation_failures.append(
                f"Technology: Expected Python/90, got {tech.name}/{tech.level}"
            )
    except Exception as e:
        all_validation_failures.append(f"Technology test failed: {e}")

    # Test 3: Person creation with all fields
    total_tests += 1
    try:
        from nexus_api.models import AlertType

        person = Person(
            id="1",
            name="Ana Silva",
            email="ana.silva@company.com",
            avatar="AS",
            repositories=[PersonRepository(name="repo", commits=10, lastActivity="2024-01-01", expertise=80)],
            technologies=[Technology(name="TypeScript", level=95)],
            domains=["Relatórios"],
            recentActivity=47,
            alerts=[Alert(type=AlertType.INFO, message="Test")],
        )
        if person.id != "1" or person.name != "Ana Silva":
            all_validation_failures.append(
                f"Person: Expected id=1/name=Ana Silva, got {person.id}/{person.name}"
            )
    except Exception as e:
        all_validation_failures.append(f"Person creation test failed: {e}")

    # Test 4: Person serialization
    total_tests += 1
    try:
        person = Person(
            id="1",
            name="Test",
            email="test@example.com",
            avatar="TE",
            repositories=[],
            technologies=[],
            domains=[],
            recentActivity=0,
            alerts=[],
        )
        data = person.model_dump()
        if data["id"] != "1" or data["email"] != "test@example.com":
            all_validation_failures.append(
                f"Person serialization: Expected id=1/email=test@example.com, got {data['id']}/{data['email']}"
            )
    except Exception as e:
        all_validation_failures.append(f"Person serialization test failed: {e}")

    # Final validation result
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
