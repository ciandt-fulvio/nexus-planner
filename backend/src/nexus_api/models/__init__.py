"""
Shared models for Nexus API.

Contains base models used across multiple domains.

Docs: https://docs.pydantic.dev/latest/

Sample input: Alert data with type and message
Expected output: Validated Alert model instance
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class AlertType(str, Enum):
    """Alert severity levels."""

    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


class Alert(BaseModel):
    """Risk/informational indicator used by Repository and Person."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    type: AlertType
    message: str


if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: Valid Alert creation
    total_tests += 1
    try:
        alert = Alert(type=AlertType.WARNING, message="Test warning")
        if alert.type != AlertType.WARNING:
            all_validation_failures.append(
                f"Alert type: Expected AlertType.WARNING, got {alert.type}"
            )
        if alert.message != "Test warning":
            all_validation_failures.append(
                f"Alert message: Expected 'Test warning', got '{alert.message}'"
            )
    except Exception as e:
        all_validation_failures.append(f"Alert creation failed: {e}")

    # Test 2: AlertType enum values
    total_tests += 1
    try:
        expected_values = {"warning", "danger", "info"}
        actual_values = {t.value for t in AlertType}
        if actual_values != expected_values:
            all_validation_failures.append(
                f"AlertType values: Expected {expected_values}, got {actual_values}"
            )
    except Exception as e:
        all_validation_failures.append(f"AlertType enum test failed: {e}")

    # Test 3: Alert with string type (auto-conversion)
    total_tests += 1
    try:
        alert = Alert(type="danger", message="Critical issue")
        if alert.type != AlertType.DANGER:
            all_validation_failures.append(
                f"Alert type from string: Expected AlertType.DANGER, got {alert.type}"
            )
    except Exception as e:
        all_validation_failures.append(f"Alert string type test failed: {e}")

    # Test 4: Invalid alert type rejected
    total_tests += 1
    try:
        Alert(type="invalid", message="Test")
        all_validation_failures.append(
            "Invalid alert type: Expected validation error, but none raised"
        )
    except ValueError:
        pass  # Expected
    except Exception as e:
        all_validation_failures.append(
            f"Invalid alert type test: Unexpected error {type(e).__name__}"
        )

    # Test 5: Extra fields rejected
    total_tests += 1
    try:
        Alert(type="warning", message="Test", extra_field="should fail")
        all_validation_failures.append("Extra fields: Expected validation error, but none raised")
    except ValueError:
        pass  # Expected
    except Exception as e:
        all_validation_failures.append(f"Extra fields test: Unexpected error {type(e).__name__}")

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
