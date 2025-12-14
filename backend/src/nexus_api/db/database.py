"""
Database connection and session management for Nexus API.

Uses SQLAlchemy 2.0 async engine with aiosqlite for non-blocking database operations.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
Docs: https://github.com/omnilib/aiosqlite

Sample usage:
    from nexus_api.db.database import get_db, engine, Base

    # In FastAPI route
    @app.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from nexus_api.config import settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""

    pass


# Create async engine with aiosqlite
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI route handlers.

    Yields an async database session and ensures proper cleanup.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    import sys

    async def validate() -> list[str]:
        """Validate database module functionality."""
        failures: list[str] = []

        # Test 1: Engine is async engine
        if not hasattr(engine, "dialect"):
            failures.append("Engine: Missing dialect attribute")

        # Test 2: Engine uses aiosqlite
        if "aiosqlite" not in str(engine.url):
            failures.append(f"Engine dialect: Expected aiosqlite, got {engine.url}")

        # Test 3: Session factory creates sessions
        async with async_session() as session:
            if not isinstance(session, AsyncSession):
                failures.append(f"Session: Expected AsyncSession, got {type(session)}")

        # Test 4: get_db yields session
        sessions = []
        async for session in get_db():
            sessions.append(session)
        if len(sessions) != 1:
            failures.append(f"get_db: Expected 1 session, got {len(sessions)}")

        # Test 5: Base has metadata
        if not hasattr(Base, "metadata"):
            failures.append("Base: Missing metadata attribute")

        return failures

    all_failures = asyncio.run(validate())
    total_tests = 5

    if all_failures:
        print(f"❌ VALIDATION FAILED - {len(all_failures)} of {total_tests} tests failed:")
        for failure in all_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
