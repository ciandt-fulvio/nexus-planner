"""
Unit tests for Person service with database integration.

Tests person_service functions with real database session.
TDD: These tests must FAIL before implementation.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable
from nexus_api.config import settings


@pytest.mark.unit
@pytest.mark.skipif(
    settings.use_mock_data,
    reason="These tests verify real database logic, skipped when USE_MOCK_DATA=true"
)
class TestPersonServiceIntegration:
    """Tests for person_service integration with database."""

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
    async def sample_commits_recent(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_person: PersonTable,
    ) -> list[CommitTable]:
        """Create sample commits in last 30 days for testing."""
        commits = []
        now = datetime.now(timezone.utc)
        for i in range(5):
            commit = CommitTable(
                id=f"commit-recent-{i:038d}",
                repository_id=sample_repo.id,
                author_name=sample_person.name,
                author_email=sample_person.email,
                committer_name=sample_person.name,
                committer_email=sample_person.email,
                author_date=now - timedelta(days=i),
                commit_date=now - timedelta(days=i),
                message=f"Recent commit {i}",
                files_changed=[{"path": f"src/file{i}.py", "additions": 10, "deletions": 5}],
                additions=10,
                deletions=5,
            )
            db_session.add(commit)
            commits.append(commit)
        await db_session.commit()
        return commits

    @pytest.mark.asyncio
    async def test_get_all_people_returns_list(
        self,
        db_session: AsyncSession,
        sample_person: PersonTable,
        sample_repo: RepositoryTable,
        sample_commits_recent: list[CommitTable],
    ) -> None:
        """Test get_all_people returns list of Person models."""
        from nexus_api.services import person_service

        people = await person_service.get_all_people(db_session)
        assert isinstance(people, list)
        assert len(people) == 1
        assert people[0].id == "test-person-1"
        assert people[0].name == "Alice Developer"

    @pytest.mark.asyncio
    async def test_get_all_people_empty_database(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_all_people returns empty list when no people exist."""
        from nexus_api.services import person_service

        people = await person_service.get_all_people(db_session)
        assert people == []

    @pytest.mark.asyncio
    async def test_get_person_by_id_found(
        self,
        db_session: AsyncSession,
        sample_person: PersonTable,
        sample_repo: RepositoryTable,
        sample_commits_recent: list[CommitTable],
    ) -> None:
        """Test get_person_by_id returns person when found."""
        from nexus_api.services import person_service

        person = await person_service.get_person_by_id(db_session, "test-person-1")
        assert person is not None
        assert person.id == "test-person-1"
        assert person.name == "Alice Developer"

    @pytest.mark.asyncio
    async def test_get_person_by_id_not_found(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_person_by_id returns None when not found."""
        from nexus_api.services import person_service

        person = await person_service.get_person_by_id(db_session, "nonexistent")
        assert person is None

    @pytest.mark.asyncio
    async def test_person_has_calculated_metrics(
        self,
        db_session: AsyncSession,
        sample_person: PersonTable,
        sample_repo: RepositoryTable,
        sample_commits_recent: list[CommitTable],
    ) -> None:
        """Test person has calculated metrics from commits."""
        from nexus_api.services import person_service

        person = await person_service.get_person_by_id(db_session, "test-person-1")
        assert person is not None

        # Should have recent activity (5 commits in last 30 days)
        assert person.recentActivity == 5

        # Should have repositories
        assert len(person.repositories) == 1
        assert person.repositories[0].name == "test-service"
        assert person.repositories[0].commits == 5

    @pytest.mark.asyncio
    async def test_person_has_avatar_initials(
        self,
        db_session: AsyncSession,
        sample_person: PersonTable,
        sample_repo: RepositoryTable,
        sample_commits_recent: list[CommitTable],
    ) -> None:
        """Test person has avatar initials from database."""
        from nexus_api.services import person_service

        person = await person_service.get_person_by_id(db_session, "test-person-1")
        assert person is not None
        assert person.avatar == "AD"

    @pytest.mark.asyncio
    async def test_person_serializes_correctly(
        self,
        db_session: AsyncSession,
        sample_person: PersonTable,
        sample_repo: RepositoryTable,
        sample_commits_recent: list[CommitTable],
    ) -> None:
        """Test person serializes to dict with camelCase fields."""
        from nexus_api.services import person_service

        person = await person_service.get_person_by_id(db_session, "test-person-1")
        assert person is not None

        data = person.model_dump()
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "avatar" in data
        assert "repositories" in data
        assert "recentActivity" in data
