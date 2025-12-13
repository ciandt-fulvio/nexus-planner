"""
Services layer for Nexus API.

This package contains business logic and data processing services.
Services are responsible for:
- Calculating metrics (activity, concentration, expertise)
- Orchestrating database operations
- Converting between ORM tables and Pydantic models

Services are pure functions where possible, making them easy to test.
"""

from nexus_api.services import (
    alert_service,
    commit_service,
    person_service,
    repository_service,
)

__all__ = ["alert_service", "commit_service", "person_service", "repository_service"]
