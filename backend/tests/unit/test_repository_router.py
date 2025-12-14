"""
Unit tests for Repository router with database integration.

Tests router endpoints using repository_service with real database session.
TDD: These tests must FAIL before implementation.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.tables import CommitTable, RepositoryTable
from nexus_api.services import repository_service
from nexus_api.config import settings


@pytest.mark.unit
@pytest.mark.skipif(
    settings.use_mock_data,
    reason="These tests verify real database logic, skipped when USE_MOCK_DATA=true"
)
class TestRepositoryServiceIntegration:
    """Tests for repository_service integration with database."""

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
    async def sample_commits(
        self, db_session: AsyncSession, sample_repo: RepositoryTable
    ) -> list[CommitTable]:
        """Create sample commits for testing."""
        commits = []
        for i in range(5):
            commit = CommitTable(
                id=f"commit-{i:040d}",
                repository_id=sample_repo.id,
                author_name="Alice",
                author_email="alice@test.com",
                committer_name="Alice",
                committer_email="alice@test.com",
                author_date=datetime(2024, 1, 15, 10, i, tzinfo=timezone.utc),
                commit_date=datetime(2024, 1, 15, 10, i, tzinfo=timezone.utc),
                message=f"Commit {i}",
                files_changed=[{"path": f"src/file{i}.py", "additions": 10, "deletions": 5}],
                additions=10,
                deletions=5,
            )
            db_session.add(commit)
            commits.append(commit)
        await db_session.commit()
        return commits

    @pytest.mark.asyncio
    async def test_get_all_repositories_returns_list(
        self, db_session: AsyncSession, sample_repo: RepositoryTable
    ) -> None:
        """Test get_all_repositories returns list of Repository models."""
        repos = await repository_service.get_all_repositories(db_session)
        assert isinstance(repos, list)
        assert len(repos) == 1
        assert repos[0].id == "test-repo-1"
        assert repos[0].name == "test-service"

    @pytest.mark.asyncio
    async def test_get_all_repositories_empty_database(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_all_repositories returns empty list when no repos exist."""
        repos = await repository_service.get_all_repositories(db_session)
        assert repos == []

    @pytest.mark.asyncio
    async def test_get_repository_by_id_found(
        self, db_session: AsyncSession, sample_repo: RepositoryTable
    ) -> None:
        """Test get_repository_by_id returns repository when found."""
        repo = await repository_service.get_repository_by_id(db_session, "test-repo-1")
        assert repo is not None
        assert repo.id == "test-repo-1"
        assert repo.name == "test-service"

    @pytest.mark.asyncio
    async def test_get_repository_by_id_not_found(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_repository_by_id returns None when not found."""
        repo = await repository_service.get_repository_by_id(db_session, "nonexistent")
        assert repo is None

    @pytest.mark.asyncio
    async def test_repository_has_calculated_metrics(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_commits: list[CommitTable],
    ) -> None:
        """Test repository has calculated metrics from commits."""
        repo = await repository_service.get_repository_by_id(db_session, "test-repo-1")
        assert repo is not None

        # Should have calculated fields
        assert repo.totalCommits == 5
        assert repo.contributors == 1  # Only Alice
        assert repo.knowledgeConcentration == 100  # Single contributor

        # Should have top contributors
        assert len(repo.topContributors) >= 1
        assert repo.topContributors[0].name == "Alice"
        assert repo.topContributors[0].commits == 5
        assert repo.topContributors[0].percentage == 100

    @pytest.mark.asyncio
    async def test_repository_has_hotspots(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_commits: list[CommitTable],
    ) -> None:
        """Test repository has calculated hotspots from file changes."""
        repo = await repository_service.get_repository_by_id(db_session, "test-repo-1")
        assert repo is not None

        # Should have hotspots (each commit changes a different file)
        assert len(repo.hotspots) == 5  # 5 unique files

    @pytest.mark.asyncio
    async def test_repository_activity_level_stale(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
    ) -> None:
        """Test repository with no recent commits has stale activity."""
        repo = await repository_service.get_repository_by_id(db_session, "test-repo-1")
        assert repo is not None
        assert repo.activity == "stale"  # No commits in last 30 days

    @pytest.mark.asyncio
    async def test_repository_serializes_correctly(
        self,
        db_session: AsyncSession,
        sample_repo: RepositoryTable,
        sample_commits: list[CommitTable],
    ) -> None:
        """Test repository serializes to dict with camelCase fields."""
        repo = await repository_service.get_repository_by_id(db_session, "test-repo-1")
        assert repo is not None

        data = repo.model_dump()
        assert "id" in data
        assert "name" in data
        assert "totalCommits" in data
        assert "knowledgeConcentration" in data
        assert "topContributors" in data
        assert "hotspots" in data
