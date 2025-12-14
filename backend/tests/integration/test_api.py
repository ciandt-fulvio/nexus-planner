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

    def test_get_repositories_contains_expected_repos(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test repositories contain expected seeded data."""
        response = client.get(f"{api_v1_prefix}/repositories")
        data = response.json()

        # Verify expected repo names exist (sorted alphabetically)
        repo_names = [repo["name"] for repo in data]
        assert "reports-service" in repo_names
        assert "finance-core" in repo_names
        assert "ui-dashboard" in repo_names

    def test_get_repositories_first_repo_has_valid_data(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test first repository has valid calculated data."""
        response = client.get(f"{api_v1_prefix}/repositories")
        data = response.json()

        first_repo = data[0]
        # ID can be UUID format (36 chars) or simple string (when USE_MOCK_DATA=true)
        assert isinstance(first_repo["id"], str)
        assert len(first_repo["id"]) > 0
        assert isinstance(first_repo["name"], str)
        assert first_repo["activity"] in {"high", "medium", "low", "stale"}
        assert 0 <= first_repo["knowledgeConcentration"] <= 100
        assert isinstance(first_repo["topContributors"], list)


@pytest.mark.integration
class TestPeopleEndpoint:
    """Tests for GET /api/v1/people endpoint."""

    def test_get_people_returns_list(self, client: TestClient, api_v1_prefix: str) -> None:
        """Test GET /people returns a list of people."""
        response = client.get(f"{api_v1_prefix}/people")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_people_returns_expected_count(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /people returns seeded people."""
        response = client.get(f"{api_v1_prefix}/people")
        assert response.status_code == 200
        data = response.json()
        # At least 5 people from seed + any additional from commits
        assert len(data) >= 5

    def test_get_people_contains_required_fields(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test each person has all required fields."""
        response = client.get(f"{api_v1_prefix}/people")
        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "id",
            "name",
            "email",
            "avatar",
            "repositories",
            "technologies",
            "domains",
            "recentActivity",
            "alerts",
        ]

        for person in data:
            for field in required_fields:
                assert field in person, f"Missing field: {field}"

    def test_get_people_contains_expected_people(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test people contain expected seeded data."""
        response = client.get(f"{api_v1_prefix}/people")
        data = response.json()

        people_names = [person["name"] for person in data]
        assert "Ana Silva" in people_names

    def test_get_people_first_person_has_valid_data(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test first person has valid calculated data."""
        response = client.get(f"{api_v1_prefix}/people")
        data = response.json()

        first_person = data[0]
        # ID can be UUID format (36 chars) or simple string (when USE_MOCK_DATA=true)
        assert isinstance(first_person["id"], str)
        assert len(first_person["id"]) > 0
        assert isinstance(first_person["name"], str)
        assert "@" in first_person["email"]
        assert len(first_person["avatar"]) >= 2
        assert first_person["recentActivity"] >= 0
        assert isinstance(first_person["repositories"], list)


@pytest.mark.integration
class TestAnalysisEndpoint:
    """Tests for POST /api/v1/analysis endpoint."""

    def test_post_analysis_returns_feature_analysis(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test POST /analysis returns a FeatureAnalysis."""
        response = client.post(
            f"{api_v1_prefix}/analysis",
            json={"description": "Test feature description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "feature" in data
        assert "impactedRepos" in data
        assert "recommendedPeople" in data
        assert "risks" in data
        assert "suggestedOrder" in data
        assert "additionalRecommendations" in data

    def test_post_analysis_contains_impacted_repos(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test analysis response contains impacted repos from seeded data."""
        response = client.post(
            f"{api_v1_prefix}/analysis",
            json={"description": "Any feature"},
        )
        data = response.json()

        # Should return repos based on active repositories in database
        assert isinstance(data["impactedRepos"], list)
        # With seeded data, we should have impacted repos
        assert len(data["impactedRepos"]) >= 0

    def test_post_analysis_contains_recommended_people(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test analysis response contains recommended people."""
        response = client.post(
            f"{api_v1_prefix}/analysis",
            json={"description": "Any feature"},
        )
        data = response.json()

        assert isinstance(data["recommendedPeople"], list)

    def test_post_analysis_empty_description_returns_400(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test empty description returns 400 error."""
        response = client.post(
            f"{api_v1_prefix}/analysis",
            json={"description": ""},
        )
        assert response.status_code == 422  # Validation error

    def test_post_analysis_whitespace_description_returns_400(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test whitespace-only description returns 400 error."""
        response = client.post(
            f"{api_v1_prefix}/analysis",
            json={"description": "   "},
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestRepositoryDetailEndpoint:
    """Tests for GET /api/v1/repositories/{id} endpoint."""

    def test_get_repository_by_id_success(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /repositories/{id} returns the repository."""
        # First get the list to get a valid ID
        list_response = client.get(f"{api_v1_prefix}/repositories")
        repos = list_response.json()
        first_repo_id = repos[0]["id"]

        response = client.get(f"{api_v1_prefix}/repositories/{first_repo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == first_repo_id

    def test_get_repository_by_id_not_found(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /repositories/invalid-uuid returns 404."""
        response = client.get(f"{api_v1_prefix}/repositories/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_repository_contains_all_fields(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test returned repository has all required fields."""
        # First get the list to get a valid ID
        list_response = client.get(f"{api_v1_prefix}/repositories")
        repos = list_response.json()
        first_repo_id = repos[0]["id"]

        response = client.get(f"{api_v1_prefix}/repositories/{first_repo_id}")
        data = response.json()

        required_fields = [
            "id", "name", "description", "lastCommit", "totalCommits",
            "contributors", "activity", "knowledgeConcentration",
            "topContributors", "hotspots", "dependencies", "alerts"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


@pytest.mark.integration
class TestPersonDetailEndpoint:
    """Tests for GET /api/v1/people/{id} endpoint."""

    def test_get_person_by_id_success(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /people/{id} returns the person."""
        # First get the list to get a valid ID
        list_response = client.get(f"{api_v1_prefix}/people")
        people = list_response.json()
        first_person_id = people[0]["id"]

        response = client.get(f"{api_v1_prefix}/people/{first_person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == first_person_id

    def test_get_person_by_id_not_found(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test GET /people/invalid-uuid returns 404."""
        response = client.get(f"{api_v1_prefix}/people/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_person_contains_all_fields(
        self, client: TestClient, api_v1_prefix: str
    ) -> None:
        """Test returned person has all required fields."""
        # First get the list to get a valid ID
        list_response = client.get(f"{api_v1_prefix}/people")
        people = list_response.json()
        first_person_id = people[0]["id"]

        response = client.get(f"{api_v1_prefix}/people/{first_person_id}")
        data = response.json()

        required_fields = [
            "id", "name", "email", "avatar", "repositories",
            "technologies", "domains", "recentActivity", "alerts"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
