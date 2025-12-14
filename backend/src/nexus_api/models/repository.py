"""
Repository models for Nexus API.

Defines Pydantic models for Repository and related entities.
Mirrors TypeScript interfaces from frontend/src/data/mockData.ts.

Docs: https://docs.pydantic.dev/latest/

Sample input: Repository data from mock_data.py
Expected output: Validated Repository model instances
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict

from nexus_api.models import Alert


class ActivityLevel(str, Enum):
    """Repository activity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STALE = "stale"


class TopContributor(BaseModel):
    """Top contributor with commit count and percentage."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    email: str
    commits: int
    percentage: int  # 0-100


class Hotspot(BaseModel):
    """File hotspot with change frequency and contributor count."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    path: str
    changes: int  # Positive integer
    lastModified: str  # Date string (e.g., "2024-01-15")
    contributors: int


class Repository(BaseModel):
    """Git repository with metrics."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    id: str
    name: str
    description: str
    lastCommit: str  # Date string (e.g., "2024-01-15")
    totalCommits: int
    contributors: int
    activity: ActivityLevel
    knowledgeConcentration: int  # 0-100
    topContributors: list[TopContributor]
    hotspots: list[Hotspot]
    dependencies: list[str]  # Repository names
    alerts: list[Alert]


if __name__ == "__main__":
    import sys

    from nexus_api.models import AlertType
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: ActivityLevel enum values
    validator.add_test(
        "ActivityLevel values",
        lambda: {level.value for level in ActivityLevel},
        {"high", "medium", "low", "stale"},
    )

    # Test 2: TopContributor creation
    validator.add_test(
        "TopContributor creation",
        lambda: (
            contributor := TopContributor(
                name="Alice", email="alice@test.com", commits=50, percentage=50
            ),
            (contributor.name, contributor.percentage),
        )[1],
        ("Alice", 50),
    )

    # Test 3: Hotspot creation
    validator.add_test(
        "Hotspot creation",
        lambda: (
            hotspot := Hotspot(
                path="src/main.ts", changes=100, lastModified="2024-01-15", contributors=5
            ),
            (hotspot.path, hotspot.changes),
        )[1],
        ("src/main.ts", 100),
    )

    # Test 4: Repository creation with all fields
    validator.add_test(
        "Repository creation",
        lambda: (
            repo := Repository(
                id="1",
                name="test-repo",
                description="Test description",
                lastCommit="2024-01-15",
                totalCommits=100,
                contributors=5,
                activity=ActivityLevel.HIGH,
                knowledgeConcentration=45,
                topContributors=[
                    TopContributor(
                        name="Alice", email="alice@test.com", commits=60, percentage=60
                    )
                ],
                hotspots=[
                    Hotspot(
                        path="src/main.ts",
                        changes=50,
                        lastModified="2024-01-15",
                        contributors=3,
                    )
                ],
                dependencies=["other-repo"],
                alerts=[Alert(type=AlertType.INFO, message="Test")],
            ),
            (repo.id, repo.name),
        )[1],
        ("1", "test-repo"),
    )

    # Test 5: Repository activity from string
    validator.add_test(
        "Repository activity from string",
        lambda: Repository(
            id="1",
            name="test",
            description="Test",
            lastCommit="2024-01-01",
            totalCommits=10,
            contributors=1,
            activity="medium",
            knowledgeConcentration=50,
            topContributors=[],
            hotspots=[],
            dependencies=[],
            alerts=[],
        ).activity,
        ActivityLevel.MEDIUM,
    )

    # Test 6: Repository serialization
    validator.add_test(
        "Repository serialization",
        lambda: Repository(
            id="1",
            name="test",
            description="Test",
            lastCommit="2024-01-01",
            totalCommits=10,
            contributors=1,
            activity="stale",
            knowledgeConcentration=50,
            topContributors=[],
            hotspots=[],
            dependencies=[],
            alerts=[],
        ).model_dump()["activity"],
        "stale",
    )

    sys.exit(validator.run())
