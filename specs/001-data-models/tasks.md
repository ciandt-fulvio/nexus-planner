# Tasks: Data Models e Persistência

**Input**: Design documents from `/specs/001-data-models/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per Constitution Principle I (Test-First Development). All tasks must follow TDD: write tests first, ensure they fail, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths follow plan.md structure with 4-layer architecture: db → models → services → routers

---

## Phase 1: Setup (Shared Infrastructure) ✅

**Purpose**: Project initialization, dependencies and configuration

- [X] T001 Add SQLAlchemy and aiosqlite dependencies in backend/pyproject.toml
- [X] T002 Add pytest-asyncio to dev dependencies in backend/pyproject.toml
- [X] T003 [P] Create db package with __init__.py in backend/src/nexus_api/db/__init__.py
- [X] T004 [P] Create services package with __init__.py in backend/src/nexus_api/services/__init__.py
- [X] T005 Add all threshold settings to Settings class in backend/src/nexus_api/config.py

---

## Phase 2: Foundational (Blocking Prerequisites) ✅

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational (MANDATORY per Constitution) ⚠️

> **CONSTITUTION PRINCIPLE I: Write these tests FIRST, commit them, verify they FAIL, then proceed to implementation**

- [X] T006 [P] Unit tests for database connection and session in backend/tests/unit/test_database.py
- [X] T007 [P] Unit tests for SQLAlchemy table definitions in backend/tests/unit/test_tables.py

### Implementation for Foundational

- [X] T008 Implement async SQLite engine and session factory in backend/src/nexus_api/db/database.py
- [X] T009 Define CommitTable SQLAlchemy model in backend/src/nexus_api/db/tables.py
- [X] T010 Define RepositoryTable SQLAlchemy model in backend/src/nexus_api/db/tables.py
- [X] T011 Define PersonTable SQLAlchemy model in backend/src/nexus_api/db/tables.py
- [X] T012 Define AlertTable SQLAlchemy model in backend/src/nexus_api/db/tables.py
- [X] T013 Define FeatureAnalysisTable SQLAlchemy model in backend/src/nexus_api/db/tables.py
- [X] T014 Add table creation on app startup in backend/src/nexus_api/main.py
- [X] T015 Create shared test fixtures (db session, sample data) in backend/tests/conftest.py

**Checkpoint**: Foundation ready - database layer complete, user story implementation can now begin

---

## Phase 3: User Story 1 - Visualizar Repositórios com Dados Reais (Priority: P1) 🎯 MVP ✅

**Goal**: Usuário visualiza repositórios com métricas reais (topContributors, hotspots, activity) calculadas sobre commits armazenados

**Independent Test**: Acessar GET /api/v1/repositories e verificar que retorna dados calculados do banco em vez de mock

### Tests for User Story 1 (MANDATORY per Constitution) ⚠️

> **CONSTITUTION PRINCIPLE I: Write these tests FIRST, commit them, verify they FAIL, then proceed to implementation**

- [X] T016 [P] [US1] Unit tests for Commit Pydantic model in backend/tests/unit/test_models.py
- [X] T017 [P] [US1] Unit tests for Repository Pydantic model in backend/tests/unit/test_models.py
- [X] T018 [P] [US1] Unit tests for metrics functions (activity, concentration) in backend/tests/unit/test_metrics.py
- [X] T019 [P] [US1] Unit tests for commit_service in backend/tests/unit/test_services.py
- [X] T020 [P] [US1] Unit tests for repository_service in backend/tests/unit/test_services.py
- [X] T021 [P] [US1] Integration tests for GET /repositories endpoint in backend/tests/integration/test_api.py

### Implementation for User Story 1

- [X] T022 [P] [US1] Create FileChange, TopContributor, Hotspot Pydantic models in backend/src/nexus_api/models/commit.py
- [X] T023 [P] [US1] Create Commit Pydantic model in backend/src/nexus_api/models/commit.py
- [X] T024 [P] [US1] Update ActivityLevel enum (lowercase values) in backend/src/nexus_api/models/repository.py
- [X] T025 [US1] Implement calculate_activity_level function in backend/src/nexus_api/services/metrics.py
- [X] T026 [US1] Implement calculate_knowledge_concentration function in backend/src/nexus_api/services/metrics.py
- [X] T027 [US1] Implement calculate_top_contributors function in backend/src/nexus_api/services/metrics.py
- [X] T028 [US1] Implement calculate_hotspots function in backend/src/nexus_api/services/metrics.py
- [X] T029 [US1] Implement commit_service with CRUD operations in backend/src/nexus_api/services/commit_service.py
- [X] T030 [US1] Implement repository_service with get_all and get_by_id in backend/src/nexus_api/services/repository_service.py
- [X] T031 [US1] Update Repository model with calculated fields in backend/src/nexus_api/models/repository.py
- [X] T032 [US1] Refactor repositories router to use repository_service in backend/src/nexus_api/routers/repositories.py
- [X] T033 [US1] Add dependency injection for db session in backend/src/nexus_api/main.py

**Checkpoint**: User Story 1 complete - GET /repositories retorna dados reais calculados

---

## Phase 4: User Story 2 - Visualizar Pessoas com Métricas Calculadas (Priority: P2) ✅

**Goal**: Usuário visualiza pessoas com tecnologias detectadas, repositórios e níveis de expertise calculados

**Independent Test**: Acessar GET /api/v1/people e verificar tecnologias e expertise calculados dos commits

### Tests for User Story 2 (MANDATORY per Constitution) ⚠️

> **CONSTITUTION PRINCIPLE I: Write these tests FIRST, commit them, verify they FAIL, then proceed to implementation**

- [X] T034 [P] [US2] Unit tests for Technology, PersonRepository Pydantic models in backend/tests/unit/test_models.py
- [X] T035 [P] [US2] Unit tests for detect_technologies function in backend/tests/unit/test_metrics.py
- [X] T036 [P] [US2] Unit tests for calculate_expertise function in backend/tests/unit/test_metrics.py
- [X] T037 [P] [US2] Unit tests for person_service in backend/tests/unit/test_services.py
- [X] T038 [P] [US2] Integration tests for GET /people endpoint in backend/tests/integration/test_api.py

### Implementation for User Story 2

- [X] T039 [P] [US2] Create Technology Pydantic model in backend/src/nexus_api/models/person.py
- [X] T040 [P] [US2] Create PersonRepository Pydantic model in backend/src/nexus_api/models/person.py
- [X] T041 [US2] Implement detect_technologies function in backend/src/nexus_api/services/metrics.py
- [X] T042 [US2] Implement calculate_expertise function in backend/src/nexus_api/services/metrics.py
- [X] T043 [US2] Implement calculate_recent_activity function in backend/src/nexus_api/services/metrics.py
- [X] T044 [US2] Implement person_service with get_all and get_by_id in backend/src/nexus_api/services/person_service.py
- [X] T045 [US2] Update Person model with calculated fields in backend/src/nexus_api/models/person.py
- [X] T046 [US2] Refactor people router to use person_service in backend/src/nexus_api/routers/people.py

**Checkpoint**: User Story 2 complete - GET /people retorna pessoas com tecnologias e expertise

---

## Phase 5: User Story 3 - Receber Alertas Gerados por IA (Priority: P3) ✅

**Goal**: Usuário visualiza alertas sobre riscos (concentração, inatividade) gerados e cacheados

**Independent Test**: Verificar que alertas são retornados com repositórios e regenerados quando PR muda

### Tests for User Story 3 (MANDATORY per Constitution) ⚠️

> **CONSTITUTION PRINCIPLE I: Write these tests FIRST, commit them, verify they FAIL, then proceed to implementation**

- [X] T047 [P] [US3] Unit tests for Alert Pydantic model in backend/tests/unit/test_models.py
- [X] T048 [P] [US3] Unit tests for alert_service cache logic in backend/tests/unit/test_services.py
- [X] T049 [P] [US3] Integration tests for alerts in repository response in backend/tests/integration/test_api.py

### Implementation for User Story 3

- [X] T050 [P] [US3] Create AlertSeverity enum in backend/src/nexus_api/models/alert.py
- [X] T051 [P] [US3] Create Alert Pydantic model with flexible structure in backend/src/nexus_api/models/alert.py
- [X] T052 [US3] Implement alert_service with cache check in backend/src/nexus_api/services/alert_service.py
- [X] T053 [US3] Implement get_alerts_for_repository in backend/src/nexus_api/services/alert_service.py
- [X] T054 [US3] Implement get_alerts_for_person in backend/src/nexus_api/services/alert_service.py
- [X] T055 [US3] Implement should_regenerate_alerts logic in backend/src/nexus_api/services/alert_service.py
- [X] T056 [US3] Integrate alerts into repository_service response in backend/src/nexus_api/services/repository_service.py
- [X] T057 [US3] Integrate alerts into person_service response in backend/src/nexus_api/services/person_service.py
- [X] T058 [US3] Update models/__init__.py exports in backend/src/nexus_api/models/__init__.py

**Checkpoint**: User Story 3 complete - Alertas são exibidos e cacheados corretamente

---

## Phase 6: User Story 4 - Obter Análise de Impacto de Feature (Priority: P4) ✅

**Goal**: Usuário descreve feature e recebe análise de impacto em Markdown com links dinâmicos

**Independent Test**: POST /api/v1/analysis retorna análise com links parseáveis

### Tests for User Story 4 (MANDATORY per Constitution) ⚠️

> **CONSTITUTION PRINCIPLE I: Write these tests FIRST, commit them, verify they FAIL, then proceed to implementation**

- [X] T059 [P] [US4] Unit tests for FeatureAnalysis Pydantic model in backend/tests/unit/test_models.py
- [X] T060 [P] [US4] Unit tests for analysis_service in backend/tests/unit/test_services.py
- [X] T061 [P] [US4] Integration tests for POST /analysis endpoint in backend/tests/integration/test_api.py

### Implementation for User Story 4

- [X] T062 [P] [US4] Create AnalysisRequest Pydantic model in backend/src/nexus_api/models/analysis.py
- [X] T063 [P] [US4] Create FeatureAnalysis Pydantic model (anemic) in backend/src/nexus_api/models/analysis.py
- [X] T064 [US4] Implement analysis_service with create and get in backend/src/nexus_api/services/analysis_service.py
- [X] T065 [US4] Implement save_analysis in backend/src/nexus_api/services/analysis_service.py
- [X] T066 [US4] Refactor analysis router to use analysis_service in backend/src/nexus_api/routers/analysis.py
- [X] T067 [US4] Add POST /analysis endpoint in backend/src/nexus_api/routers/analysis.py

**Checkpoint**: User Story 4 complete - Análises são criadas e armazenadas

---

## Phase 7: Polish & Cross-Cutting Concerns ✅

**Purpose**: Improvements that affect multiple user stories

- [X] T068 [P] Update services/__init__.py exports in backend/src/nexus_api/services/__init__.py
- [X] T069 [P] Remove mock_data fallback from routers, add seed_service for database seeding on startup
- [X] T070 [P] Add integration test for database operations in backend/tests/integration/test_db.py
- [X] T071 Run all tests and verify < 5s for fast battery in backend/ (100 tests in 1.68s ✅)
- [X] T072 Validate quickstart.md instructions in specs/001-data-models/quickstart.md
- [X] T073 Verify all APIs match contracts/api-v1.yaml in specs/001-data-models/contracts/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 can start after Foundational
  - US2 depends on Foundational only (can parallel with US1)
  - US3 depends on US1 and US2 (uses repository and person data)
  - US4 depends on US1 and US2 (uses repository and person data)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - implements core metrics for repositories
- **User Story 2 (P2)**: Foundation only - implements metrics for people
- **User Story 3 (P3)**: Depends on US1 + US2 - adds alerts to existing entities
- **User Story 4 (P4)**: Depends on US1 + US2 - creates feature analysis

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Constitution Principle I)
- Fast test battery (< 5s) runs before each commit (Constitution Principle II)
- Commit at each task completion (Constitution Principle IV)
- Models before services
- Services before routers
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004 can run in parallel (different packages)

**Phase 2 (Foundational)**:
- T006, T007 can run in parallel (different test files)
- T009-T013 can run in parallel (same file but different classes)

**Phase 3 (US1)**:
- All tests T016-T021 can run in parallel
- T022, T023, T024 can run in parallel (different models)
- T025-T028 can run in parallel (different functions)

**Phase 4 (US2)**:
- All tests T034-T038 can run in parallel
- T039, T040 can run in parallel (different models)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit tests for Commit Pydantic model in backend/tests/unit/test_models.py"
Task: "Unit tests for Repository Pydantic model in backend/tests/unit/test_models.py"
Task: "Unit tests for metrics functions in backend/tests/unit/test_metrics.py"

# Launch all Pydantic models together:
Task: "Create FileChange, TopContributor, Hotspot models in backend/src/nexus_api/models/commit.py"
Task: "Create Commit model in backend/src/nexus_api/models/commit.py"
Task: "Update ActivityLevel enum in backend/src/nexus_api/models/repository.py"

# Launch all metrics functions together:
Task: "Implement calculate_activity_level in backend/src/nexus_api/services/metrics.py"
Task: "Implement calculate_knowledge_concentration in backend/src/nexus_api/services/metrics.py"
Task: "Implement calculate_top_contributors in backend/src/nexus_api/services/metrics.py"
Task: "Implement calculate_hotspots in backend/src/nexus_api/services/metrics.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test GET /repositories returns real data
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

---

## Notes

### Task Execution

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing

### Constitution Compliance (MANDATORY)

- **Principle I (TDD/BDD)**: Write tests FIRST, verify they FAIL, then implement
- **Principle II (Fast Battery)**: Run fast tests (< 5s) before EACH commit
- **Principle III (Complete Battery)**: Run ALL tests before opening PR
- **Principle IV (Frequent Commits)**: Commit after EACH task or small logical step
- **Principle V (Simplicity)**: Keep functions < 30 lines, files < 500 lines

### Development Flow

1. Write test (commit: "test: add tests for [feature]")
2. Verify test fails
3. Implement feature incrementally
4. Run fast test battery before each commit
5. Commit at each task completion
6. Stop at checkpoints to validate story independently
7. Run complete test battery before PR

### Thresholds (via .env)

All thresholds are configurable via environment variables:
- `WINDOW_SIZE=300`
- `ACTIVITY_HIGH_THRESHOLD=30`
- `ACTIVITY_MEDIUM_THRESHOLD=10`
- `ACTIVITY_LOW_THRESHOLD=1`
- `CONCENTRATION_WARNING_THRESHOLD=50`
- `CONCENTRATION_CRITICAL_THRESHOLD=70`
- `TOP_CONTRIBUTORS_LIMIT=3`
- `TOP_HOTSPOTS_LIMIT=5`
