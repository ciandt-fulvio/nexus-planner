# Implementation Plan: Code Review & Refactoring for Maintainability

**Branch**: `002-code-review` | **Date**: 2025-12-14 | **Spec**: [specs/002-code-review/spec.md](spec.md)
**Input**: Feature specification from `/specs/002-code-review/spec.md`

**Note**: This is a refactoring feature (not new feature development). Focus is on code consolidation, DRY/KISS principles, and maintaining 100% test pass rate throughout.

## Summary

Analyze the Nexus Planner codebase to identify code duplication patterns and refactor following DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles. Primary goals:

1. **Identify & Document**: All duplication patterns (400-640 lines in `__main__` blocks, 40-50% similar CRUD routers, 40-50% duplicate dashboard components)
2. **Apply DRY**: Consolidate validation helpers, create router factories, extract dashboard templates
3. **Apply KISS**: Simplify overly complex sections to reduce cognitive load
4. **Maintain Quality**: 100% test pass rate is the PRIMARY criterion (FR-000, SC-001)

This is NOT a new feature - it's code refactoring to improve maintainability. Testing existing functionality must pass before and after every change.

## Technical Context

**Language/Version**: Python 3.13+ (backend) + TypeScript 5.5+ (frontend)
**Primary Dependencies**:
  - Backend: FastAPI 0.109+, SQLAlchemy 2.0+, Pydantic 2.5+, pytest (testing)
  - Frontend: React 18.3+, TanStack Query 5.56+, TypeScript, shadcn/ui (for components)
