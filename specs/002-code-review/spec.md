# Feature Specification: Code Review & Refactoring for Maintainability

**Feature Branch**: `002-code-review`
**Created**: 2025-12-14
**Status**: Draft
**Input**: User description: "faca uma verificaçao de código e indique pontos que parecem estar duplicando código ou lógica. Use conceitos com o D.R.Y e o K.I.S.S. para garantir um código de mais fácil manutenabilidade"

---

## User Scenarios & Testing

### User Story 1 - Identify Code Duplication Patterns (Priority: P1)

As a developer maintaining the Nexus Planner codebase, I need to identify where code is being duplicated or where similar logic patterns exist, so that I can prioritize refactoring efforts and improve code maintainability.

**Why this priority**: Identifying duplication is the foundation for all subsequent refactoring work. Without a comprehensive map of where code is repeated, we cannot make informed decisions about which refactoring will deliver the most value.

**Independent Test**: Can be fully tested by running a static analysis scan across the codebase and producing a report documenting all identified duplication patterns, organized by impact level and affected files.

**Acceptance Scenarios**:

1. **Given** the complete codebase (backend Python + frontend TypeScript), **When** analyzing for code duplication, **Then** a report identifies all duplicate code blocks, similar patterns, and repeated logic with location references (file:line)
2. **Given** duplicate code blocks, **When** prioritizing, **Then** they are categorized by impact level (P1: High Risk, P2: Medium Risk, P3: Low Risk) based on maintainability impact
3. **Given** identified patterns, **When** reviewing duplicated sections, **Then** the report shows concrete code examples and explains why they represent duplication

---

### User Story 2 - Apply DRY (Don't Repeat Yourself) Principle (Priority: P1)

As a developer, I need to refactor the identified duplication to follow DRY principles, so that changes to business logic only need to be made in one place.

**Why this priority**: The DRY principle directly prevents bugs caused by inconsistent updates across multiple locations. This is critical for code quality and maintenance cost reduction.

**Independent Test**: Can be fully tested by verifying that refactored code achieves the same functionality as the original, reduces lines of duplicated code by at least 40%, and maintains all existing test coverage.

**Acceptance Scenarios**:

1. **Given** code with identified duplication, **When** applying DRY refactoring, **Then** similar logic is consolidated into shared functions, classes, or templates
2. **Given** consolidated code, **When** running the test suite, **Then** all tests pass and behavior is identical to the pre-refactored version
3. **Given** a change to shared logic, **When** updating once, **Then** the change automatically applies to all locations that use that logic

---

### User Story 3 - Apply KISS (Keep It Simple, Stupid) Principle (Priority: P1)

As a developer, I need to simplify overly complex code sections, so that the codebase is easier to understand and maintain without sacrificing functionality.

**Why this priority**: Complex code is harder to maintain and more prone to bugs. Simplifying the code reduces cognitive load and makes future maintenance cheaper.

**Independent Test**: Can be fully tested by verifying that simplified code is still functionally correct, requires less cognitive effort to understand (measured by cyclomatic complexity or code readability metrics), and has fewer lines.

**Acceptance Scenarios**:

1. **Given** complex code sections identified during review, **When** applying KISS principle, **Then** unnecessary abstractions are removed and code is simplified to the minimum required for the feature
2. **Given** simplified code, **When** reviewing, **Then** the code logic is clear and understandable without extensive comments
3. **Given** simplified sections, **When** running tests, **Then** all tests pass with identical behavior

---

### User Story 4 - Refactor Validation Code (`__main__` blocks) (Priority: P2)

As a developer, I need to consolidate the 400+ lines of duplicated validation code currently in multiple `__main__` blocks, so that validation logic is consistent, centralized, and easier to maintain.

**Why this priority**: This is the highest-impact duplication opportunity (400-640 lines of near-identical code across 8+ files). Consolidating this saves significant maintenance effort and prevents inconsistencies.

**Independent Test**: Can be fully tested by creating a pytest-compatible validation helper module that eliminates duplication in `__main__` blocks and produces the same validation output.

**Acceptance Scenarios**:

1. **Given** 8+ files with duplicated `__main__` validation code, **When** consolidating into a shared helper, **Then** each file's `__main__` block uses the helper instead of repeating 50-80 lines of code
2. **Given** consolidated validation, **When** running any module's `__main__`, **Then** it produces the same formatted output (PASS/FAIL with test counts) as before
3. **Given** the validation helper, **When** using it in any module, **Then** adding new tests requires minimal boilerplate

---

### User Story 5 - Refactor Router Patterns (Priority: P2)

As a backend developer, I need to eliminate duplication in FastAPI router patterns across `repositories.py`, `people.py`, and `analysis.py`, so that adding new endpoints requires less boilerplate and router logic is more maintainable.

**Why this priority**: Router duplication (40-50% similar code across 3 routers) impacts developer velocity when adding features. Consolidating these patterns enables faster feature development.

**Independent Test**: Can be fully tested by verifying that a factory or base class approach reduces each router by 30-40% of boilerplate while maintaining identical API contracts and behavior.

