"""
Analysis models for Nexus API.

Defines Pydantic models for FeatureAnalysis and related entities.
Mirrors TypeScript interfaces from frontend/src/data/mockData.ts.

Docs: https://docs.pydantic.dev/latest/

Sample input: Feature description for analysis
Expected output: FeatureAnalysis with impacted repos, people, risks
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class RiskLevel(str, Enum):
    """Risk severity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImpactedRepo(BaseModel):
    """Repository impacted by a feature."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    confidence: int  # 0-100
    reasoning: str
    modules: list[str]  # Affected module paths


class RecommendedPerson(BaseModel):
    """Person recommended for a feature."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    name: str
    relevance: int  # 0-100
    reasoning: str


class Risk(BaseModel):
    """Risk identified for a feature."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    type: RiskLevel
    message: str


class SuggestedStep(BaseModel):
    """Suggested implementation step."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    step: int  # 1-based order
    action: str
    repository: str
    reasoning: str


class FeatureAnalysis(BaseModel):
    """Result of analyzing a feature description."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    feature: str  # The input feature description
    impactedRepos: list[ImpactedRepo]
    recommendedPeople: list[RecommendedPerson]
    risks: list[Risk]
    suggestedOrder: list[SuggestedStep]
    additionalRecommendations: list[str]


class AnalyzeFeatureRequest(BaseModel):
    """Request body for feature analysis endpoint."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    description: str

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        """Validate description is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v


if __name__ == "__main__":
    import sys

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: RiskLevel enum values
    validator.add_test(
        "RiskLevel values",
        lambda: {level.value for level in RiskLevel},
        {"high", "medium", "low"},
    )

    # Test 2: ImpactedRepo creation
    validator.add_test(
        "ImpactedRepo creation",
        lambda: (
            repo := ImpactedRepo(
                name="reports-service",
                confidence=95,
                reasoning="Test",
                modules=["src/api/"],
            ),
            (repo.name, repo.confidence),
        )[1],
        ("reports-service", 95),
    )

    # Test 3: FeatureAnalysis creation
    validator.add_test(
        "FeatureAnalysis creation",
        lambda: FeatureAnalysis(
            feature="Test feature",
            impactedRepos=[],
            recommendedPeople=[],
            risks=[],
            suggestedOrder=[],
            additionalRecommendations=[],
        ).feature,
        "Test feature",
    )

    # Test 4: AnalyzeFeatureRequest validation - valid
    validator.add_test(
        "Valid request",
        lambda: AnalyzeFeatureRequest(description="Valid description").description,
        "Valid description",
    )

    # Test 5: AnalyzeFeatureRequest validation - empty rejected
    def test_empty_rejected():
        try:
            AnalyzeFeatureRequest(description="")
            return False  # Should have raised ValueError
        except ValueError:
            return True  # Expected

    validator.add_test("Empty description rejected", test_empty_rejected, True)

    # Test 6: AnalyzeFeatureRequest validation - whitespace rejected
    def test_whitespace_rejected():
        try:
            AnalyzeFeatureRequest(description="   ")
            return False  # Should have raised ValueError
        except ValueError:
            return True  # Expected

    validator.add_test("Whitespace description rejected", test_whitespace_rejected, True)

    sys.exit(validator.run())
