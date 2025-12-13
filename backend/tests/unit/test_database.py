"""
Unit tests for database connection and session management.

Tests the async SQLite engine and session factory.
Following TDD: these tests are written FIRST and should FAIL until implementation.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


@pytest.mark.unit
@pytest.mark.asyncio
async def test_engine_is_async_engine():
    """Test that engine is an AsyncEngine instance."""
    from nexus_api.db.database import engine

    assert isinstance(engine, AsyncEngine)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_engine_uses_aiosqlite():
    """Test that engine uses aiosqlite dialect."""
    from nexus_api.db.database import engine

    assert "aiosqlite" in str(engine.url)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_session_factory_creates_session():
    """Test that async_session factory creates AsyncSession instances."""
    from nexus_api.db.database import async_session

    async with async_session() as session:
        assert isinstance(session, AsyncSession)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_db_yields_session():
    """Test that get_db dependency yields a session."""
    from nexus_api.db.database import get_db

    sessions = []
    async for session in get_db():
        sessions.append(session)
        assert isinstance(session, AsyncSession)

    assert len(sessions) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_base_metadata_exists():
    """Test that Base has metadata for table creation."""
    from nexus_api.db.database import Base

    assert hasattr(Base, "metadata")
    assert Base.metadata is not None
