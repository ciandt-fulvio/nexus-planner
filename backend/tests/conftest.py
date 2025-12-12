"""
Shared pytest fixtures for Nexus API tests.

Docs: https://docs.pytest.org/en/stable/reference/fixtures.html

Provides:
- TestClient fixture for integration tests
- Common test data fixtures
"""

import pytest
from fastapi.testclient import TestClient

from nexus_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def api_v1_prefix() -> str:
    """Return the API v1 prefix."""
    return "/api/v1"
