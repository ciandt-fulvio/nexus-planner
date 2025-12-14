"""
Unit tests for service layer.

Tests commit_service and repository_service functions.
Following TDD: these tests are written FIRST and should FAIL until implementation.
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_commit_service_create(db_session: AsyncSession, sample_repository_id: str):
    """Test creating a commit via commit_service."""
    from nexus_api.services.commit_service import create_commit
    from nexus_api.db.tables import CommitTable

    commit_data = {
        "id": "a" * 40,
        "repository_id": sample_repository_id,
        "author_name": "Alice",
        "author_email": "alice@test.com",
        "committer_name": "Alice",
        "committer_email": "alice@test.com",
        "author_date": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "commit_date": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "message": "Initial commit",
        "files_changed": [{"path": "main.py", "status": "added"}],
        "additions": 100,
        "deletions": 0,
    }

    result = await create_commit(db_session, commit_data)

    assert result.id == "a" * 40
    assert result.author_name == "Alice"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_commit_service_get_by_repository(
    db_session: AsyncSession, sample_repository_id: str
):
    """Test getting commits by repository."""
    from nexus_api.services.commit_service import create_commit, get_commits_by_repository

    # Create test commits
    for i in range(5):
        commit_data = {
            "id": f"{'a' * 39}{i}",
            "repository_id": sample_repository_id,
            "author_name": "Alice",
            "author_email": "alice@test.com",
            "committer_name": "Alice",
            "committer_email": "alice@test.com",
            "author_date": datetime(2024, 1, 15, 10, i, 0, tzinfo=timezone.utc),
            "commit_date": datetime(2024, 1, 15, 10, i, 0, tzinfo=timezone.utc),
            "message": f"Commit {i}",
            "files_changed": [],
            "additions": 10,
            "deletions": 5,
        }
        await create_commit(db_session, commit_data)

    commits = await get_commits_by_repository(db_session, sample_repository_id, limit=3)

    assert len(commits) == 3


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.use_mock_data,
    reason="Tests real database logic, skipped when USE_MOCK_DATA=true"
)
async def test_repository_service_get_all(db_session: AsyncSession):
    """Test getting all repositories with calculated metrics."""
    from nexus_api.services.repository_service import get_all_repositories
    from nexus_api.db.tables import RepositoryTable

    # Create test repository
    repo = RepositoryTable(
        id=str(uuid.uuid4()),
        name="test-repo",
        git_url="https://github.com/test/repo.git",
    )
    db_session.add(repo)
    await db_session.commit()

    repositories = await get_all_repositories(db_session)

    assert len(repositories) >= 1
    assert any(r.name == "test-repo" for r in repositories)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.use_mock_data,
    reason="Tests real database logic, skipped when USE_MOCK_DATA=true"
)
async def test_repository_service_get_by_id(db_session: AsyncSession):
    """Test getting a repository by ID."""
    from nexus_api.services.repository_service import get_repository_by_id
    from nexus_api.db.tables import RepositoryTable

    repo_id = str(uuid.uuid4())
    repo = RepositoryTable(
        id=repo_id,
        name="test-repo",
        git_url="https://github.com/test/repo.git",
    )
    db_session.add(repo)
    await db_session.commit()

    result = await get_repository_by_id(db_session, repo_id)

    assert result is not None
    assert result.name == "test-repo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_repository_service_get_by_id_not_found(db_session: AsyncSession):
    """Test getting a non-existent repository returns None."""
    from nexus_api.services.repository_service import get_repository_by_id

    result = await get_repository_by_id(db_session, str(uuid.uuid4()))

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.use_mock_data,
    reason="Tests real database logic, skipped when USE_MOCK_DATA=true"
)
async def test_repository_service_includes_calculated_fields(db_session: AsyncSession):
    """Test that repository includes calculated fields."""
    from nexus_api.services.repository_service import get_repository_by_id
    from nexus_api.services.commit_service import create_commit
    from nexus_api.db.tables import RepositoryTable

    repo_id = str(uuid.uuid4())
    repo = RepositoryTable(
        id=repo_id,
        name="test-repo",
        git_url="https://github.com/test/repo.git",
    )
    db_session.add(repo)
    await db_session.commit()

    # Add some commits
    for i in range(10):
        commit_data = {
            "id": f"{'b' * 39}{i}",
            "repository_id": repo_id,
            "author_name": "Alice",
            "author_email": "alice@test.com",
            "committer_name": "Alice",
            "committer_email": "alice@test.com",
            "author_date": datetime(2024, 1, 15, 10, i, 0, tzinfo=timezone.utc),
            "commit_date": datetime(2024, 1, 15, 10, i, 0, tzinfo=timezone.utc),
            "message": f"Commit {i}",
            "files_changed": [{"path": "main.py", "status": "modified"}],
            "additions": 10,
            "deletions": 5,
        }
        await create_commit(db_session, commit_data)

    result = await get_repository_by_id(db_session, repo_id)

    assert result is not None
    assert result.totalCommits >= 10
    assert hasattr(result, "topContributors")
    assert hasattr(result, "hotspots")
    assert hasattr(result, "activity")
