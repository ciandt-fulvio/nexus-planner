"""
Configuration module for Nexus API.

Uses pydantic-settings for type-safe configuration from environment variables.
Docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

Sample input: Environment variables in backend/.env
Expected output: Settings instance with validated configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS Configuration
    cors_origins: str = "http://localhost:8080"

    # API Configuration
    api_v1_prefix: str = "/api/v1"

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

    # Test 1: Settings load with defaults
    total_tests += 1
    try:
        test_settings = Settings()
        if test_settings.host != "0.0.0.0":
            all_validation_failures.append(
                f"Default host: Expected '0.0.0.0', got '{test_settings.host}'"
            )
        if test_settings.port != 8000:
            all_validation_failures.append(f"Default port: Expected 8000, got {test_settings.port}")
    except Exception as e:
        all_validation_failures.append(f"Settings load failed: {e}")

    # Test 2: CORS origins parsing
    total_tests += 1
    try:
        test_settings = Settings(cors_origins="http://localhost:3000,http://localhost:8080")
        expected_origins = ["http://localhost:3000", "http://localhost:8080"]
        if test_settings.cors_origins_list != expected_origins:
            all_validation_failures.append(
                f"CORS parsing: Expected {expected_origins}, got {test_settings.cors_origins_list}"
            )
    except Exception as e:
        all_validation_failures.append(f"CORS parsing failed: {e}")

    # Test 3: API prefix default
    total_tests += 1
    try:
        test_settings = Settings()
        if test_settings.api_v1_prefix != "/api/v1":
            all_validation_failures.append(
                f"API prefix: Expected '/api/v1', got '{test_settings.api_v1_prefix}'"
            )
    except Exception as e:
        all_validation_failures.append(f"API prefix test failed: {e}")

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
