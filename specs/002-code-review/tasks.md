# Task List: Code Review & Refactoring for Maintainability

**Feature**: Code Review & Refactoring for Maintainability (002-code-review)
**Branch**: `002-code-review`
**Created**: 2025-12-14
**Plan**: [specs/002-code-review/plan.md](plan.md) | **Spec**: [specs/002-code-review/spec.md](spec.md) | **Research**: [specs/002-code-review/research.md](research.md)

---

## 🔴 CRITICAL REQUIREMENT - ALL TESTS MUST PASS

**FR-000 MANDATORY**: Every task completion MUST result in:
```bash
✅ uv run pytest tests/unit/ -v           # All PASS (< 5s)
✅ uv run pytest tests/integration/ -v    # All PASS
✅ uv run ruff check src/                 # Zero violations
✅ uv run mypy src/                       # Zero violations
```

**If ANY test fails** → Revert refactoring immediately and diagnose

---

## Implementation Strategy

This refactoring follows a **layered approach** with minimal risk:

1. **Create consolidation infrastructure first** (validation helper, router factory, etc.)
2. **Refactor modules one at a time** (can stop at any point)
3. **Run full test suite after EACH module refactoring**
4. **Commit frequently** (after each successful refactoring)

**MVP Scope**: Complete User Story 1 (Duplication Analysis Report) - can be done independently before any refactoring work

---

## Dependency Graph

```
Phase 1: Setup (Refactoring Infrastructure)
  ├── T001: Create ValidationHelper module
  ├── T002: Create CRUDRouterFactory function
  └── T003: Create DashboardTemplate component

Phase 2: Foundational (Setup Validation)
  └── T004: Validate all tests pass before refactoring starts

Phase 3: User Story 1 (P1) - Identify & Document Duplication
  ├── T005: Document validation helper consolidation approach
  ├── T006: Document router factory consolidation approach
  ├── T007: Document service builder consolidation approach
  └── T008: Document dashboard template consolidation approach
  → OUTPUT: Duplication analysis report (can be generated standalone)

Phase 4: User Story 4 (P2) - Refactor Validation Code
  ├── T009: [P] Refactor models/repository.py to use ValidationHelper
  ├── T010: [P] Refactor models/person.py to use ValidationHelper
  ├── T011: [P] Refactor models/analysis.py to use ValidationHelper
  ├── T012: [P] Refactor routers/repositories.py to use ValidationHelper
  ├── T013: [P] Refactor routers/people.py to use ValidationHelper
  ├── T014: [P] Refactor routers/analysis.py to use ValidationHelper
  ├── T015: [P] Refactor main.py to use ValidationHelper
  └── T016: [P] Refactor remaining __main__ blocks
  → After all: Commit validation consolidation

Phase 5: User Story 5 (P2) - Refactor Router Patterns
  ├── T017: Refactor routers/repositories.py to use CRUDRouterFactory
  ├── T018: Refactor routers/people.py to use CRUDRouterFactory
  ├── T019: Refactor routers/analysis.py to use CRUDRouterFactory
  └── T020: Add documentation for CRUDRouterFactory pattern
  → After all: Commit router factory consolidation

Phase 6: User Story 2 + 3 (P1) - Apply DRY & KISS Principles
  ├── T021: [P] Refactor service builders to use base class
  ├── T022: [P] Simplify complex service logic
  └── T023: Verify cyclomatic complexity reduction >= 20%
  → After all: Commit service simplification

Phase 7: User Story 6 (P3) - Refactor Dashboard Components
  ├── T024: Extract DashboardTemplate component
  ├── T025: Refactor RepositoryDashboard to use template
  ├── T026: Refactor PersonDashboard to use template
  └── T027: Add usage documentation
  → After all: Commit dashboard extraction

Phase 8: Polish & Documentation
  ├── T028: Update .claude/backend.md with new patterns
  ├── T029: Update .claude/frontend.md with new patterns
  ├── T030: Create quickstart.md with examples
  └── T031: Final validation and PR preparation
```

---

## Phase 1: Setup - Refactoring Infrastructure

