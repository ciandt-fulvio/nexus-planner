"""
Unit tests for SQLAlchemy table definitions.

Tests the ORM table structure for all entities.
Following TDD: these tests are written FIRST and should FAIL until implementation.

Docs: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html
"""

import pytest
from sqlalchemy import Column, inspect


@pytest.mark.unit
def test_commit_table_exists():
    """Test that CommitTable is defined."""
    from nexus_api.db.tables import CommitTable

    assert CommitTable.__tablename__ == "commits"


@pytest.mark.unit
def test_commit_table_has_required_columns():
    """Test that CommitTable has all required columns."""
    from nexus_api.db.tables import CommitTable

    mapper = inspect(CommitTable)
    column_names = [c.key for c in mapper.columns]

    required_columns = [
        "id",
        "repository_id",
        "author_name",
        "author_email",
        "committer_name",
        "committer_email",
        "author_date",
        "commit_date",
        "message",
        "files_changed",
        "additions",
        "deletions",
        "parent_shas",
    ]

    for col in required_columns:
        assert col in column_names, f"Missing column: {col}"


@pytest.mark.unit
def test_repository_table_exists():
    """Test that RepositoryTable is defined."""
    from nexus_api.db.tables import RepositoryTable

    assert RepositoryTable.__tablename__ == "repositories"


@pytest.mark.unit
def test_repository_table_has_required_columns():
    """Test that RepositoryTable has all required columns."""
    from nexus_api.db.tables import RepositoryTable

    mapper = inspect(RepositoryTable)
    column_names = [c.key for c in mapper.columns]

    required_columns = [
        "id",
        "name",
        "description",
        "git_url",
        "last_alerts_pr_id",
        "created_at",
        "updated_at",
    ]

    for col in required_columns:
        assert col in column_names, f"Missing column: {col}"


@pytest.mark.unit
def test_person_table_exists():
    """Test that PersonTable is defined."""
    from nexus_api.db.tables import PersonTable

    assert PersonTable.__tablename__ == "persons"


@pytest.mark.unit
def test_person_table_has_required_columns():
    """Test that PersonTable has all required columns."""
    from nexus_api.db.tables import PersonTable

    mapper = inspect(PersonTable)
    column_names = [c.key for c in mapper.columns]

    required_columns = [
        "id",
        "email",
        "name",
        "avatar",
        "last_alert_commit_sha",
        "created_at",
        "updated_at",
    ]

    for col in required_columns:
        assert col in column_names, f"Missing column: {col}"


@pytest.mark.unit
def test_alert_table_exists():
    """Test that AlertTable is defined."""
    from nexus_api.db.tables import AlertTable

    assert AlertTable.__tablename__ == "alerts"


@pytest.mark.unit
def test_alert_table_has_required_columns():
    """Test that AlertTable has all required columns."""
    from nexus_api.db.tables import AlertTable

    mapper = inspect(AlertTable)
    column_names = [c.key for c in mapper.columns]

    required_columns = [
        "id",
        "entity_type",
        "entity_id",
        "reference_id",
        "title",
        "description",
        "severity",
        "category",
        "suggested_actions",
        "created_at",
    ]

    for col in required_columns:
        assert col in column_names, f"Missing column: {col}"


@pytest.mark.unit
def test_feature_analysis_table_exists():
    """Test that FeatureAnalysisTable is defined."""
    from nexus_api.db.tables import FeatureAnalysisTable

    assert FeatureAnalysisTable.__tablename__ == "feature_analyses"


@pytest.mark.unit
def test_feature_analysis_table_has_required_columns():
    """Test that FeatureAnalysisTable has all required columns."""
    from nexus_api.db.tables import FeatureAnalysisTable

    mapper = inspect(FeatureAnalysisTable)
    column_names = [c.key for c in mapper.columns]

    required_columns = [
        "id",
        "feature_description",
        "analysis_text",
        "created_at",
    ]

    for col in required_columns:
        assert col in column_names, f"Missing column: {col}"


@pytest.mark.unit
def test_commit_table_primary_key():
    """Test that CommitTable has id as primary key."""
    from nexus_api.db.tables import CommitTable

    mapper = inspect(CommitTable)
    pk_columns = [c.name for c in mapper.primary_key]
    assert pk_columns == ["id"]


@pytest.mark.unit
def test_repository_table_primary_key():
    """Test that RepositoryTable has id as primary key."""
    from nexus_api.db.tables import RepositoryTable

    mapper = inspect(RepositoryTable)
    pk_columns = [c.name for c in mapper.primary_key]
    assert pk_columns == ["id"]
