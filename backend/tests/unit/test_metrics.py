"""
Unit tests for metrics calculation functions.

Tests the pure functions for calculating activity level, concentration,
top contributors, and hotspots from commit data.

Following TDD: these tests are written FIRST and should FAIL until implementation.
"""

import pytest
from datetime import date


@pytest.mark.unit
def test_calculate_activity_level_high():
    """Test that high activity is returned for commits >= high threshold."""
    from nexus_api.services.metrics import calculate_activity_level
    from nexus_api.models.repository import ActivityLevel

    result = calculate_activity_level(commits_last_30_days=35)
    assert result == ActivityLevel.HIGH


@pytest.mark.unit
def test_calculate_activity_level_medium():
    """Test that medium activity is returned for commits between medium and high."""
    from nexus_api.services.metrics import calculate_activity_level
    from nexus_api.models.repository import ActivityLevel

    result = calculate_activity_level(commits_last_30_days=15)
    assert result == ActivityLevel.MEDIUM


@pytest.mark.unit
def test_calculate_activity_level_low():
    """Test that low activity is returned for commits between low and medium."""
    from nexus_api.services.metrics import calculate_activity_level
    from nexus_api.models.repository import ActivityLevel

    result = calculate_activity_level(commits_last_30_days=5)
    assert result == ActivityLevel.LOW


@pytest.mark.unit
def test_calculate_activity_level_stale():
    """Test that stale is returned for commits below low threshold."""
    from nexus_api.services.metrics import calculate_activity_level
    from nexus_api.models.repository import ActivityLevel

    result = calculate_activity_level(commits_last_30_days=0)
    assert result == ActivityLevel.STALE


@pytest.mark.unit
def test_calculate_knowledge_concentration():
    """Test knowledge concentration calculation."""
    from nexus_api.services.metrics import calculate_knowledge_concentration

    # Contributor with 75% of commits
    contributor_commits = [{"author_email": "alice@test.com", "count": 75}]
    total_commits = 100

    result = calculate_knowledge_concentration(contributor_commits, total_commits)
    assert result == 75


@pytest.mark.unit
def test_calculate_knowledge_concentration_multiple():
    """Test knowledge concentration with multiple contributors."""
    from nexus_api.services.metrics import calculate_knowledge_concentration

    contributor_commits = [
        {"author_email": "alice@test.com", "count": 50},
        {"author_email": "bob@test.com", "count": 30},
        {"author_email": "carol@test.com", "count": 20},
    ]
    total_commits = 100

    result = calculate_knowledge_concentration(contributor_commits, total_commits)
    assert result == 50  # Top contributor percentage


@pytest.mark.unit
def test_calculate_knowledge_concentration_zero_commits():
    """Test knowledge concentration returns 0 for no commits."""
    from nexus_api.services.metrics import calculate_knowledge_concentration

    result = calculate_knowledge_concentration([], 0)
    assert result == 0


@pytest.mark.unit
def test_calculate_top_contributors():
    """Test top contributors calculation."""
    from nexus_api.services.metrics import calculate_top_contributors

    commits = [
        {"author_email": "alice@test.com", "author_name": "Alice", "count": 50},
        {"author_email": "bob@test.com", "author_name": "Bob", "count": 30},
        {"author_email": "carol@test.com", "author_name": "Carol", "count": 20},
    ]
    total_commits = 100

    result = calculate_top_contributors(commits, total_commits, limit=3)

    assert len(result) == 3
    assert result[0].name == "Alice"
    assert result[0].commits == 50
    assert result[0].percentage == 50


@pytest.mark.unit
def test_calculate_top_contributors_limit():
    """Test that top contributors respects the limit."""
    from nexus_api.services.metrics import calculate_top_contributors

    commits = [
        {"author_email": "a@test.com", "author_name": "A", "count": 40},
        {"author_email": "b@test.com", "author_name": "B", "count": 30},
        {"author_email": "c@test.com", "author_name": "C", "count": 20},
        {"author_email": "d@test.com", "author_name": "D", "count": 10},
    ]
    total_commits = 100

    result = calculate_top_contributors(commits, total_commits, limit=2)

    assert len(result) == 2
    assert result[0].name == "A"
    assert result[1].name == "B"


@pytest.mark.unit
def test_calculate_hotspots():
    """Test hotspots calculation from file changes."""
    from nexus_api.services.metrics import calculate_hotspots

    file_changes = [
        {"path": "src/main.py", "changes": 50, "last_modified": date(2024, 1, 15), "contributors": 5},
        {"path": "src/utils.py", "changes": 30, "last_modified": date(2024, 1, 10), "contributors": 3},
        {"path": "tests/test.py", "changes": 20, "last_modified": date(2024, 1, 5), "contributors": 2},
    ]

    result = calculate_hotspots(file_changes, limit=3)

    assert len(result) == 3
    assert result[0].path == "src/main.py"
    assert result[0].changes == 50
    assert result[0].contributors == 5


@pytest.mark.unit
def test_calculate_hotspots_limit():
    """Test that hotspots respects the limit."""
    from nexus_api.services.metrics import calculate_hotspots

    file_changes = [
        {"path": "a.py", "changes": 50, "last_modified": date(2024, 1, 15), "contributors": 5},
        {"path": "b.py", "changes": 40, "last_modified": date(2024, 1, 14), "contributors": 4},
        {"path": "c.py", "changes": 30, "last_modified": date(2024, 1, 13), "contributors": 3},
        {"path": "d.py", "changes": 20, "last_modified": date(2024, 1, 12), "contributors": 2},
    ]

    result = calculate_hotspots(file_changes, limit=2)

    assert len(result) == 2
    assert result[0].path == "a.py"
    assert result[1].path == "b.py"
