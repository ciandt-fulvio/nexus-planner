"""
Integration tests for API endpoints.

Tests endpoint behavior, response formats, and error handling.
TDD: These tests must FAIL before implementation.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestRepositoriesEndpoint:
    """Tests for GET /api/v1/repositories endpoint."""

    def test_get_repositories_returns_list(self, client: TestClient, api_v1_prefix: str) -> None:
        """Test GET /repositories returns a list of repositories."""
        response = client.get(f"{api_v1_prefix}/repositories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_repositories_returns_five_repos(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /repositories returns exactly 5 repositories."""
        response = client.get(f"{api_v1_prefix}/repositories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_repositories_contains_required_fields(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test each repository has all required fields."""
        response = client.get(f"{api_v1_prefix}/repositories")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "id",
            "name",
            "description",
            "lastCommit",
            "totalCommits",
            "contributors",
            "activity",
            "knowledgeConcentration",
            "topContributors",
            "hotspots",
            "dependencies",
            "alerts",
        ]

        for repo in data:
            for field in required_fields:
                assert field in repo, f"Missing field: {field}"

    def test_get_repositories_activity_valid_values(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test activity field contains valid values."""
        response = client.get(f"{api_v1_prefix}/repositories")
        data = response.json()

        valid_activities = {"high", "medium", "low", "stale"}
        for repo in data:
            assert repo["activity"] in valid_activities

    def test_get_repositories_first_repo_is_reports_service(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test first repository is reports-service with correct data."""
        response = client.get(f"{api_v1_prefix}/repositories")
        data = response.json()

        first_repo = data[0]
        assert first_repo["id"] == "1"
        assert first_repo["name"] == "reports-service"
        assert first_repo["activity"] == "high"
        assert first_repo["knowledgeConcentration"] == 45
        assert len(first_repo["topContributors"]) == 3
        assert first_repo["topContributors"][0]["name"] == "Ana Silva"