> **Purpose**: Create shared modules and components that will consolidate duplicated code

### Setup Validation

- [ ] T001 Run baseline test suite to confirm all tests pass before refactoring `backend/tests/unit/` and `backend/tests/integration/`

---

## Phase 2: User Story 1 - Identify Code Duplication Patterns (P1)

> **User Story**: "I need to identify where code is being duplicated or where similar logic patterns exist"
> **Independent Test**: Generated duplication analysis report with patterns documented
> **Acceptance**: Report identifies all 4 patterns with concrete examples and consolidation strategies

### Analysis Tasks

- [ ] T002 [US1] Review and confirm ValidationHelper consolidation strategy in `backend/src/nexus_api/testing/` (from research.md)
- [ ] T003 [US1] Review and confirm CRUDRouterFactory consolidation strategy in `backend/src/nexus_api/routers/` (from research.md)
- [ ] T004 [US1] Review and confirm BaseService consolidation strategy in `backend/src/nexus_api/services/` (from research.md)
- [ ] T005 [US1] Review and confirm DashboardTemplate consolidation strategy in `frontend/src/components/` (from research.md)
- [ ] T006 [US1] Generate duplication analysis report documenting all patterns with locations and line counts

**Independent Test Criteria**:
- ✅ Report identifies 4 duplication patterns: validation blocks, routers, service builders, dashboard components
- ✅ Each pattern shows: affected files, line counts, consolidation approach, dependency analysis
- ✅ All concrete examples from actual code are documented
- ✅ Test impact assessment confirms no breaking changes

---

## Phase 3: User Story 4 - Refactor Validation Code `__main__` blocks (P2)

> **User Story**: "I need to consolidate 400+ lines of duplicated validation code"
> **Independent Test**: All refactored modules produce identical validation output, tests pass 100%
> **Acceptance**: 8+ files use ValidationHelper, each `__main__` block < 10 lines

### Validation Helper Setup

- [ ] T007 Create ValidationHelper module in `backend/src/nexus_api/testing/validation_helpers.py` with run() method and add_test() method

### Refactoring Validation Blocks (Parallelizable)

- [ ] T008 [P] [US4] Refactor `backend/src/nexus_api/models/repository.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/models/repository.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T009 [P] [US4] Refactor `backend/src/nexus_api/models/person.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/models/person.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T010 [P] [US4] Refactor `backend/src/nexus_api/models/analysis.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/models/analysis.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T011 [P] [US4] Refactor `backend/src/nexus_api/routers/repositories.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/routers/repositories.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T012 [P] [US4] Refactor `backend/src/nexus_api/routers/people.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/routers/people.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T013 [P] [US4] Refactor `backend/src/nexus_api/routers/analysis.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/routers/analysis.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T014 [P] [US4] Refactor `backend/src/nexus_api/main.py` __main__ block to use ValidationHelper
  - Test: `python backend/src/nexus_api/main.py` produces same output
  - Run full suite: `uv run pytest tests/`

- [ ] T015 [P] [US4] Refactor remaining `__main__` validation blocks (5+ other files) to use ValidationHelper
  - Test: Each module's `python module.py` produces identical output
  - Run full suite: `uv run pytest tests/`

### Validation Consolidation Completion

- [ ] T016 [US4] Commit validation helper refactoring with commit message: `refactor(validation): consolidate 400+ lines of __main__ blocks into ValidationHelper`
- [ ] T017 [US4] Verify all unit tests pass: `uv run pytest tests/unit/ -v` (< 5s)
- [ ] T018 [US4] Verify all integration tests pass: `uv run pytest tests/integration/ -v`

**Independent Test Criteria**:
- ✅ All 8+ modules use ValidationHelper (< 10 lines in `__main__` each)
- ✅ 100% of tests pass (unit + integration)
- ✅ Each module's `__main__` validation produces identical output to before
- ✅ 400-640 lines of duplication eliminated

---

## Phase 4: User Story 5 - Refactor Router Patterns (P2)

