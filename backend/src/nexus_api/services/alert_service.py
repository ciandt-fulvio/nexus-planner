"""
Alert service for generating AI-like alerts based on repository and person metrics.

Provides async functions for generating alerts based on calculated metrics.
Alerts are generated for:
- High knowledge concentration (bus factor risk)
- Stale repositories (no recent activity)
- High contributor expertise (informational)

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Repository or Person ID
Expected output: List of Alert Pydantic models
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings
from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable
from nexus_api.models import Alert, AlertType


async def generate_alerts_for_repository(
    db: AsyncSession,
    repository_id: str,
) -> list[Alert]:
    """
    Generate alerts for a repository based on its metrics.

    Args:
        db: Async database session
        repository_id: UUID of the repository

    Returns:
        List of Alert models based on repository metrics
    """
    alerts: list[Alert] = []

    # Check if repository exists
    repo_stmt = select(RepositoryTable).where(RepositoryTable.id == repository_id)
    repo_result = await db.execute(repo_stmt)
    repo = repo_result.scalar_one_or_none()

    if repo is None:
        return alerts

    # Get commit counts in sliding window
    commits_stmt = (
        select(CommitTable)
        .where(CommitTable.repository_id == repository_id)
        .order_by(CommitTable.commit_date.desc())
        .limit(settings.window_size)
    )
    commits_result = await db.execute(commits_stmt)
    commits = commits_result.scalars().all()

    total_commits = len(commits)
    if total_commits == 0:
        alerts.append(
            Alert(
                type=AlertType.WARNING,
                message="Repositório sem commits sincronizados",
            )
        )
        return alerts

    # Check for stale repository (no commits in last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_commits = []
    for c in commits:
        if c.commit_date:
            # Handle both naive and aware datetimes
            commit_dt = c.commit_date
            if commit_dt.tzinfo is None:
                commit_dt = commit_dt.replace(tzinfo=timezone.utc)
            if commit_dt >= thirty_days_ago:
                recent_commits.append(c)

    if len(recent_commits) == 0:
        alerts.append(
            Alert(
                type=AlertType.WARNING,
                message="Repositório inativo há mais de 30 dias",
            )
        )

    # Check for knowledge concentration
    contributor_counts: dict[str, int] = {}
    for commit in commits:
        email = commit.author_email
        contributor_counts[email] = contributor_counts.get(email, 0) + 1

    if contributor_counts:
        top_contributor_email = max(contributor_counts, key=contributor_counts.get)
        top_contributor_count = contributor_counts[top_contributor_email]
        concentration = int((top_contributor_count / total_commits) * 100)

        if concentration >= settings.concentration_critical_threshold:
            # Get contributor name
            name_stmt = (
                select(CommitTable.author_name)
                .where(CommitTable.author_email == top_contributor_email)
                .limit(1)
            )
            name_result = await db.execute(name_stmt)
            contributor_name = name_result.scalar() or top_contributor_email

            alerts.append(
                Alert(
                    type=AlertType.DANGER,
                    message=f"Concentração crítica: {contributor_name} é responsável por {concentration}% dos commits",
                )
            )
        elif concentration >= settings.concentration_warning_threshold:
            name_stmt = (
                select(CommitTable.author_name)
                .where(CommitTable.author_email == top_contributor_email)
                .limit(1)
            )
            name_result = await db.execute(name_stmt)
            contributor_name = name_result.scalar() or top_contributor_email

            alerts.append(
                Alert(
                    type=AlertType.WARNING,
                    message=f"Concentração de conhecimento: {contributor_name} possui {concentration}% dos commits",
                )
            )

    return alerts


async def generate_alerts_for_person(
    db: AsyncSession,
    person_id: str,
) -> list[Alert]:
    """
    Generate alerts for a person based on their metrics.

    Args:
        db: Async database session
        person_id: UUID of the person

    Returns:
        List of Alert models based on person metrics
    """
    alerts: list[Alert] = []

    # Check if person exists
    person_stmt = select(PersonTable).where(PersonTable.id == person_id)
    person_result = await db.execute(person_stmt)
    person = person_result.scalar_one_or_none()

    if person is None:
        return alerts

    # Get repositories where this person is top contributor
    # Subquery to get all commits by this person
    person_commits_stmt = (
        select(
            CommitTable.repository_id,
            func.count(CommitTable.id).label("person_count"),
        )
        .where(CommitTable.author_email == person.email)
        .group_by(CommitTable.repository_id)
    )
    person_commits_result = await db.execute(person_commits_stmt)
    person_repo_counts = {row.repository_id: row.person_count for row in person_commits_result.all()}

    # Check each repository for expertise
    expert_repos: list[str] = []
    for repo_id, person_count in person_repo_counts.items():
        # Get total commits for this repo
        total_stmt = (
            select(func.count())
            .select_from(CommitTable)
            .where(CommitTable.repository_id == repo_id)
        )
        total_result = await db.execute(total_stmt)
        total_count = total_result.scalar() or 1

        expertise = int((person_count / total_count) * 100)
        if expertise >= settings.concentration_critical_threshold:
            # Get repo name
            repo_stmt = select(RepositoryTable.name).where(RepositoryTable.id == repo_id)
            repo_result = await db.execute(repo_stmt)
            repo_name = repo_result.scalar() or repo_id
            expert_repos.append(repo_name)

    if expert_repos:
        if len(expert_repos) == 1:
            alerts.append(
                Alert(
                    type=AlertType.INFO,
                    message=f"Principal especialista em {expert_repos[0]}",
                )
            )
        else:
            alerts.append(
                Alert(
                    type=AlertType.INFO,
                    message=f"Principal especialista em {len(expert_repos)} repositórios",
                )
            )

    # Check for recent activity
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_stmt = (
        select(func.count())
        .select_from(CommitTable)
        .where(CommitTable.author_email == person.email)
        .where(CommitTable.commit_date >= thirty_days_ago)
    )
    recent_result = await db.execute(recent_stmt)
    recent_commits = recent_result.scalar() or 0

    if recent_commits == 0 and person_repo_counts:
        alerts.append(
            Alert(
                type=AlertType.WARNING,
                message="Inativo há mais de 30 dias",
            )
        )

    return alerts


if __name__ == "__main__":
    print("✅ alert_service module loaded successfully")
