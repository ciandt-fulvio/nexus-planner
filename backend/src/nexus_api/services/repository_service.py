"""
Repository service for querying repositories with calculated metrics.

Provides async functions for getting repositories with all calculated fields.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Repository ID or no filter
Expected output: Repository Pydantic models with calculated metrics
"""

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings
from nexus_api.data import mock_data
from nexus_api.db.tables import CommitTable, RepositoryTable
from nexus_api.models.repository import ActivityLevel, Hotspot, Repository, TopContributor
from nexus_api.services import commit_service
from nexus_api.services import alert_service
from nexus_api.services.metrics import (
    calculate_activity_level,
    calculate_hotspots,
    calculate_knowledge_concentration,
    calculate_top_contributors,
)


async def _build_repository_model(
    db: AsyncSession,
    repo: RepositoryTable,
) -> Repository:
    """
    Build a Repository model with all calculated fields.

    Args:
        db: Async database session
        repo: RepositoryTable instance

    Returns:
        Repository Pydantic model with calculated metrics
    """
    # Get commits in window
    commits = await commit_service.get_commits_by_repository(
        db, repo.id, limit=settings.window_size
    )
    total_commits = len(commits)

    # Get last commit date
    last_commit_date = None
    if commits:
        last_commit_date = commits[0].commit_date.date() if commits[0].commit_date else None

    # Get commits last 30 days for activity
    commits_last_30_days = await commit_service.get_commits_last_30_days(db, repo.id)

    # Get contributor stats
    contributor_stats = await commit_service.get_contributor_stats(
        db, repo.id, limit=settings.window_size
    )

    # Get file change stats
    file_stats = await commit_service.get_file_change_stats(
        db, repo.id, limit=settings.window_size
    )

    # Calculate metrics
    activity = calculate_activity_level(commits_last_30_days)
    knowledge_concentration = calculate_knowledge_concentration(contributor_stats, total_commits)
    top_contributors = calculate_top_contributors(
        contributor_stats, total_commits, limit=settings.top_contributors_limit
    )
    hotspots = calculate_hotspots(file_stats, limit=settings.top_hotspots_limit)

    # Count unique contributors
    unique_contributors = len(contributor_stats)

    # Generate alerts for this repository
    alerts = await alert_service.generate_alerts_for_repository(db, repo.id)

    return Repository(
        id=repo.id,
        name=repo.name,
        description=repo.description or "",
        lastCommit=last_commit_date.isoformat() if last_commit_date else "",
        totalCommits=total_commits,
        contributors=unique_contributors,
        activity=activity,
        knowledgeConcentration=knowledge_concentration,
        topContributors=top_contributors,
        hotspots=hotspots,
        dependencies=[],  # TODO: Implement dependency detection
        alerts=alerts,
    )


async def get_all_repositories(db: AsyncSession) -> list[Repository]:
    """
    Get all repositories with calculated metrics.

    Returns mock data if USE_MOCK_DATA is true, otherwise queries database.

    Args:
        db: Async database session

    Returns:
        List of Repository models with calculated metrics
    """
    if settings.use_mock_data:
        return mock_data.get_all_repositories()

    stmt = select(RepositoryTable).order_by(RepositoryTable.name)
    result = await db.execute(stmt)
    repos = result.scalars().all()

    return [await _build_repository_model(db, repo) for repo in repos]


async def get_repository_by_id(
    db: AsyncSession,
    repository_id: str,
) -> Repository | None:
    """
    Get a repository by ID with calculated metrics.

    Returns mock data if USE_MOCK_DATA is true, otherwise queries database.

    Args:
        db: Async database session
        repository_id: UUID of the repository

    Returns:
        Repository model with calculated metrics, or None if not found
    """
    if settings.use_mock_data:
        return mock_data.get_repository_by_id(repository_id)

    stmt = select(RepositoryTable).where(RepositoryTable.id == repository_id)
    result = await db.execute(stmt)
    repo = result.scalar_one_or_none()

    if repo is None:
        return None

    return await _build_repository_model(db, repo)


if __name__ == "__main__":
    print("✅ repository_service module loaded successfully")