> **User Story**: "I need to eliminate duplication in FastAPI router patterns"
> **Independent Test**: Routers reduced by 30-40%, all endpoints respond identically, tests pass 100%
> **Acceptance**: Each router uses CRUDRouterFactory, boilerplate reduced by 30-40%

### Router Factory Setup

- [ ] T019 Create CRUDRouterFactory function in `backend/src/nexus_api/routers/factory.py` with support for GET, GET /{id}, POST operations

### Refactoring Routers (Sequential - dependency on factory)

- [ ] T020 [US5] Refactor `backend/src/nexus_api/routers/repositories.py` to use CRUDRouterFactory
  - Update router to use factory for standard endpoints
  - Maintain any custom endpoints (e.g., `GET /repositories/{repo_id}/metrics`)
  - Test: `uv run pytest tests/integration/test_repositories_router.py -v`
  - Run full suite: `uv run pytest tests/`

- [ ] T021 [US5] Refactor `backend/src/nexus_api/routers/people.py` to use CRUDRouterFactory
  - Update router to use factory for standard endpoints
  - Test: `uv run pytest tests/integration/test_people_router.py -v`
  - Run full suite: `uv run pytest tests/`

- [ ] T022 [US5] Refactor `backend/src/nexus_api/routers/analysis.py` to use CRUDRouterFactory
  - Update router to use factory for standard endpoints
  - Test: `uv run pytest tests/integration/test_analysis_router.py -v`
  - Run full suite: `uv run pytest tests/`

### Router Consolidation Completion

- [ ] T023 [US5] Commit router factory refactoring with commit message: `refactor(routers): consolidate CRUD patterns using CRUDRouterFactory reducing boilerplate by 30-40%`
- [ ] T024 [US5] Verify line count reduction: each router reduced by 30-40% (measure before/after)
- [ ] T025 [US5] Verify all API tests pass: `uv run pytest tests/integration/ -v`
- [ ] T026 [US5] Verify linting passes: `uv run ruff check backend/src/nexus_api/routers/`

**Independent Test Criteria**:
- ✅ All 3 routers use CRUDRouterFactory
- ✅ Each router reduced by 30-40% of code (~360 lines total eliminated)
- ✅ 100% of API tests pass (endpoints respond identically)
- ✅ No breaking changes to request/response contracts

---

## Phase 5: User Story 2 + 3 - Apply DRY & KISS Principles (P1)

> **User Story 2**: "I need to refactor identified duplication to follow DRY principles"
> **User Story 3**: "I need to simplify overly complex code sections"
> **Independent Test**: Code complexity reduced by 20%, all tests pass 100%, duplication reduced by 40%
> **Acceptance**: Service builders consolidated, simplified logic with clear intent

### Service Builder Consolidation

- [ ] T027 [P] [US2] Extract BaseService class in `backend/src/nexus_api/services/base_service.py` with _build_model() pattern
- [ ] T028 [P] [US2] Refactor `backend/src/nexus_api/services/repository_service.py` to inherit from BaseService
  - Test: `uv run pytest tests/unit/test_repository_service.py -v`
  - Run full suite: `uv run pytest tests/`

- [ ] T029 [P] [US2] Refactor `backend/src/nexus_api/services/person_service.py` to inherit from BaseService
  - Test: `uv run pytest tests/unit/test_person_service.py -v`
  - Run full suite: `uv run pytest tests/`

### Code Simplification

- [ ] T030 [US3] Identify and simplify overly complex sections in service layer (methods > 30 lines)
  - Create list of complex methods with cyclomatic complexity metrics
  - Simplify logic by removing unnecessary abstractions
  - Measure complexity reduction (target: >= 20%)

- [ ] T031 [US3] Refactor identified complex sections in `backend/src/nexus_api/services/` for clarity
  - Test: `uv run pytest tests/unit/ -v` confirms behavior unchanged

### DRY & KISS Consolidation Completion