**Storage**: SQLite (async via aiosqlite) - N/A for refactoring
**Testing**: pytest (backend unit & integration), existing test suite MUST maintain 100% pass rate
**Target Platform**: Web application (Python backend + React frontend)
**Project Type**: Full-stack web (backend: Python FastAPI, frontend: React + TypeScript)
**Performance Goals**: N/A for refactoring (maintain current performance, don't degrade)
**Constraints**:
  - NO breaking changes to APIs or component interfaces
  - ALL existing tests MUST pass after each refactoring change
  - Files must remain under 500 lines (except TSX/HTML up to 1000 lines)
  - Code must follow PEP 8 (Ruff) and project style guidelines
**Scale/Scope**:
  - Backend: ~4,866 lines across 40+ files, 8+ files with duplicated `__main__` validation
  - Frontend: 60+ React components, 2 dashboards with 40-50% code duplication
  - Refactoring affects 13-15 files total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

- [x] **Principle I: Test-First (TDD/BDD)** - ✅ SPECIAL CASE: Refactoring feature. Tests already exist for all current functionality. NO TESTS WILL BE MODIFIED/BROKEN - FR-000 makes 100% test pass rate THE PRIMARY CRITERION. Tests verify behavior BEFORE refactoring and AFTER refactoring must be identical.

- [x] **Principle II: Fast Test Battery** - ✅ Existing fast battery (unit tests) must continue to pass: `uv run pytest tests/unit/` (< 5s). All refactoring commits must pass this.

- [x] **Principle III: Complete Test Battery** - ✅ CRITICAL: All tests (unit + integration) MUST pass before PR. This feature's success is 100% defined by test pass rate (SC-001 PRIMARY). No refactoring is accepted if ANY test fails.

- [x] **Principle IV: Frequent Commits** - ✅ Commit strategy: after each refactoring pattern consolidation, after each file refactoring, at each duplication elimination milestone. Message format: `refactor(component): consolidate [pattern] reducing [X] lines`

- [x] **Principle V: Simplicity** - ✅ Refactoring GOAL is simplicity (DRY + KISS). Justification: consolidated code is inherently simpler and more maintainable than duplicated code. No unnecessary complexity introduced.

**Status**: ✅ COMPLIANT - All Constitution principles explicitly addressed

## Project Structure

### Documentation (this feature)

```text
specs/002-code-review/
├── plan.md                  # This file (phase planning)
├── spec.md                  # Feature specification with user stories
├── checklists/
│   └── requirements.md      # Specification quality validation
├── research.md              # Phase 0: Analysis of duplication patterns (TO BE GENERATED)
├── data-model.md            # Phase 1: Refactoring data model (TO BE GENERATED)
├── quickstart.md            # Phase 1: Usage guide for refactored code (TO BE GENERATED)
├── contracts/               # Phase 1: API contracts (N/A - refactoring doesn't change contracts)
└── tasks.md                 # Phase 2: Actionable refactoring tasks (TO BE GENERATED)
```

### Source Code (Web application - Backend + Frontend)

**BACKEND** - Files affected by refactoring:
```text
backend/src/nexus_api/
├── models/
│   ├── repository.py        # Contains duplicated __main__ validation (80-100 lines)
│   ├── person.py            # Contains duplicated __main__ validation
│   ├── analysis.py          # Contains duplicated __main__ validation
│   └── ...                  # 5+ other files with same pattern
├── routers/
│   ├── repositories.py      # 40-50% duplicated CRUD patterns
│   ├── people.py            # 40-50% duplicated CRUD patterns
│   ├── analysis.py          # 40-50% duplicated CRUD patterns
│   └── ...
├── services/
│   ├── repository_service.py  # 80-100 line builder methods
│   ├── person_service.py      # 80-100 line builder methods
│   └── ...
└── testing/
    └── validation_helpers.py # NEW: Consolidated validation helper module

backend/tests/
├── unit/                    # MUST pass: uv run pytest tests/unit/ -v (< 5s)
└── integration/             # MUST pass: uv run pytest tests/integration/ -v
```

**FRONTEND** - Files affected by refactoring:
```text
frontend/src/
├── components/
│   ├── RepositoryDashboard.tsx    # 200+ lines, 40-50% duplicated
│   ├── PersonDashboard.tsx        # 200+ lines, 40-50% duplicated
│   └── DashboardTemplate.tsx      # NEW: Reusable template component
└── services/
    └── [API services - NO changes expected to contracts]
```

**Structure Decision**: Web application (backend: Python FastAPI, frontend: React). Refactoring is in-place optimization of existing code, no new architectural layers.

## Complexity Tracking

> **NOT APPLICABLE** - Constitution Check fully compliant. Refactoring REDUCES complexity (that's the goal). No violations to justify.

**Note**: Refactoring work intentionally aims to reduce cyclomatic complexity by 20% (SC-007) and eliminate duplication (SC-002). Any complexity increase would violate the purpose of this work.

---

## Phase 0: Code Analysis & Research

**Goal**: Analyze existing code to confirm identified duplication patterns and document consolidation approaches.

**RESEARCH REQUIRED - NONE**: Spec already identified all duplication patterns based on code review:
- ✅ `__main__` validation blocks: 8+ files, 400-640 lines duplicated, FR-005
- ✅ FastAPI routers: 3 routers, 40-50% similarity, FR-006
- ✅ Service builders: 80-100 line methods, similar patterns, FR-007
- ✅ Dashboard components: 40-50% duplication, FR-008

**Phase 0 Deliverable**: `research.md` documenting:
1. Code duplication analysis summary (confirmed patterns from spec)
2. Refactoring approach for each pattern (validation helpers, factory patterns, component extraction)
3. Dependency analysis (which modules depend on duplicated code)
4. Test impact assessment (which tests verify duplicated code)

**Phase 0 Command**: Research will be consolidated directly into research.md without external agent tasks (patterns are well-defined).

---

## Phase 1: Design & Contracts

**Goal**: Define refactoring architecture and data models for consolidated code.

### 1.1 Data Model (`data-model.md`)

This feature doesn't introduce new entities, but documents refactoring consolidation:

**Validation Helper Module** (NEW):
```
ValidationHelper
├── Purpose: Consolidate __main__ validation from 8+ modules
├── Methods:
│   ├── run(): Execute all tests and report results
│   ├── add_test(name, func, expected): Register test
│   └── run_validation(): Validate all tests pass
├── Output Format: Same as current __main__ (PASS/FAIL counts)
└── Used By: All models (repository.py, person.py, analysis.py, etc.)
```

**Router Factory Pattern** (NEW):
```
CRUDRouterFactory
├── Purpose: Generate standard CRUD endpoints from entity + service
├── Input: Entity name, service reference, response model
├── Output: Router with standardized get, list, create, update, delete endpoints
└── Benefit: Eliminates 40-50% boilerplate from 3 routers
```

**Dashboard Template Component** (NEW):
```
DashboardTemplate<T>
├── Props: data[], isLoading, error, onSelect, renderCard(item)
├── Purpose: Reusable layout for repository/person/custom dashboards
├── Output: Grid layout, selection state, loading/error handling
└── Used By: RepositoryDashboard, PersonDashboard
```

### 1.2 Contracts

**Note**: Refactoring does NOT change API contracts. All existing endpoints maintain same request/response format.

- ✅ GET `/repositories` - unchanged
- ✅ GET `/repositories/{id}` - unchanged
- ✅ GET `/people` - unchanged
- ✅ GET `/people/{id}` - unchanged
- ✅ (All other endpoints unchanged)

### 1.3 Quickstart (`quickstart.md`)

After refactoring, development workflows remain identical:
- Using the validation helpers: `from testing.validation_helpers import ValidationHelper`
- Adding a new router: Use `CRUDRouterFactory` with service + entity
- Creating a dashboard: Use `DashboardTemplate<T>` with data hook

### 1.4 Agent Context Update

Run: `.specify/scripts/bash/update-agent-context.sh claude`

This will update `.claude/backend.md` and `.claude/frontend.md` with:
- New validation_helpers module in testing/
- New CRUDRouterFactory pattern
- New DashboardTemplate component pattern

---

## Phase 1 Completion Checklist

- [ ] research.md: Duplication analysis complete
- [ ] data-model.md: Refactoring modules documented
- [ ] contracts/: Verified no API changes (or documented if any)
- [ ] quickstart.md: Usage examples for refactored patterns
- [ ] Agent context: Updated with new patterns
- [ ] Constitution check (re-eval): All principles still compliant

---

## Phase 2: Task Generation

After Phase 1 approval, run `/speckit.tasks` to generate task list with:
- Individual refactoring tasks (one per duplication pattern)
- Task dependencies (validation helper first, then uses of it)
- Test commands for each task
- Commit message templates