**Acceptance Scenarios**:

1. **Given** 3 routers with similar CRUD patterns, **When** applying a factory or base class, **Then** each router is reduced by 30-40% of code while maintaining identical endpoint behavior
2. **Given** refactored routers, **When** running API tests, **Then** all endpoints respond identically to pre-refactored versions
3. **Given** the new router factory/base class, **When** adding a new router, **Then** boilerplate code is reduced by at least 50% compared to copying an existing router

---

### User Story 6 - Refactor Frontend Dashboard Components (Priority: P3)

As a frontend developer, I need to extract the 40-50% duplicated code from `RepositoryDashboard` and `PersonDashboard` into a reusable `DashboardTemplate` component, so that adding new dashboards is faster and dashboard logic is consistent.

**Why this priority**: While this is valuable for future feature development, it's less critical than backend refactoring. It can be implemented after higher-priority items without blocking functionality.

**Independent Test**: Can be fully tested by creating a `DashboardTemplate<T>` component that reduces both dashboard components to 100 lines each (from current 200+ lines) while maintaining identical visual behavior.

**Acceptance Scenarios**:

1. **Given** `RepositoryDashboard.tsx` and `PersonDashboard.tsx` with 40-50% duplicated logic, **When** extracting a reusable template, **Then** both components are reduced to ~100 lines each (from ~200+ lines)
2. **Given** the `DashboardTemplate` component, **When** using it in the existing dashboards, **Then** visual output and behavior are identical to the original implementation
3. **Given** the template, **When** adding a new dashboard type, **Then** creating the dashboard requires only 30-50 lines of code

---

### Edge Cases

- What happens when a module contains both class definitions and functions in its `__main__` validation block? (Complex multi-entity validation)
- How should validation be structured for modules with interdependent test cases that must run in sequence?
- How do we handle modules where the validation setup requires database initialization or external resources?
- Should the refactored code maintain backward compatibility with existing `__main__` invocations, or is it safe to change the interface?

---

## Requirements

### Functional Requirements

- **FR-000** ⭐ **MANDATORY**: System MUST verify that 100% of all unit, integration, and contract tests pass after each refactoring. If ANY test fails, the refactoring is considered FAILED and must be reverted or fixed immediately. This requirement takes absolute priority over all other requirements.
  - Backend unit tests MUST pass: `uv run pytest tests/unit/ -v`
  - Backend integration tests MUST pass: `uv run pytest tests/integration/ -v`
  - All linting MUST pass: `uv run ruff check src/` and `uv run mypy src/`
  - No test can be disabled, skipped, or marked as "expected to fail" to make the build pass

- **FR-001**: System MUST identify and document all code duplication patterns in the Python backend (models, services, routers) and TypeScript frontend (components, services)

- **FR-002**: System MUST categorize identified duplication by impact level (High/Medium/Low Risk) based on maintenance cost and frequency of change

- **FR-003**: System MUST provide concrete code examples for each duplication pattern, including file paths and line numbers

- **FR-004**: System MUST document a consolidation strategy for each duplication pattern that applies DRY principles

- **FR-005**: System MUST refactor Backend `__main__` validation blocks (8+ files, 400-640 lines) into a reusable pytest-compatible helper

- **FR-006**: System MUST refactor FastAPI routers (repositories.py, people.py, analysis.py) to eliminate 40-50% duplicated CRUD patterns

- **FR-007**: System MUST refactor Backend service builders to use inheritance or factory patterns instead of repeating 80-100 line build methods

- **FR-008**: System MUST refactor Frontend dashboard components to extract 40-50% duplicated logic into a reusable `DashboardTemplate<T>` component

- **FR-009**: System MUST ensure all refactoring preserves existing functionality (verified by FR-000 test pass requirement)

- **FR-010**: System MUST maintain API contracts (request/response models) unchanged during backend refactoring

- **FR-011**: System MUST ensure all refactored code follows project style guidelines (Python 3.13+, TypeScript conventions, PEP 8/Ruff, Black formatting)

- **FR-012**: System MUST document all refactoring changes with clear commit messages following the project's convention (feat:, refactor:, test:)

### Key Entities

- **Code Duplication Pattern**: A section of code that appears multiple times with minimal variation. Characterized by: type (validation logic, CRUD endpoints, component logic), impact level, location(s), duplicate lines count
- **Consolidation Strategy**: A planned refactoring approach (function extraction, class inheritance, factory pattern, component composition) that eliminates a specific duplication pattern
- **Refactored Module**: A file or component where duplication has been eliminated and consolidated code has been applied
- **Test Coverage**: The set of existing tests that must pass after refactoring to verify behavior preservation

---

## Success Criteria

### ⚠️ CRITICAL: Test Pass Rate is Non-Negotiable

**MANDATORY REQUIREMENT**: All refactoring work MUST NOT break any tests. If ANY test fails after refactoring, the refactoring is considered FAILED and must be reverted or fixed immediately.

