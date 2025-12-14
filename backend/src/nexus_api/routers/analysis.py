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

    # Import the main app to test with full context
    from nexus_api.main import app

    all_validation_failures: list[str] = []
    total_tests = 0

    # Use main app with lifespan and database
    client = TestClient(app)

    # Test 1: POST /api/v1/analysis returns 200
    total_tests += 1
    response = client.post(
        "/api/v1/analysis",
        json={"description": "Test feature"},
    )
    if response.status_code != 200:
        all_validation_failures.append(
            f"POST /analysis status: Expected 200, got {response.status_code}"
        )

    # Test 2: Response contains expected fields
    total_tests += 1
    data = response.json()
    required_fields = ["feature", "impactedRepos", "recommendedPeople", "risks", "suggestedOrder"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        all_validation_failures.append(f"Response missing fields: {missing}")

    # Test 3: Response contains impacted repos
    total_tests += 1
    if "impactedRepos" in data and len(data["impactedRepos"]) != 4:
        all_validation_failures.append(
            f"impactedRepos count: Expected 4, got {len(data['impactedRepos'])}"
        )

    # Test 4: Empty description returns 422
    total_tests += 1
    response = client.post(
        "/api/v1/analysis",
        json={"description": ""},
    )
    if response.status_code != 422:
        all_validation_failures.append(
            f"Empty description status: Expected 422, got {response.status_code}"
        )

    # Test 5: Whitespace description returns 422
    total_tests += 1
    response = client.post(
        "/api/v1/analysis",
        json={"description": "   "},
    )
    if response.status_code != 422:
        all_validation_failures.append(
            f"Whitespace description status: Expected 422, got {response.status_code}"
        )

    # Final validation result
    if all_validation_failures:
        print(
            f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:"
        )
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
