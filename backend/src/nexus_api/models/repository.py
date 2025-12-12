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
    """Top contributor with percentage of commits."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    percentage: int  # 0-100


class Hotspot(BaseModel):
    """File hotspot with change frequency."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    path: str
    changes: int  # Positive integer


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

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: ActivityLevel enum values
    total_tests += 1
    try:
        expected_values = {"high", "medium", "low", "stale"}
        actual_values = {level.value for level in ActivityLevel}
        if actual_values != expected_values:
            all_validation_failures.append(
                f"ActivityLevel values: Expected {expected_values}, got {actual_values}"
            )
    except Exception as e:
        all_validation_failures.append(f"ActivityLevel test failed: {e}")

    # Test 2: TopContributor creation
    total_tests += 1
    try:
        contributor = TopContributor(name="Alice", percentage=50)
        if contributor.name != "Alice" or contributor.percentage != 50:
            all_validation_failures.append(
                f"TopContributor: Expected Alice/50, got {contributor.name}/{contributor.percentage}"
            )
    except Exception as e:
        all_validation_failures.append(f"TopContributor test failed: {e}")

    # Test 3: Hotspot creation
    total_tests += 1
    try:
        hotspot = Hotspot(path="src/main.ts", changes=100)
        if hotspot.path != "src/main.ts" or hotspot.changes != 100:
            all_validation_failures.append(
                f"Hotspot: Expected src/main.ts/100, got {hotspot.path}/{hotspot.changes}"
            )
    except Exception as e:
        all_validation_failures.append(f"Hotspot test failed: {e}")

    # Test 4: Repository creation with all fields
    total_tests += 1
    try:
        from nexus_api.models import AlertType

        repo = Repository(
            id="1",
            name="test-repo",
            description="Test description",
            lastCommit="2024-01-15",
            totalCommits=100,
            contributors=5,
            activity=ActivityLevel.HIGH,
            knowledgeConcentration=45,
            topContributors=[TopContributor(name="Alice", percentage=60)],
            hotspots=[Hotspot(path="src/main.ts", changes=50)],
            dependencies=["other-repo"],
            alerts=[Alert(type=AlertType.INFO, message="Test")],
        )
        if repo.id != "1" or repo.name != "test-repo":
            all_validation_failures.append(
                f"Repository: Expected id=1/name=test-repo, got {repo.id}/{repo.name}"
            )
    except Exception as e:
        all_validation_failures.append(f"Repository creation test failed: {e}")

    # Test 5: Repository activity from string
    total_tests += 1
    try:
        repo = Repository(
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
        )
        if repo.activity != ActivityLevel.MEDIUM:
            all_validation_failures.append(
                f"Repository activity: Expected MEDIUM, got {repo.activity}"
            )
    except Exception as e:
        all_validation_failures.append(f"Repository activity test failed: {e}")

    # Test 6: Repository serialization
    total_tests += 1
    try:
        repo = Repository(
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
        )
        data = repo.model_dump()
        if data["activity"] != "stale":
            all_validation_failures.append(
                f"Repository serialization: Expected activity='stale', got {data['activity']}"
            )
    except Exception as e:
        all_validation_failures.append(f"Repository serialization test failed: {e}")

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
