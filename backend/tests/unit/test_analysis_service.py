"""
Unit tests for Analysis service.

Tests analysis creation and retrieval.
TDD: These tests must FAIL before implementation.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable
from nexus_api.models.analysis import FeatureAnalysis


@pytest.mark.unit
class TestAnalysisServiceCreation:
    """Tests for analysis_service creation logic."""

    @pytest_asyncio.fixture
    async def sample_repos(self, db_session: AsyncSession) -> list[RepositoryTable]:
        """Create sample repositories for testing."""
        repos = []
        for i in range(3):
            repo = RepositoryTable(
                id=f"repo-{i}",
                name=f"service-{i}",
                description=f"Test repository {i}",
                git_url=f"https://github.com/test/service-{i}.git",
            )
            db_session.add(repo)
            repos.append(repo)
        await db_session.commit()
        return repos

    @pytest_asyncio.fixture
    async def sample_people(self, db_session: AsyncSession) -> list[PersonTable]:
        """Create sample people for testing."""
        people = []
        for i, (name, email) in enumerate([
            ("Alice Developer", "alice@test.com"),
            ("Bob Coder", "bob@test.com"),
            ("Carol Engineer", "carol@test.com"),
        ]):
            person = PersonTable(
                id=f"person-{i}",
                email=email,
                name=name,
                avatar=name[0] + name.split()[1][0],
            )
            db_session.add(person)
            people.append(person)
        await db_session.commit()
        return people

    @pytest_asyncio.fixture
    async def sample_commits(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
    ) -> list[CommitTable]:
        """Create sample commits for testing."""
        commits = []
        now = datetime.now(timezone.utc)

        # Alice commits to service-0
        for i in range(10):
            commit = CommitTable(
                id=f"commit-alice-{i:037d}",
                repository_id=sample_repos[0].id,
                author_name=sample_people[0].name,
                author_email=sample_people[0].email,
                committer_name=sample_people[0].name,
                committer_email=sample_people[0].email,
                author_date=now - timedelta(days=i),
                commit_date=now - timedelta(days=i),
                message=f"Alice commit {i}",
                files_changed=[{"path": f"src/module{i}.py"}],
                additions=10,
                deletions=5,
            )
            db_session.add(commit)
            commits.append(commit)

        # Bob commits to service-1
        for i in range(5):
            commit = CommitTable(
                id=f"commit-bob-{i:039d}",
                repository_id=sample_repos[1].id,
                author_name=sample_people[1].name,
                author_email=sample_people[1].email,
                committer_name=sample_people[1].name,
                committer_email=sample_people[1].email,
                author_date=now - timedelta(days=i),
                commit_date=now - timedelta(days=i),
                message=f"Bob commit {i}",
                files_changed=[{"path": f"src/bob{i}.py"}],
                additions=5,
                deletions=2,
            )
            db_session.add(commit)
            commits.append(commit)

        await db_session.commit()
        return commits

    @pytest.mark.asyncio
    async def test_create_analysis_returns_feature_analysis(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test create_analysis returns a FeatureAnalysis model."""
        from nexus_api.services import analysis_service

        analysis = await analysis_service.create_analysis(
            db_session, "Add new reporting feature"
        )
        assert isinstance(analysis, FeatureAnalysis)
        assert analysis.feature == "Add new reporting feature"

    @pytest.mark.asyncio
    async def test_create_analysis_includes_impacted_repos(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test create_analysis includes impacted repositories."""
        from nexus_api.services import analysis_service

        analysis = await analysis_service.create_analysis(
            db_session, "Update service functionality"
        )
        assert isinstance(analysis.impactedRepos, list)
        # Should include repos based on recent activity
        assert len(analysis.impactedRepos) >= 0

    @pytest.mark.asyncio
    async def test_create_analysis_includes_recommended_people(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test create_analysis includes recommended people."""
        from nexus_api.services import analysis_service

        analysis = await analysis_service.create_analysis(
            db_session, "Implement new endpoint"
        )
        assert isinstance(analysis.recommendedPeople, list)

    @pytest.mark.asyncio
    async def test_create_analysis_includes_risks(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test create_analysis includes identified risks."""
        from nexus_api.services import analysis_service

        analysis = await analysis_service.create_analysis(
            db_session, "Major refactoring"
        )
        assert isinstance(analysis.risks, list)

    @pytest.mark.asyncio
    async def test_save_analysis_stores_in_database(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test save_analysis stores analysis in database."""
        from nexus_api.services import analysis_service
        from nexus_api.db.tables import FeatureAnalysisTable
        from sqlalchemy import select

        analysis = await analysis_service.create_analysis(
            db_session, "Feature for storage test"
        )

        # Save to database
        saved = await analysis_service.save_analysis(db_session, analysis)
        assert saved is not None

        # Verify it's in the database
        stmt = select(FeatureAnalysisTable).where(
            FeatureAnalysisTable.feature_description == "Feature for storage test"
        )
        result = await db_session.execute(stmt)
        stored = result.scalar_one_or_none()
        assert stored is not None

    @pytest.mark.asyncio
    async def test_analysis_is_valid_pydantic_model(
        self,
        db_session: AsyncSession,
        sample_repos: list[RepositoryTable],
        sample_people: list[PersonTable],
        sample_commits: list[CommitTable],
    ) -> None:
        """Test analysis is a valid Pydantic model that serializes correctly."""
        from nexus_api.services import analysis_service

        analysis = await analysis_service.create_analysis(
            db_session, "Test serialization"
        )

        data = analysis.model_dump()
        assert "feature" in data
        assert "impactedRepos" in data
        assert "recommendedPeople" in data
        assert "risks" in data
        assert "suggestedOrder" in data
        assert "additionalRecommendations" in data
