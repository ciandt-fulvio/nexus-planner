"""
Analysis router for Nexus API.

Provides endpoint for feature analysis with database storage.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/
Docs: https://fastapi.tiangolo.com/tutorial/dependencies/

Sample input: POST /api/v1/analysis with {"description": "feature text"}
Expected output: FeatureAnalysis object as JSON
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.database import get_db
from nexus_api.models.analysis import AnalyzeFeatureRequest, FeatureAnalysis
from nexus_api.services import analysis_service

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post("", response_model=FeatureAnalysis)
async def analyze_feature(
    request: AnalyzeFeatureRequest,
    db: AsyncSession = Depends(get_db),
) -> FeatureAnalysis:
    """
    Analyze a feature description and return impact assessment.

    Creates an analysis based on repository and person data from the database.
    Saves the analysis to the database for future reference.

    Database is seeded automatically on startup in development mode.

    Args:
        request: Feature description to analyze
        db: Database session from dependency injection

    Returns:
        FeatureAnalysis with impacted repos, recommended people, and risks
    """
    # Create analysis from database data
    analysis = await analysis_service.create_analysis(db, request.description)

    # Save analysis to database if we have impacted repos
    if analysis.impactedRepos:
        await analysis_service.save_analysis(db, analysis)

    return analysis


if __name__ == "__main__":
    import sys

    from fastapi.testclient import TestClient

    from nexus_api.main import app
    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()
    client = TestClient(app)

    # Test 1: POST /api/v1/analysis returns 200
    validator.add_test(
        "POST /analysis status",
        lambda: client.post("/api/v1/analysis", json={"description": "Test feature"}).status_code,
        200,
    )

    # Test 2: Response contains expected fields
    def test_response_fields():
        data = client.post("/api/v1/analysis", json={"description": "Test feature"}).json()
        required_fields = ["feature", "impactedRepos", "recommendedPeople", "risks", "suggestedOrder"]
        missing = [f for f in required_fields if f not in data]
        return len(missing) == 0

    validator.add_test("Response has required fields", test_response_fields, True)

    # Test 3: Response contains 4 impacted repos
    validator.add_test(
        "impactedRepos count",
        lambda: len(
            client.post("/api/v1/analysis", json={"description": "Test feature"}).json()["impactedRepos"]
        ),
        4,
    )

    # Test 4: Empty description returns 422
    validator.add_test(
        "Empty description status",
        lambda: client.post("/api/v1/analysis", json={"description": ""}).status_code,
        422,
    )

    # Test 5: Whitespace description returns 422
    validator.add_test(
        "Whitespace description status",
        lambda: client.post("/api/v1/analysis", json={"description": "   "}).status_code,
        422,
    )

    sys.exit(validator.run())
