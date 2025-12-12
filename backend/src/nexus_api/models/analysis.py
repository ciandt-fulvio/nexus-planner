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

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: RiskLevel enum values
    total_tests += 1
    try:
        expected_values = {"high", "medium", "low"}
        actual_values = {level.value for level in RiskLevel}
        if actual_values != expected_values:
            all_validation_failures.append(
                f"RiskLevel values: Expected {expected_values}, got {actual_values}"
            )
    except Exception as e:
        all_validation_failures.append(f"RiskLevel test failed: {e}")

    # Test 2: ImpactedRepo creation
    total_tests += 1
    try:
        repo = ImpactedRepo(
            name="reports-service",
            confidence=95,
            reasoning="Test",
            modules=["src/api/"],
        )
        if repo.name != "reports-service" or repo.confidence != 95:
            all_validation_failures.append(
                f"ImpactedRepo: Expected reports-service/95, got {repo.name}/{repo.confidence}"
            )
    except Exception as e:
        all_validation_failures.append(f"ImpactedRepo test failed: {e}")

    # Test 3: FeatureAnalysis creation
    total_tests += 1
    try:
        analysis = FeatureAnalysis(
            feature="Test feature",
            impactedRepos=[],
            recommendedPeople=[],
            risks=[],
            suggestedOrder=[],
            additionalRecommendations=[],
        )
        if analysis.feature != "Test feature":
            all_validation_failures.append(
                f"FeatureAnalysis feature: Expected 'Test feature', got '{analysis.feature}'"
            )
    except Exception as e:
        all_validation_failures.append(f"FeatureAnalysis test failed: {e}")

    # Test 4: AnalyzeFeatureRequest validation - valid
    total_tests += 1
    try:
        request = AnalyzeFeatureRequest(description="Valid description")
        if request.description != "Valid description":
            all_validation_failures.append(
                f"Request description: Expected 'Valid description', got '{request.description}'"
            )
    except Exception as e:
        all_validation_failures.append(f"Valid request test failed: {e}")

    # Test 5: AnalyzeFeatureRequest validation - empty rejected
    total_tests += 1
    try:
        AnalyzeFeatureRequest(description="")
        all_validation_failures.append(
            "Empty description: Expected validation error, but none raised"
        )
    except ValueError:
        pass  # Expected
    except Exception as e:
        all_validation_failures.append(f"Empty description test: Unexpected error {type(e).__name__}")

    # Test 6: AnalyzeFeatureRequest validation - whitespace rejected
    total_tests += 1
    try:
        AnalyzeFeatureRequest(description="   ")
        all_validation_failures.append(
            "Whitespace description: Expected validation error, but none raised"
        )
    except ValueError:
        pass  # Expected
    except Exception as e:
        all_validation_failures.append(f"Whitespace description test: Unexpected error {type(e).__name__}")

    # Final validation result
    if all_validation_failures:
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
