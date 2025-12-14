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

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: Engine has dialect
    validator.add_test("Engine has dialect", lambda: hasattr(engine, "dialect"), True)

    # Test 2: Engine uses aiosqlite
    validator.add_test("Engine uses aiosqlite", lambda: "aiosqlite" in str(engine.url), True)

    # Test 3: Session factory creates AsyncSession
    async def test_session_factory():
        async with async_session() as session:
            return isinstance(session, AsyncSession)

    validator.add_test("Session factory creates AsyncSession", lambda: asyncio.run(test_session_factory()), True)

    # Test 4: get_db yields exactly one session
    async def test_get_db():
        sessions = []
        async for session in get_db():
            sessions.append(session)
        return len(sessions)

    validator.add_test("get_db yields one session", lambda: asyncio.run(test_get_db()), 1)

    # Test 5: Base has metadata
    validator.add_test("Base has metadata", lambda: hasattr(Base, "metadata"), True)

    sys.exit(validator.run())
