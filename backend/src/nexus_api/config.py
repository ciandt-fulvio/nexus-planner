"""
Configuration module for Nexus API.

Uses pydantic-settings for type-safe configuration from environment variables.
Docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

Sample input: Environment variables in backend/.env
Expected output: Settings instance with validated configuration
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are REQUIRED - no defaults. Application will fail to start if any variable is missing.
    See .env.example for all required variables and their descriptions.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration (REQUIRED)
    host: str = Field(..., description="Server host")
    port: int = Field(..., description="Server port")
    debug: bool = Field(..., description="Debug mode (true/false)")

    # CORS Configuration (REQUIRED)
    cors_origins: str = Field(..., description="CORS allowed origins (comma-separated)")

    # API Configuration (REQUIRED)
    api_v1_prefix: str = Field(..., description="API v1 prefix")

    # Database Configuration (REQUIRED)
    database_url: str = Field(..., description="Database URL (sqlite or postgresql)")

    # Data Source Configuration (REQUIRED)
    use_mock_data: bool = Field(
        ...,
        description="Use mock data from mock_data.py (true) or real data from services (false)"
    )

    # Seed Configuration (REQUIRED)
    auto_seed: bool = Field(
        ..., description="Automatically seed database on startup if empty (true) or not (false)"
    )

    # Sliding Window Configuration (REQUIRED)
    window_size: int = Field(..., description="Number of most recent commits for calculations")

    # Activity Thresholds (REQUIRED) - commits in last 30 days
    activity_high_threshold: int = Field(..., description="Activity threshold for high activity level")
    activity_medium_threshold: int = Field(..., description="Activity threshold for medium activity level")
    activity_low_threshold: int = Field(..., description="Activity threshold for low activity level")

    # Knowledge Concentration Thresholds (REQUIRED) - percentage values
    concentration_warning_threshold: int = Field(..., description="Knowledge concentration warning threshold (%)")
    concentration_critical_threshold: int = Field(..., description="Knowledge concentration critical threshold (%)")

    # Display Limits (REQUIRED)
    top_contributors_limit: int = Field(..., description="Maximum number of top contributors to display")
    top_hotspots_limit: int = Field(..., description="Maximum number of hotspots to display")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton instance
settings = Settings()


if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: All required variables present and correct types
    total_tests += 1
    try:
        test_settings = Settings(
            host="0.0.0.0",
            port=8000,
            debug=True,
            cors_origins="http://localhost:8080",
            api_v1_prefix="/api/v1",
            database_url="sqlite+aiosqlite:///test.db",
            use_mock_data=True,
            auto_seed=True,
            window_size=300,
            activity_high_threshold=30,
            activity_medium_threshold=10,
            activity_low_threshold=1,
            concentration_warning_threshold=50,
            concentration_critical_threshold=70,
            top_contributors_limit=3,
            top_hotspots_limit=5,
        )
        if test_settings.host != "0.0.0.0":
            all_validation_failures.append(
                f"Host: Expected '0.0.0.0', got '{test_settings.host}'"
            )
        if test_settings.port != 8000:
            all_validation_failures.append(f"Port: Expected 8000, got {test_settings.port}")
        if test_settings.debug != True:
            all_validation_failures.append(f"Debug: Expected True, got {test_settings.debug}")
    except Exception as e:
        all_validation_failures.append(f"Settings load failed: {e}")

    # Test 2: USE_MOCK_DATA can be true or false
    total_tests += 1
    try:
        test_settings_real = Settings(
            host="0.0.0.0",
            port=8000,
            debug=False,
            cors_origins="http://example.com",
            api_v1_prefix="/api/v1",
            database_url="postgresql://user:pass@localhost/db",
            use_mock_data=False,
            auto_seed=False,
            window_size=300,
            activity_high_threshold=30,
            activity_medium_threshold=10,
            activity_low_threshold=1,
            concentration_warning_threshold=50,
            concentration_critical_threshold=70,
            top_contributors_limit=3,
            top_hotspots_limit=5,
        )
        if test_settings_real.use_mock_data != False:
            all_validation_failures.append(
                f"USE_MOCK_DATA false: Expected False, got {test_settings_real.use_mock_data}"
            )
    except Exception as e:
        all_validation_failures.append(f"USE_MOCK_DATA false test failed: {e}")

    # Test 3: CORS origins parsing
    total_tests += 1
    try:
        test_settings = Settings(
            host="0.0.0.0",
            port=8000,
            debug=True,
            cors_origins="http://localhost:3000,http://localhost:8080",
            api_v1_prefix="/api/v1",
            database_url="sqlite+aiosqlite:///test.db",
            use_mock_data=True,
            auto_seed=True,
            window_size=300,
            activity_high_threshold=30,
            activity_medium_threshold=10,
            activity_low_threshold=1,
            concentration_warning_threshold=50,
            concentration_critical_threshold=70,
            top_contributors_limit=3,
            top_hotspots_limit=5,
        )
        expected_origins = ["http://localhost:3000", "http://localhost:8080"]
        if test_settings.cors_origins_list != expected_origins:
            all_validation_failures.append(
                f"CORS parsing: Expected {expected_origins}, got {test_settings.cors_origins_list}"
            )
    except Exception as e:
        all_validation_failures.append(f"CORS parsing failed: {e}")

    # Test 4: AUTO_SEED can be true or false
    total_tests += 1
    try:
        test_settings_no_seed = Settings(
            host="0.0.0.0",
            port=8000,
            debug=False,
            cors_origins="http://example.com",
            api_v1_prefix="/api/v1",
            database_url="postgresql://user:pass@localhost/db",
            use_mock_data=False,
            auto_seed=False,
            window_size=300,
            activity_high_threshold=30,
            activity_medium_threshold=10,
            activity_low_threshold=1,
            concentration_warning_threshold=50,
            concentration_critical_threshold=70,
            top_contributors_limit=3,
            top_hotspots_limit=5,
        )
        if test_settings_no_seed.auto_seed != False:
            all_validation_failures.append(
                f"AUTO_SEED false: Expected False, got {test_settings_no_seed.auto_seed}"
            )
    except Exception as e:
        all_validation_failures.append(f"AUTO_SEED false test failed: {e}")

    # Test 5: All threshold values are required
    total_tests += 1
    try:
        test_settings = Settings(
            host="0.0.0.0",
            port=8000,
            debug=True,
            cors_origins="http://localhost:8080",
            api_v1_prefix="/api/v1",
            database_url="sqlite+aiosqlite:///test.db",
            use_mock_data=True,
            auto_seed=True,
            window_size=500,
            activity_high_threshold=45,
            activity_medium_threshold=15,
            activity_low_threshold=2,
            concentration_warning_threshold=55,
            concentration_critical_threshold=80,
            top_contributors_limit=5,
            top_hotspots_limit=8,
        )
        if test_settings.activity_high_threshold != 45:
            all_validation_failures.append(
                f"Activity high: Expected 45, got {test_settings.activity_high_threshold}"
            )
        if test_settings.top_contributors_limit != 5:
            all_validation_failures.append(
                f"Top contributors: Expected 5, got {test_settings.top_contributors_limit}"
            )
    except Exception as e:
        all_validation_failures.append(f"Threshold settings test failed: {e}")

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
