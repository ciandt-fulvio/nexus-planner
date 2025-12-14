"""
Pure functions for calculating repository and person metrics.

All functions are side-effect free and easily testable.
Uses configurable thresholds from settings.

Docs: https://docs.pydantic.dev/latest/

Sample input: Commit aggregation data
Expected output: Calculated metrics (activity level, concentration, etc.)
"""

from datetime import date
from typing import Any

from nexus_api.config import settings
from nexus_api.models.repository import ActivityLevel, Hotspot, TopContributor


def calculate_activity_level(
    commits_last_30_days: int,
    high_threshold: int | None = None,
    medium_threshold: int | None = None,
    low_threshold: int | None = None,
) -> ActivityLevel:
    """
    Calculate activity level based on commit count in last 30 days.

    Args:
        commits_last_30_days: Number of commits in the last 30 days
        high_threshold: Override for high activity threshold
        medium_threshold: Override for medium activity threshold
        low_threshold: Override for low activity threshold

    Returns:
        ActivityLevel enum value (HIGH, MEDIUM, LOW, or STALE)
    """
    high = high_threshold if high_threshold is not None else settings.activity_high_threshold
    medium = medium_threshold if medium_threshold is not None else settings.activity_medium_threshold
    low = low_threshold if low_threshold is not None else settings.activity_low_threshold

    if commits_last_30_days >= high:
        return ActivityLevel.HIGH
    elif commits_last_30_days >= medium:
        return ActivityLevel.MEDIUM
    elif commits_last_30_days >= low:
        return ActivityLevel.LOW
    else:
        return ActivityLevel.STALE


def calculate_knowledge_concentration(
    contributor_commits: list[dict[str, Any]],
    total_commits: int,
) -> int:
    """
    Calculate knowledge concentration as percentage of top contributor.

    Args:
        contributor_commits: List of dicts with author_email and count
        total_commits: Total number of commits

    Returns:
        Percentage (0-100) of commits by top contributor
    """
    if total_commits == 0 or not contributor_commits:
        return 0

    # Find the top contributor's commit count
    top_count = max(c.get("count", 0) for c in contributor_commits)
    return int((top_count / total_commits) * 100)


def calculate_top_contributors(
    contributor_commits: list[dict[str, Any]],
    total_commits: int,
    limit: int | None = None,
) -> list[TopContributor]:
    """
    Calculate top contributors with commit counts and percentages.

    Args:
        contributor_commits: List of dicts with author_email, author_name, count
        total_commits: Total number of commits
        limit: Maximum number of contributors to return

    Returns:
        List of TopContributor models, sorted by commit count descending
    """
    if total_commits == 0 or not contributor_commits:
        return []

    max_results = limit if limit is not None else settings.top_contributors_limit

    # Sort by count descending
    sorted_contributors = sorted(
        contributor_commits,
        key=lambda c: c.get("count", 0),
        reverse=True,
    )

    result = []
    for c in sorted_contributors[:max_results]:
        count = c.get("count", 0)
        percentage = int((count / total_commits) * 100) if total_commits > 0 else 0
        result.append(
            TopContributor(
                name=c.get("author_name", "Unknown"),
                email=c.get("author_email", ""),
                commits=count,
                percentage=percentage,
            )
        )

    return result


def calculate_hotspots(
    file_changes: list[dict[str, Any]],
    limit: int | None = None,
) -> list[Hotspot]:
    """
    Calculate file hotspots (most frequently changed files).

    Args:
        file_changes: List of dicts with path, changes, last_modified, contributors
        limit: Maximum number of hotspots to return

    Returns:
        List of Hotspot models, sorted by change count descending
    """
    if not file_changes:
        return []

    max_results = limit if limit is not None else settings.top_hotspots_limit

    # Sort by changes descending
    sorted_files = sorted(
        file_changes,
        key=lambda f: f.get("changes", 0),
        reverse=True,
    )

    result = []
    for f in sorted_files[:max_results]:
        last_modified = f.get("last_modified")
        if isinstance(last_modified, date):
            last_modified_str = last_modified.isoformat()
        else:
            last_modified_str = str(last_modified) if last_modified else ""

        result.append(
            Hotspot(
                path=f.get("path", ""),
                changes=f.get("changes", 0),
                lastModified=last_modified_str,
                contributors=f.get("contributors", 0),
            )
        )

    return result


if __name__ == "__main__":
    import sys
    from datetime import date

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1-4: Activity levels
    validator.add_test("Activity HIGH", lambda: calculate_activity_level(35), ActivityLevel.HIGH)
    validator.add_test("Activity MEDIUM", lambda: calculate_activity_level(15), ActivityLevel.MEDIUM)
    validator.add_test("Activity LOW", lambda: calculate_activity_level(5), ActivityLevel.LOW)
    validator.add_test("Activity STALE", lambda: calculate_activity_level(0), ActivityLevel.STALE)

    # Test 5: Knowledge concentration
    validator.add_test(
        "Knowledge concentration",
        lambda: calculate_knowledge_concentration([{"author_email": "alice@test.com", "count": 75}], 100),
        75,
    )

    # Test 6: Top contributors
    def test_top_contributors():
        contributors = [
            {"author_email": "alice@test.com", "author_name": "Alice", "count": 50},
            {"author_email": "bob@test.com", "author_name": "Bob", "count": 30},
        ]
        result = calculate_top_contributors(contributors, 100, limit=2)
        return (len(result), result[0].name)

    validator.add_test("Top contributors", test_top_contributors, (2, "Alice"))

    # Test 7: Hotspots
    def test_hotspots():
        files = [
            {"path": "a.py", "changes": 50, "last_modified": date(2024, 1, 15), "contributors": 5},
            {"path": "b.py", "changes": 30, "last_modified": date(2024, 1, 10), "contributors": 3},
        ]
        result = calculate_hotspots(files, limit=2)
        return (len(result), result[0].path)

    validator.add_test("Hotspots", test_hotspots, (2, "a.py"))

    sys.exit(validator.run())