- [ ] T032 [US2] Commit service consolidation with commit message: `refactor(services): consolidate builders into BaseService reducing duplication by 40%`
- [ ] T033 [US3] Commit code simplification with commit message: `refactor(services): simplify complex logic reducing cyclomatic complexity by 20%`
- [ ] T034 [US2] [US3] Verify complexity reduction: Document metrics before/after
- [ ] T035 [US2] [US3] Verify all unit tests pass: `uv run pytest tests/unit/ -v`

**Independent Test Criteria**:
- ✅ BaseService class eliminates 160-200 lines of builder pattern duplication
- ✅ Services inherit common behavior with no functional changes
- ✅ Cyclomatic complexity reduced by >= 20%
- ✅ 100% of unit tests pass
- ✅ Code is simpler and more maintainable (fewer lines per function)

---

## Phase 6: User Story 6 - Refactor Frontend Dashboard Components (P3)

> **User Story**: "I need to extract 40-50% duplicated code into reusable DashboardTemplate"
> **Independent Test**: Dashboard components reduced to ~100 lines each, visual behavior identical, tests pass
> **Acceptance**: DashboardTemplate<T> component created, dashboards use template

### Dashboard Template Extraction

- [ ] T036 Create DashboardTemplate component in `frontend/src/components/DashboardTemplate.tsx`
  - Generic `<T extends { id: string }>` type
  - Props: data[], isLoading, error, selectedId, onSelect, renderCard, renderDetails
  - Render: Grid layout with selection state, loading/error handling

### Dashboard Refactoring

- [ ] T037 [US6] Refactor `frontend/src/components/RepositoryDashboard.tsx` to use DashboardTemplate
  - Reduce from ~200+ lines to ~50-60 lines
  - Test: Visual output unchanged, selection behavior identical
  - Run: `pnpm lint` and visual smoke test in browser

- [ ] T038 [US6] Refactor `frontend/src/components/PersonDashboard.tsx` to use DashboardTemplate
  - Reduce from ~200+ lines to ~50-60 lines
  - Test: Visual output unchanged, selection behavior identical
  - Run: `pnpm lint` and visual smoke test in browser

### Dashboard Consolidation Completion

- [ ] T039 [US6] Commit dashboard extraction with commit message: `refactor(components): extract DashboardTemplate reducing dashboard boilerplate by 60%`
- [ ] T040 [US6] Verify line count reduction: each dashboard reduced from 200+ to ~50-60 lines
- [ ] T041 [US6] Verify frontend linting passes: `pnpm lint`
- [ ] T042 [US6] Visual regression test: Verify dashboards render identically in browser

**Independent Test Criteria**:
- ✅ DashboardTemplate<T> created as reusable component
- ✅ Both dashboards reduced to ~50-60 lines each (from 200+ lines)
- ✅ 60% boilerplate elimination per dashboard
- ✅ Visual output and behavior unchanged
- ✅ Frontend linting passes

---

## Phase 7: Polish & Documentation

> **Purpose**: Update development guides, create examples, prepare for PR

### Documentation Updates

- [ ] T043 Update `backend/.claude/backend.md` to document:
  - ValidationHelper module location and usage pattern
  - CRUDRouterFactory pattern with examples
  - BaseService inheritance pattern
  - New testing/ module structure

- [ ] T044 Update `frontend/.claude/frontend.md` to document:
  - DashboardTemplate<T> component with TypeScript generics example
  - Usage pattern for creating new dashboard types
  - Component composition pattern

- [ ] T045 Create `specs/002-code-review/data-model.md` documenting:
  - ValidationHelper class structure and methods
  - CRUDRouterFactory function signature
  - BaseService class inheritance
  - DashboardTemplate component interface

- [ ] T046 Create `specs/002-code-review/quickstart.md` with:
  - Example: Using ValidationHelper in a new module
  - Example: Creating a new CRUD router
  - Example: Creating a new dashboard component
  - Example: Running refactored code

### Final Validation

- [ ] T047 Run complete test battery:
  - `uv run pytest tests/unit/ -v` (all pass, < 5s)
  - `uv run pytest tests/integration/ -v` (all pass)
  - `uv run ruff check backend/src/` (zero violations)
  - `uv run mypy backend/src/` (zero violations)
  - `cd frontend && pnpm lint` (zero violations)

