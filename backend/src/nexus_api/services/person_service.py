"""
Person service for querying people with calculated metrics.

Provides async functions for getting people with all calculated fields.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Person ID or no filter
Expected output: Person Pydantic models with calculated metrics
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings
from nexus_api.data import mock_data
from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable
from nexus_api.models.person import Person, PersonRepository, Technology
from nexus_api.services import alert_service


async def _get_person_repositories(
    db: AsyncSession,
    person_email: str,
) -> list[PersonRepository]:
    """
    Get repository stats for a person.

    Args:
        db: Async database session
        person_email: Email of the person

    Returns:
        List of PersonRepository models with commit stats
    """
    # Get commits per repository for this person
    stmt = (
        select(
            RepositoryTable.name,
            func.count(CommitTable.id).label("commit_count"),
            func.max(CommitTable.commit_date).label("last_activity"),
        )
        .join(CommitTable, CommitTable.repository_id == RepositoryTable.id)
        .where(CommitTable.author_email == person_email)
        .group_by(RepositoryTable.id, RepositoryTable.name)
        .order_by(func.count(CommitTable.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    repositories = []
    for row in rows:
        # Calculate expertise as percentage of total commits in this repo
        total_commits_stmt = (
            select(func.count())
            .select_from(CommitTable)
            .join(RepositoryTable, CommitTable.repository_id == RepositoryTable.id)
            .where(RepositoryTable.name == row.name)
        )
        total_result = await db.execute(total_commits_stmt)
        total_commits = total_result.scalar() or 1

        expertise = int((row.commit_count / total_commits) * 100)

        last_activity = ""
        if row.last_activity:
            if hasattr(row.last_activity, "date"):
                last_activity = row.last_activity.date().isoformat()
            else:
                last_activity = str(row.last_activity)

        repositories.append(
            PersonRepository(
                name=row.name,
                commits=row.commit_count,
                lastActivity=last_activity,
                expertise=expertise,
            )
        )

    return repositories


async def _get_recent_activity(
    db: AsyncSession,
    person_email: str,
) -> int:
    """
    Count commits in the last 30 days for a person.

    Args:
        db: Async database session
        person_email: Email of the person

    Returns:
        Number of commits in last 30 days
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    stmt = (
        select(func.count())
        .select_from(CommitTable)
        .where(CommitTable.author_email == person_email)
        .where(CommitTable.commit_date >= thirty_days_ago)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def _build_person_model(
    db: AsyncSession,
    person: PersonTable,
) -> Person:
    """
    Build a Person model with all calculated fields.

    Args:
        db: Async database session
        person: PersonTable instance

    Returns:
        Person Pydantic model with calculated metrics
    """
    # Get repository stats
    repositories = await _get_person_repositories(db, person.email)

    # Get recent activity
    recent_activity = await _get_recent_activity(db, person.email)

    # Generate alerts for this person
    alerts = await alert_service.generate_alerts_for_person(db, person.id)

    return Person(
        id=person.id,
        name=person.name,
        email=person.email,
        avatar=person.avatar or _generate_initials(person.name),
        repositories=repositories,
        technologies=[],  # TODO: Implement technology detection
        domains=[],  # TODO: Implement domain detection
        recentActivity=recent_activity,
        alerts=alerts,
    )


def _generate_initials(name: str) -> str:
    """
    Generate avatar initials from name.

    Args:
        name: Full name

    Returns:
        Two-letter initials (e.g., "Ana Silva" -> "AS")
    """
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    return "??"


async def get_all_people(db: AsyncSession) -> list[Person]:
    """
    Get all people with calculated metrics.

    Returns mock data if USE_MOCK_DATA is true, otherwise queries database.

    Args:
        db: Async database session

    Returns:
        List of Person models with calculated metrics
    """
    if settings.use_mock_data:
        return mock_data.get_all_people()

    stmt = select(PersonTable).order_by(PersonTable.name)
    result = await db.execute(stmt)
    persons = result.scalars().all()

    return [await _build_person_model(db, person) for person in persons]


async def get_person_by_id(
    db: AsyncSession,
    person_id: str,
) -> Person | None:
    """
    Get a person by ID with calculated metrics.

    Returns mock data if USE_MOCK_DATA is true, otherwise queries database.

    Args:
        db: Async database session
        person_id: UUID of the person

    Returns:
        Person model with calculated metrics, or None if not found
    """
    if settings.use_mock_data:
        return mock_data.get_person_by_id(person_id)

    stmt = select(PersonTable).where(PersonTable.id == person_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if person is None:
        return None

    return await _build_person_model(db, person)


if __name__ == "__main__":
    print("✅ person_service module loaded successfully")
