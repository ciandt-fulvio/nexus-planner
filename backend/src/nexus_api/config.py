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

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Helper function to create default settings
    def create_settings(**overrides):
        defaults = {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": True,
            "cors_origins": "http://localhost:8080",
            "api_v1_prefix": "/api/v1",
            "database_url": "sqlite+aiosqlite:///test.db",
            "use_mock_data": True,
            "auto_seed": True,
            "window_size": 300,
            "activity_high_threshold": 30,
            "activity_medium_threshold": 10,
            "activity_low_threshold": 1,
            "concentration_warning_threshold": 50,
            "concentration_critical_threshold": 70,
            "top_contributors_limit": 3,
            "top_hotspots_limit": 5,
        }
        defaults.update(overrides)
        return Settings(**defaults)

    # Test 1: Basic settings load correctly
    validator.add_test(
        "Settings host",
        lambda: (s := create_settings(), s.host)[1],
        "0.0.0.0",
    )

    # Test 2: Port is correct type
    validator.add_test(
        "Settings port",
        lambda: (s := create_settings(), s.port)[1],
        8000,
    )

    # Test 3: Debug flag works
    validator.add_test(
        "Settings debug",
        lambda: (s := create_settings(), s.debug)[1],
        True,
    )

    # Test 4: USE_MOCK_DATA=false works
    validator.add_test(
        "USE_MOCK_DATA false",
        lambda: (s := create_settings(use_mock_data=False), s.use_mock_data)[1],
        False,
    )

    # Test 5: CORS origins parsing
    validator.add_test(
        "CORS origins parsing",
        lambda: (
            s := create_settings(cors_origins="http://localhost:3000,http://localhost:8080"),
            s.cors_origins_list,
        )[1],
        ["http://localhost:3000", "http://localhost:8080"],
    )

    # Test 6: AUTO_SEED=false works
    validator.add_test(
        "AUTO_SEED false",
        lambda: (s := create_settings(auto_seed=False), s.auto_seed)[1],
        False,
    )

    # Test 7: Custom threshold values
    validator.add_test(
        "Activity high threshold",
        lambda: (s := create_settings(activity_high_threshold=45), s.activity_high_threshold)[1],
        45,
    )

    # Test 8: Top contributors limit
    validator.add_test(
        "Top contributors limit",
        lambda: (s := create_settings(top_contributors_limit=5), s.top_contributors_limit)[1],
        5,
    )

    sys.exit(validator.run())
