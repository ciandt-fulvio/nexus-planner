"""
Unit tests for Pydantic models.

Tests model validation, serialization, and edge cases.
TDD: These tests must FAIL before implementation.
"""

import pytest

from nexus_api.models import Alert, AlertType


class TestAlertModel:
    """Tests for Alert and AlertType models."""

    def test_alert_creation_with_enum(self) -> None:
        """Test creating Alert with AlertType enum."""
        alert = Alert(type=AlertType.WARNING, message="Test warning")
        assert alert.type == AlertType.WARNING
        assert alert.message == "Test warning"

    def test_alert_creation_with_string(self) -> None:
        """Test creating Alert with string type value."""
        alert = Alert(type="danger", message="Critical issue")
        assert alert.type == AlertType.DANGER

    def test_alert_invalid_type_rejected(self) -> None:
        """Test that invalid alert type is rejected."""
        with pytest.raises(ValueError):
            Alert(type="invalid", message="Test")

    def test_alert_extra_fields_rejected(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(ValueError):
            Alert(type="warning", message="Test", extra_field="should fail")


# Repository model tests - TDD: Will fail until T015-T016 implemented
@pytest.mark.unit
class TestRepositoryModel:
    """Tests for Repository model validation."""

    def test_repository_creation(self) -> None:
        """Test creating a valid Repository."""
        from nexus_api.models.repository import (
            ActivityLevel,
            Hotspot,
            Repository,
            TopContributor,
        )

        repo = Repository(
            id="1",
            name="test-repo",
            description="A test repository",
            lastCommit="2024-01-15",
            totalCommits=100,
            contributors=5,
            activity=ActivityLevel.HIGH,
            knowledgeConcentration=45,
            topContributors=[
                TopContributor(name="Alice", percentage=60),
                TopContributor(name="Bob", percentage=40),
            ],
            hotspots=[
                Hotspot(path="src/main.ts", changes=50),
            ],
            dependencies=["other-repo"],
            alerts=[
                Alert(type=AlertType.INFO, message="Test info"),
            ],
        )
        assert repo.id == "1"
        assert repo.name == "test-repo"
        assert repo.activity == ActivityLevel.HIGH
        assert len(repo.topContributors) == 2
        assert len(repo.hotspots) == 1
        assert len(repo.alerts) == 1

    def test_repository_activity_from_string(self) -> None:
        """Test creating Repository with string activity value."""
        from nexus_api.models.repository import ActivityLevel, Repository

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
        assert repo.activity == ActivityLevel.MEDIUM

    def test_repository_knowledge_concentration_valid_range(self) -> None:
        """Test knowledgeConcentration must be 0-100."""
        from nexus_api.models.repository import Repository

        # Valid value
        repo = Repository(
            id="1",
            name="test",
            description="Test",
            lastCommit="2024-01-01",
            totalCommits=10,
            contributors=1,
            activity="low",
            knowledgeConcentration=75,
            topContributors=[],
            hotspots=[],
            dependencies=[],
            alerts=[],
        )
        assert repo.knowledgeConcentration == 75

    def test_top_contributor_percentage_valid(self) -> None:
        """Test TopContributor percentage must be 0-100."""
        from nexus_api.models.repository import TopContributor

        contributor = TopContributor(name="Alice", percentage=50)
        assert contributor.percentage == 50

    def test_hotspot_changes_positive(self) -> None:
        """Test Hotspot changes must be positive."""
        from nexus_api.models.repository import Hotspot

        hotspot = Hotspot(path="src/file.ts", changes=100)
        assert hotspot.changes == 100

    def test_repository_serialization(self) -> None:
        """Test Repository model serializes to dict correctly."""
        from nexus_api.models.repository import Repository

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
        assert data["id"] == "1"
        assert data["activity"] == "stale"
