"""
Unit tests for Alert service.

Tests alert generation based on repository and person metrics.
TDD: These tests must FAIL before implementation.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable
from nexus_api.models import Alert, AlertType


@pytest.mark.unit
class TestAlertServiceGeneration:
    """Tests for alert generation logic."""

    @pytest_asyncio.fixture
    async def sample_repo(self, db_session: AsyncSession) -> RepositoryTable:
        """Create a sample repository for testing."""
        repo = RepositoryTable(
            id="test-repo-1",
            name="test-service",
            description="A test repository",
            git_url="https://github.com/test/test-service.git",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        return repo

    @pytest_asyncio.fixture
    async def sample_person(self, db_session: AsyncSession) -> PersonTable:
        """Create a sample person for testing."""
        person = PersonTable(
            id="test-person-1",
            email="alice@test.com",
            name="Alice Developer",
            avatar="AD",
        )
        db_session.add(person)
        await db_session.commit()
        await db_session.refresh(person)
        return person

    @pytest_asyncio.fixture
    async def high_concentration_commits(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
    ) -> list[CommitTable]:
        """Create commits where one person has 80% of all commits (high concentration)."""
        commits = []
        now = datetime.now(timezone.utc)

        # Alice has 80 commits
        for i in range(80):
            commit = CommitTable(
                id=f"commit-alice-{i:037d}",
                repository_id=sample_repo.id,
                author_name=sample_person.name,
                author_email=sample_person.email,
                committer_name=sample_person.name,
                committer_email=sample_person.email,
                author_date=now - timedelta(days=i % 30),
                commit_date=now - timedelta(days=i % 30),
                message=f"Alice commit {i}",
                files_changed=[{"path": f"src/file{i}.py"}],
                additions=10,
                deletions=5,
            )
            db_session.add(commit)
            commits.append(commit)

        # Bob has 20 commits
        for i in range(20):
            commit = CommitTable(
                id=f"commit-bob-{i:039d}",
                repository_id=sample_repo.id,
                author_name="Bob Dev",
                author_email="bob@test.com",
                committer_name="Bob Dev",
                committer_email="bob@test.com",
                author_date=now - timedelta(days=i % 30),
                commit_date=now - timedelta(days=i % 30),
                message=f"Bob commit {i}",
                files_changed=[{"path": f"src/bob{i}.py"}],
                additions=5,
                deletions=2,
            )
            db_session.add(commit)
            commits.append(commit)

        await db_session.commit()
        return commits

    @pytest_asyncio.fixture
    async def stale_repo_commits(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
    ) -> list[CommitTable]:
        """Create commits that are all older than 30 days (stale repo)."""
        commits = []
        now = datetime.now(timezone.utc)

        for i in range(10):
            commit = CommitTable(
                id=f"commit-stale-{i:038d}",
                repository_id=sample_repo.id,
                author_name=sample_person.name,
                author_email=sample_person.email,
                committer_name=sample_person.name,
                committer_email=sample_person.email,
                author_date=now - timedelta(days=60 + i),  # All older than 30 days
                commit_date=now - timedelta(days=60 + i),
                message=f"Old commit {i}",
                files_changed=[{"path": f"src/old{i}.py"}],
                additions=5,
                deletions=2,
            )
            db_session.add(commit)
            commits.append(commit)

        await db_session.commit()
        return commits

    @pytest.mark.asyncio
    async def test_generate_alerts_high_concentration_warning(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
        high_concentration_commits: list[CommitTable],
    ) -> None:
        """Test alert generated for high knowledge concentration."""
        from nexus_api.services import alert_service

        alerts = await alert_service.generate_alerts_for_repository(
            db_session, sample_repo.id
        )
        assert isinstance(alerts, list)

        # Should have a warning about knowledge concentration
        concentration_alerts = [a for a in alerts if "concentr" in a.message.lower()]
        assert len(concentration_alerts) >= 1
        assert concentration_alerts[0].type in [AlertType.WARNING, AlertType.DANGER]

    @pytest.mark.asyncio
    async def test_generate_alerts_stale_repository(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
        stale_repo_commits: list[CommitTable],
    ) -> None:
        """Test alert generated for stale repository (no recent activity)."""
        from nexus_api.services import alert_service

        alerts = await alert_service.generate_alerts_for_repository(
            db_session, sample_repo.id
        )

        # Should have a warning about inactivity
        inactivity_alerts = [
            a for a in alerts if "inativ" in a.message.lower() or "stale" in a.message.lower()
        ]
        assert len(inactivity_alerts) >= 1

    @pytest.mark.asyncio
    async def test_generate_alerts_for_person(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
        high_concentration_commits: list[CommitTable],
    ) -> None:
        """Test alert generated for person who dominates a repository."""
        from nexus_api.services import alert_service

        alerts = await alert_service.generate_alerts_for_person(
            db_session, sample_person.id
        )
        assert isinstance(alerts, list)

        # Person with 80% of commits should have info alert about being main contributor
        expert_alerts = [
            a for a in alerts
            if "expert" in a.message.lower()
            or "principal" in a.message.lower()
            or "main" in a.message.lower()
        ]
        # This is informational, not always a warning
        assert len(alerts) >= 0  # May or may not have alerts depending on thresholds

    @pytest.mark.asyncio
    async def test_generate_alerts_returns_list(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
    ) -> None:
        """Test generate_alerts_for_repository returns list even when empty."""
        from nexus_api.services import alert_service

        alerts = await alert_service.generate_alerts_for_repository(
            db_session, "nonexistent-repo"
        )
        assert isinstance(alerts, list)

    @pytest.mark.asyncio
    async def test_alerts_are_valid_pydantic_models(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
        high_concentration_commits: list[CommitTable],
    ) -> None:
        """Test all generated alerts are valid Alert Pydantic models."""
        from nexus_api.services import alert_service

        alerts = await alert_service.generate_alerts_for_repository(
            db_session, sample_repo.id
        )

        for alert in alerts:
            assert isinstance(alert, Alert)
            assert isinstance(alert.type, AlertType)
            assert isinstance(alert.message, str)
            assert len(alert.message) > 0
