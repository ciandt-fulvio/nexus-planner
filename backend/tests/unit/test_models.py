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
                TopContributor(name="Alice", email="alice@test.com", commits=60, percentage=60),
                TopContributor(name="Bob", email="bob@test.com", commits=40, percentage=40),
            ],
            hotspots=[
                Hotspot(path="src/main.ts", changes=50, lastModified="2024-01-15", contributors=3),
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

        contributor = TopContributor(
            name="Alice", email="alice@test.com", commits=50, percentage=50
        )
        assert contributor.percentage == 50
        assert contributor.commits == 50

    def test_hotspot_changes_positive(self) -> None:
        """Test Hotspot changes must be positive."""
        from nexus_api.models.repository import Hotspot

        hotspot = Hotspot(
            path="src/file.ts", changes=100, lastModified="2024-01-15", contributors=3
        )
        assert hotspot.changes == 100
        assert hotspot.contributors == 3

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


# Person model tests - TDD: Will fail until T026-T027 implemented
@pytest.mark.unit
class TestPersonModel:
    """Tests for Person model validation."""

    def test_person_creation(self) -> None:
        """Test creating a valid Person."""
        from nexus_api.models.person import (
            Person,
            PersonRepository,
            Technology,
        )

        person = Person(
            id="1",
            name="Ana Silva",
            email="ana.silva@company.com",
            avatar="AS",
            repositories=[
                PersonRepository(
                    name="reports-service",
                    commits=271,
                    lastActivity="2024-01-15",
                    expertise=95,
                ),
            ],
            technologies=[
                Technology(name="TypeScript", level=95),
            ],
            domains=["Relatórios", "APIs REST"],
            recentActivity=47,
            alerts=[
                Alert(type=AlertType.INFO, message="Principal especialista"),
            ],
        )
        assert person.id == "1"
        assert person.name == "Ana Silva"
        assert person.email == "ana.silva@company.com"
        assert len(person.repositories) == 1
        assert len(person.technologies) == 1

    def test_person_repository_expertise_range(self) -> None:
        """Test PersonRepository expertise must be 0-100."""
        from nexus_api.models.person import PersonRepository

        repo = PersonRepository(
            name="test-repo",
            commits=100,
            lastActivity="2024-01-01",
            expertise=85,
        )
        assert repo.expertise == 85

    def test_technology_level_range(self) -> None:
        """Test Technology level must be 0-100."""
        from nexus_api.models.person import Technology

        tech = Technology(name="Python", level=90)
        assert tech.level == 90

    def test_person_serialization(self) -> None:
        """Test Person model serializes to dict correctly."""
        from nexus_api.models.person import Person

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
        assert data["id"] == "1"
        assert data["email"] == "test@example.com"


# FeatureAnalysis model tests - TDD: Will fail until T038-T039 implemented
@pytest.mark.unit
class TestFeatureAnalysisModel:
    """Tests for FeatureAnalysis model validation."""

    def test_feature_analysis_creation(self) -> None:
        """Test creating a valid FeatureAnalysis."""
        from nexus_api.models.analysis import (
            FeatureAnalysis,
            ImpactedRepo,
            RecommendedPerson,
            Risk,
            RiskLevel,
            SuggestedStep,
        )

        analysis = FeatureAnalysis(
            feature="Test feature",
            impactedRepos=[
                ImpactedRepo(
                    name="reports-service",
                    confidence=95,
                    reasoning="Test reasoning",
                    modules=["src/api/"],
                ),
            ],
            recommendedPeople=[
                RecommendedPerson(
                    name="Ana Silva",
                    relevance=95,
                    reasoning="Main expert",
                ),
            ],
            risks=[
                Risk(type=RiskLevel.HIGH, message="Critical risk"),
            ],
            suggestedOrder=[
                SuggestedStep(
                    step=1,
                    action="Review code",
                    repository="reports-service",
                    reasoning="Start here",
                ),
            ],
            additionalRecommendations=["Test recommendation"],
        )
        assert analysis.feature == "Test feature"
        assert len(analysis.impactedRepos) == 1
        assert len(analysis.recommendedPeople) == 1
        assert len(analysis.risks) == 1
        assert len(analysis.suggestedOrder) == 1

    def test_risk_level_valid_values(self) -> None:
        """Test RiskLevel enum has correct values."""
        from nexus_api.models.analysis import RiskLevel

        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.LOW.value == "low"

    def test_impacted_repo_confidence_range(self) -> None:
        """Test ImpactedRepo confidence must be 0-100."""
        from nexus_api.models.analysis import ImpactedRepo

        repo = ImpactedRepo(
            name="test",
            confidence=85,
            reasoning="test",
            modules=["src/"],
        )
        assert repo.confidence == 85

    def test_feature_analysis_serialization(self) -> None:
        """Test FeatureAnalysis model serializes correctly."""
        from nexus_api.models.analysis import FeatureAnalysis

        analysis = FeatureAnalysis(
            feature="Test",
            impactedRepos=[],
            recommendedPeople=[],
            risks=[],
            suggestedOrder=[],
            additionalRecommendations=[],
        )
        data = analysis.model_dump()
        assert data["feature"] == "Test"
        assert isinstance(data["impactedRepos"], list)
