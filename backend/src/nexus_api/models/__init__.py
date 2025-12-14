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

    from nexus_api.testing.validation_helpers import ValidationHelper

    validator = ValidationHelper()

    # Test 1: Alert type is correct
    validator.add_test(
        "Alert type",
        lambda: (alert := Alert(type=AlertType.WARNING, message="Test warning"), alert.type)[1],
        AlertType.WARNING,
    )

    # Test 2: Alert message is correct
    validator.add_test(
        "Alert message",
        lambda: (alert := Alert(type=AlertType.WARNING, message="Test warning"), alert.message)[1],
        "Test warning",
    )

    # Test 3: AlertType enum values
    validator.add_test(
        "AlertType values",
        lambda: {t.value for t in AlertType},
        {"warning", "danger", "info"},
    )

    # Test 4: Alert with string type (auto-conversion)
    validator.add_test(
        "Alert type from string",
        lambda: (alert := Alert(type="danger", message="Critical issue"), alert.type)[1],
        AlertType.DANGER,
    )

    # Test 5: Invalid alert type rejected
    def test_invalid_type():
        try:
            Alert(type="invalid", message="Test")
            return False  # Should have raised ValueError
        except ValueError:
            return True  # Expected

    validator.add_test("Invalid alert type rejected", test_invalid_type, True)

    # Test 6: Extra fields rejected
    def test_extra_fields():
        try:
            Alert(type="warning", message="Test", extra_field="should fail")
            return False  # Should have raised ValueError
        except ValueError:
            return True  # Expected

    validator.add_test("Extra fields rejected", test_extra_fields, True)

    sys.exit(validator.run())
