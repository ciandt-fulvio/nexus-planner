"""
Seed service for populating the database with development data.

Converts mock data to database tables for development and demo purposes.
Should only run when database is empty or when explicitly requested.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Empty database
Expected output: Populated database with mock repositories, people, and commits
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.data import mock_data
from nexus_api.db.tables import CommitTable, PersonTable, RepositoryTable


async def is_database_empty(db: AsyncSession) -> bool:
    """
    Check if the database has any data.

    Args:
        db: Async database session

    Returns:
        True if database is empty, False otherwise
    """
    stmt = select(func.count()).select_from(RepositoryTable)
    result = await db.execute(stmt)
    count = result.scalar() or 0
    return count == 0


async def seed_database(db: AsyncSession) -> dict[str, int]:
    """
    Populate the database with mock data for development.

    Creates repositories, people, and synthetic commits based on mock data.
    Only runs if database is empty.

    Args:
        db: Async database session

    Returns:
        Dict with counts of created entities
    """
    if not await is_database_empty(db):
        return {"repositories": 0, "people": 0, "commits": 0, "skipped": True}

    # Get mock data
    mock_repos = mock_data.get_all_repositories()
    mock_people = mock_data.get_all_people()

    # Create repositories
    repo_mapping: dict[str, str] = {}  # name -> id
    for mock_repo in mock_repos:
        repo_id = str(uuid.uuid4())
        repo_mapping[mock_repo.name] = repo_id

        repo = RepositoryTable(
            id=repo_id,
            name=mock_repo.name,
            description=mock_repo.description,
            git_url=f"https://github.com/company/{mock_repo.name}.git",
        )
        db.add(repo)

    # Create people
    person_mapping: dict[str, str] = {}  # email -> id
    for mock_person in mock_people:
        person_id = str(uuid.uuid4())
        person_mapping[mock_person.email] = person_id

        person = PersonTable(
            id=person_id,
            email=mock_person.email,
            name=mock_person.name,
            avatar=mock_person.avatar,
        )
        db.add(person)

    await db.commit()

    # Create synthetic commits based on mock data
    commits_created = 0
    now = datetime.now(UTC)

    for mock_repo in mock_repos:
        repo_id = repo_mapping.get(mock_repo.name)
        if not repo_id:
            continue

        # Create commits for each contributor
        for contributor in mock_repo.topContributors:
            # Ensure person exists in mapping
            if contributor.email not in person_mapping:
                person_id = str(uuid.uuid4())
                person_mapping[contributor.email] = person_id
                person = PersonTable(
                    id=person_id,
                    email=contributor.email,
                    name=contributor.name,
                    avatar=contributor.name[:2].upper(),
                )
                db.add(person)

            # Create commits spread over time
            commits_to_create = contributor.commits
            for i in range(commits_to_create):
                # Spread commits over the last year, with more recent ones
                # closer to the last commit date
                days_ago = int((i / commits_to_create) * 365)
                commit_date = now - timedelta(days=days_ago)

                # Generate file changes based on hotspots
                files_changed = []
                if mock_repo.hotspots:
                    hotspot = mock_repo.hotspots[i % len(mock_repo.hotspots)]
                    files_changed = [{"path": hotspot.path, "status": "modified"}]

                commit = CommitTable(
                    id=f"{repo_id[:8]}-{contributor.email[:8]}-{i:06d}",
                    repository_id=repo_id,
                    author_name=contributor.name,
                    author_email=contributor.email,
                    committer_name=contributor.name,
                    committer_email=contributor.email,
                    author_date=commit_date,
                    commit_date=commit_date,
                    message=f"Update {mock_repo.name} - commit {i + 1}",
                    files_changed=files_changed,
                    additions=10 + (i % 50),
                    deletions=5 + (i % 20),
                )
                db.add(commit)
                commits_created += 1

    await db.commit()

    return {
        "repositories": len(mock_repos),
        "people": len(person_mapping),
        "commits": commits_created,
        "skipped": False,
    }


async def clear_database(db: AsyncSession) -> dict[str, int]:
    """
    Clear all data from the database.

    Use with caution - this deletes all data!

    Args:
        db: Async database session

    Returns:
        Dict with counts of deleted entities
    """
    from nexus_api.db.tables import AlertTable, FeatureAnalysisTable

    # Count before delete
    repos_count = (await db.execute(select(func.count()).select_from(RepositoryTable))).scalar() or 0
    people_count = (await db.execute(select(func.count()).select_from(PersonTable))).scalar() or 0
    commits_count = (await db.execute(select(func.count()).select_from(CommitTable))).scalar() or 0

    # Delete in order (respecting foreign keys)
    await db.execute(CommitTable.__table__.delete())
    await db.execute(AlertTable.__table__.delete())
    await db.execute(FeatureAnalysisTable.__table__.delete())
    await db.execute(PersonTable.__table__.delete())
    await db.execute(RepositoryTable.__table__.delete())
    await db.commit()

    return {
        "repositories": repos_count,
        "people": people_count,
        "commits": commits_count,
    }


if __name__ == "__main__":
    print("✅ seed_service module loaded successfully")