- **All unit tests MUST pass** (backend: `pytest tests/unit/`, run time: < 5s)
- **All integration tests MUST pass** (backend: `pytest tests/integration/`)
- **All API contract tests MUST pass** (endpoint responses match specification)
- **Frontend tests MUST pass** (when implemented: `pnpm test`)

This is the PRIMARY success criterion. Refactoring work that reduces duplication but breaks tests is **not acceptable**. Only after 100% test pass rate is achieved can other success criteria be evaluated.

---

### Measurable Outcomes

- **SC-001** ⭐ **PRIMARY - Test Integrity**: Maintain 100% test pass rate across all unit and integration tests. ALL tests in both backend and frontend must pass without any failures, warnings, or deprecations (Completion metric: Test suite run completes with 0 failures)
  - Backend unit tests: `uv run pytest tests/unit/ -v` → All PASS
  - Backend integration tests: `uv run pytest tests/integration/ -v` → All PASS
  - Linting/type checks: `uv run mypy src/` and `uv run ruff check src/` → Zero violations
  - Frontend linting: `pnpm lint` → Zero violations

- **SC-002**: Code Review Report: Comprehensive documentation of all duplication patterns identified, categorized by impact level, with concrete code examples (Completion metric: Report generated and approved)

- **SC-003**: DRY Application: Reduce duplicate code by at least 40% in identified patterns through consolidation strategies (Completion metric: Line count reduction verified by comparing pre/post refactoring)

- **SC-004**: Validation Helper: Consolidate 400-640 lines of `__main__` duplication into a single pytest-compatible helper module (Completion metric: All 8+ affected files use helper with < 10 lines in each `__main__` block)

- **SC-005**: Router Refactoring: Reduce router boilerplate by 30-40% through factory or base class implementation (Completion metric: Each router uses factory/base class, line count reduction verified)

- **SC-006**: Code Quality: All refactored code passes linting (Ruff), type checking (mypy), and style checks without warnings (Completion metric: Zero linting/type check violations after refactoring)

- **SC-007**: Maintainability: Cyclomatic complexity of refactored modules is reduced by at least 20% (Completion metric: Complexity metrics before/after comparison shows improvement)

- **SC-008**: Documentation: All refactoring changes are documented with clear commit messages and optional inline documentation for complex patterns (Completion metric: Commit history explains refactoring rationale and impact on tests)

---

## Assumptions

1. ⚠️ **TEST PASS RATE IS MANDATORY**: Every refactoring change MUST result in 100% test pass rate. If tests fail, the change must be reverted immediately. This is non-negotiable and takes precedence over all other concerns.

2. **Test Suite Completeness**: Existing test suite provides sufficient coverage to catch regressions during refactoring. All critical paths and edge cases are covered.

3. **Code Stability**: No concurrent changes to the codebase that would conflict with refactoring efforts. The codebase will remain stable during refactoring.

4. **API Contract Stability**: API field names and structure should not change during backend refactoring (use Pydantic aliases if needed to maintain contract).

5. **Tool Availability**: Linting tools (Ruff), type checkers (mypy), and test runners (pytest) are configured and working correctly in the environment.

6. **No Breaking Changes Required**: Refactoring should preserve all external APIs and user-facing behavior without backward compatibility breaks.

7. **Validation Testing Approach**: It's acceptable to replace the current `__main__` validation blocks with pytest-compatible helpers while maintaining test semantics.

---

## Dependencies & Constraints

### External Dependencies
- **Pytest**: Required for the new validation helper module
- **Existing Test Suite**: Tests must pass after refactoring to verify correctness

### Architectural Constraints
- Backend must maintain FastAPI router interface compatibility
- Frontend must maintain React component props interface (unless explicitly breaking change)
- All changes must be backward compatible with existing code that imports from refactored modules

### Quality Constraints
- No refactoring should reduce test coverage
- All code must pass project style checks (Ruff, Black-compatible formatting)
- No dead code or unreachable branches introduced during refactoring

---

## Success Story Example

**Current State**: `backend/src/nexus_api/models/repository.py` contains 80-100 lines of `__main__` validation code that is nearly identical to the same code in `models/person.py`, `models/analysis.py`, and 5 other files. This represents 400-640 lines of duplicated validation infrastructure.

**After Refactoring**:
- New module `backend/src/nexus_api/testing/validation_helpers.py` contains a reusable `ValidationHelper` class
- Each model's `__main__` block is reduced to ~5 lines:
  ```python
  if __name__ == "__main__":
      from src.nexus_api.testing.validation_helpers import ValidationHelper
      validator = ValidationHelper([
          ("test_name", lambda: test_func(), expected_result),
      ])
      validator.run()
  ```
- All 8+ modules use this helper
- Test output is consistent and reliable across all modules
- Adding new validation tests to any module requires only 1-2 lines of code

**Impact**:
- 400+ lines of duplicated code eliminated
- Maintenance burden reduced (changes to validation format in one place)
- DRY principle applied successfully
- Code is simpler (KISS principle applied)