- [ ] T048 Generate refactoring summary report:
  - Lines of code eliminated (should be 1,200-1,500 total)
  - Cyclomatic complexity reduction (should be >= 20%)
  - Files refactored (should be 13-15)
  - Test pass rate (should be 100%)

- [ ] T049 Create PR with:
  - Summary of all refactoring changes
  - Reference to spec.md and plan.md
  - Test results confirmation
  - Before/after metrics
  - Links to refactored components

---

## Success Metrics

### Quantitative Targets (SC-001 through SC-008)

- **SC-001 (PRIMARY)**: ✅ 100% test pass rate maintained throughout
  - Unit tests: `uv run pytest tests/unit/ -v` < 5s all PASS
  - Integration tests: `uv run pytest tests/integration/ -v` all PASS
  - Linting: `uv run ruff check src/` zero violations
  - Type checking: `uv run mypy src/` zero violations

- **SC-002**: ✅ 40% code duplication reduction
  - Before: 1,200-1,500 lines of duplicated code
  - After: Measure actual reduction after refactoring

- **SC-003**: ✅ Validation helper consolidation
  - 8+ modules refactored to use ValidationHelper
  - Each `__main__` block < 10 lines (from 80-100 lines)
  - 400-640 lines eliminated

- **SC-004**: ✅ Router boilerplate reduction
  - 3 routers using CRUDRouterFactory
  - Each router reduced by 30-40%
  - ~360 lines eliminated

- **SC-005**: ✅ Test integrity (FR-000)
  - All tests pass before and after refactoring
  - No tests disabled or marked as "expected to fail"
  - Zero regressions

- **SC-006**: ✅ Code quality
  - Zero linting violations (Ruff)
  - Zero type check violations (mypy)
  - Zero style violations

- **SC-007**: ✅ Complexity reduction
  - Cyclomatic complexity reduced >= 20%
  - Service builders simplified
  - Code readability improved

- **SC-008**: ✅ Documentation
  - Commit messages document each refactoring
  - Pattern documentation in .claude/ files
  - Quickstart guide with examples

---

## Parallel Execution Examples

**Parallel Opportunity 1**: Validation block refactoring (T008-T015)
- Tasks T008 through T015 can run in parallel
- Each task refactors a different module
- All run full test suite, so serialize after first one succeeds
- Suggested execution: Do T008 sequentially, then T009-T015 can proceed independently

```bash
# Sequential approach (safer):
Task T008 → verify tests pass → commit
Task T009 → verify tests pass → commit
Task T010 → verify tests pass → commit
# ... continue for T011-T015

# OR Parallel approach (after first success):
Task T008 (sequential first)
Then: T009, T010, T011, T012, T013, T014, T015 (each with own test verification, then sync)
```

**Parallel Opportunity 2**: Service refactoring (T027-T029)
- Tasks T027 and T028-T029 have dependency on T027
- T027 creates BaseService, then T028-T029 can proceed independently
- Suggested execution: T027 → then T028 and T029 in parallel

**Parallel Opportunity 3**: Dashboard refactoring (T037-T038)
- T036 creates DashboardTemplate
- T037 and T038 are independent (different files, no cross-dependencies)
- Suggested execution: T036 → then T037 and T038 in parallel

---

## Task Totals

| Phase | User Story | Count | Duration Estimate |
|-------|-----------|-------|-------------------|
| 1 | Setup | 1 | < 5 min |
| 2 | US1 (P1) | 5 | < 30 min |
| 3 | US4 (P2) | 17 | 2-3 hours |
| 4 | US5 (P2) | 8 | 1-2 hours |
| 5 | US2+3 (P1) | 9 | 2-3 hours |
| 6 | US6 (P3) | 7 | 1-2 hours |
| 7 | Polish | 7 | 1 hour |
| **TOTAL** | | **54** | **7-11 hours** |

**MVP Scope** (US1 only):
- Tasks: T001-T006 (6 tasks)
- Time: < 30 minutes
- Output: Duplication analysis report
- Can be delivered independently before any refactoring work
