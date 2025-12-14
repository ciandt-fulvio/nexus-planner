"""
Commit service for CRUD operations on commits.

Provides async functions for creating, reading, and querying commits.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Commit data dict
Expected output: CommitTable instances or query results
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.config import settings
from nexus_api.db.tables import CommitTable


async def create_commit(
    db: AsyncSession,
    commit_data: dict[str, Any],
) -> CommitTable:
    """
    Create a new commit in the database.

    Args:
        db: Async database session
        commit_data: Dict with commit fields

    Returns:
        Created CommitTable instance
    """
    commit = CommitTable(
        id=commit_data["id"],
        repository_id=commit_data["repository_id"],
        author_name=commit_data["author_name"],
        author_email=commit_data["author_email"],
        committer_name=commit_data["committer_name"],
        committer_email=commit_data["committer_email"],
        author_date=commit_data["author_date"],
        commit_date=commit_data["commit_date"],
        message=commit_data["message"],
        files_changed=commit_data.get("files_changed", []),
        additions=commit_data.get("additions", 0),
        deletions=commit_data.get("deletions", 0),
        parent_shas=commit_data.get("parent_shas"),
    )
    db.add(commit)
    await db.commit()
    await db.refresh(commit)
    return commit


async def get_commits_by_repository(
    db: AsyncSession,
    repository_id: str,
    limit: int | None = None,
) -> list[CommitTable]:
    """
    Get commits for a repository, ordered by commit date descending.

    Args:
        db: Async database session
        repository_id: UUID of the repository
        limit: Maximum number of commits to return (uses window_size if None)

    Returns:
        List of CommitTable instances
    """
    max_results = limit if limit is not None else settings.window_size

    stmt = (
        select(CommitTable)
        .where(CommitTable.repository_id == repository_id)
        .order_by(CommitTable.commit_date.desc())
        .limit(max_results)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_commits_last_30_days(
    db: AsyncSession,
    repository_id: str,
) -> int:
    """
    Count commits in the last 30 days for a repository.

    Args:
        db: Async database session
        repository_id: UUID of the repository

    Returns:
        Number of commits in last 30 days
    """
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

    stmt = (
        select(func.count())
        .select_from(CommitTable)
        .where(CommitTable.repository_id == repository_id)
        .where(CommitTable.commit_date >= thirty_days_ago)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_contributor_stats(
    db: AsyncSession,
    repository_id: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Get contributor statistics for a repository.

    Args:
        db: Async database session
        repository_id: UUID of the repository
        limit: Use sliding window limit (window_size)

    Returns:
        List of dicts with author_email, author_name, count
    """
    max_commits = limit if limit is not None else settings.window_size

    # Subquery to get the most recent commits within window
    subq = (
        select(CommitTable)
        .where(CommitTable.repository_id == repository_id)
        .order_by(CommitTable.commit_date.desc())
        .limit(max_commits)
        .subquery()
    )

    # Aggregate by author
    stmt = (
        select(
            subq.c.author_email,
            subq.c.author_name,
            func.count().label("count"),
        )
        .group_by(subq.c.author_email, subq.c.author_name)
        .order_by(func.count().desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"author_email": row.author_email, "author_name": row.author_name, "count": row.count}
        for row in rows
    ]


async def get_file_change_stats(
    db: AsyncSession,
    repository_id: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    Get file change statistics for a repository.

    Args:
        db: Async database session
        repository_id: UUID of the repository
        limit: Use sliding window limit (window_size)

    Returns:
        List of dicts with path, changes, last_modified, contributors
    """
    max_commits = limit if limit is not None else settings.window_size

    # Get commits within window
    commits = await get_commits_by_repository(db, repository_id, limit=max_commits)

    # Aggregate file changes
    file_stats: dict[str, dict[str, Any]] = {}
    for commit in commits:
        files_changed = commit.files_changed or []
        for file_change in files_changed:
            path = file_change.get("path", "")
            if not path:
                continue

            if path not in file_stats:
                file_stats[path] = {
                    "path": path,
                    "changes": 0,
                    "last_modified": commit.commit_date.date() if commit.commit_date else None,
                    "contributors": set(),
                }

            file_stats[path]["changes"] += 1
            file_stats[path]["contributors"].add(commit.author_email)

            # Update last_modified if this commit is more recent
            if commit.commit_date:
                current_date = file_stats[path]["last_modified"]
                commit_date = commit.commit_date.date()
                if current_date is None or commit_date > current_date:
                    file_stats[path]["last_modified"] = commit_date

    # Convert sets to counts
    result = []
    for _path, stats in file_stats.items():
        result.append({
            "path": stats["path"],
            "changes": stats["changes"],
            "last_modified": stats["last_modified"],
            "contributors": len(stats["contributors"]),
        })

    return result


if __name__ == "__main__":
    print("✅ commit_service module loaded successfully")
