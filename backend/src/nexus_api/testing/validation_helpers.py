"""
Validation helpers for module-level __main__ block testing.

Consolidates duplicated validation logic from 8+ modules into a single reusable class.

Sample input: Test functions with expected values
Expected output: Validation report with pass/fail status and exit code

Before (80-100 lines per module):
    if __name__ == "__main__":
        import sys
        all_validation_failures = []
        total_tests = 0
        # ... repetitive validation logic ...

After (5-10 lines per module):
    if __name__ == "__main__":
        from nexus_api.testing.validation_helpers import ValidationHelper
        validator = ValidationHelper()
        validator.add_test("test_name", lambda: function_call(), expected_value)
        sys.exit(validator.run())
"""

from typing import Any, Callable


class ValidationHelper:
    """Consolidates __main__ validation logic from 8+ modules."""

    def __init__(self) -> None:
        """Initialize validation helper with empty test list."""
        self.tests: list[tuple[str, Callable[[], Any], Any]] = []
        self.failures: list[str] = []
        self.total_tests = 0

    def add_test(
        self, name: str, test_func: Callable[[], Any], expected: Any
    ) -> None:
        """
        Register a test case.

        Args:
            name: Descriptive test name
            test_func: Callable that returns a result to validate
            expected: Expected result value
        """
        self.tests.append((name, test_func, expected))

    def run(self) -> int:
        """
        Execute all tests and return exit code.

        Returns:
            0 if all tests pass, 1 if any test fails

        Prints validation results in consistent format:
            ✅ VALIDATION PASSED - All N tests successful
            OR
            ❌ VALIDATION FAILED - M of N tests failed:
              - test_name: Expected X, got Y
        """
        self.total_tests = len(self.tests)
        for name, test_func, expected in self.tests:
            try:
                result = test_func()
                if result != expected:
                    self.failures.append(
                        f"{name}: Expected {expected}, got {result}"
                    )
            except Exception as e:
                self.failures.append(f"{name}: {type(e).__name__}: {e}")

        return self._print_results()

    def _print_results(self) -> int:
        """
        Print validation results in consistent format.

        Returns:
            0 if all tests pass, 1 if any test fails
        """
        if self.failures:
            print(
                f"❌ VALIDATION FAILED - {len(self.failures)}/{self.total_tests} tests failed:"
            )
            for failure in self.failures:
                print(f"  - {failure}")
            return 1
        else:
            print(
                f"✅ VALIDATION PASSED - All {self.total_tests} tests successful"
            )
            return 0


if __name__ == "__main__":
    import sys

    # Self-validation: Test the ValidationHelper itself
    validator = ValidationHelper()

    # Test 1: Simple equality test (should pass)
    validator.add_test("simple_equality", lambda: 1 + 1, 2)

    # Test 2: String test (should pass)
    validator.add_test("string_test", lambda: "hello".upper(), "HELLO")

    # Test 3: List test (should pass)
    validator.add_test("list_test", lambda: [1, 2, 3], [1, 2, 3])

    # Test 4: Function test (should pass)
    validator.add_test("function_test", lambda: len([1, 2, 3]), 3)

    # Run all tests
    sys.exit(validator.run())
