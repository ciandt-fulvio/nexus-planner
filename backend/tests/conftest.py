"""
Shared pytest fixtures for Nexus API tests.

Docs: https://docs.pytest.org/en/stable/reference/fixtures.html

Provides:
- TestClient fixture for integration tests
- Database session fixtures for unit tests
- Common test data fixtures
"""

import sys
import uuid
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nexus_api.db.database import Base  # noqa: E402
from nexus_api.main import app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application.

    Uses context manager to trigger lifespan events (startup/shutdown).
    This ensures database tables are created and seeded before tests run.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def api_v1_prefix() -> str:
    """Return the API v1 prefix."""
    return "/api/v1"


# Test database engine (in-memory SQLite)
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)

test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with tables."""
    # Import tables to register them with Base.metadata
    from nexus_api.db import tables  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def sample_repository_id() -> str:
    """Return a sample repository UUID."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_person_id() -> str:
    """Return a sample person UUID."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_commit_sha() -> str:
    """Return a sample commit SHA."""
    return "a" * 40  # Valid 40-char SHA


@pytest.fixture
def sample_datetime() -> datetime:
    """Return a sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
