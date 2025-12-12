"""
Analysis router for Nexus API.

Provides endpoint for feature analysis.

Docs: https://fastapi.tiangolo.com/tutorial/bigger-applications/

Sample input: POST /api/v1/analysis with {"description": "feature text"}
Expected output: FeatureAnalysis object as JSON
"""

from fastapi import APIRouter

from nexus_api.data.mock_data import get_example_analysis
from nexus_api.models.analysis import AnalyzeFeatureRequest, FeatureAnalysis

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post("", response_model=FeatureAnalysis)
def analyze_feature(request: AnalyzeFeatureRequest) -> FeatureAnalysis:
    """
    Analyze a feature description.

    Returns static example analysis regardless of input.
    In future versions, this will perform actual analysis.
    """
    # For now, return the static example analysis
    # The request.description is validated but not used
    return get_example_analysis()


if __name__ == "__main__":
    import sys

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    all_validation_failures: list[str] = []
    total_tests = 0

    # Create test app
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
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
        all_validation_failures.append(
            f"Response missing fields: {missing}"
        )

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
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
