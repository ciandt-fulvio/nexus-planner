# Tasks: Backend API with Mocked Data

**Input**: Design documents from `/specs/001-backend-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD is required by project constitution. Tests MUST be written and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/nexus_api/`, `backend/tests/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Initialize Python project with uv and create backend/pyproject.toml
- [x] T003 [P] Add FastAPI, Pydantic, uvicorn, pydantic-settings, loguru dependencies
- [x] T004 [P] Add dev dependencies: pytest, pytest-cov, httpx, mypy, ruff
- [x] T005 [P] Create backend/.env with HOST, PORT, DEBUG, CORS_ORIGINS, API_V1_PREFIX
- [x] T006 [P] Create frontend/.env with VITE_API_URL=http://localhost:8000/api/v1

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create config module with Settings class in backend/src/nexus_api/config.py
- [x] T008 Create FastAPI app with CORS middleware in backend/src/nexus_api/main.py
- [x] T009 [P] Create shared Alert and AlertType models in backend/src/nexus_api/models/__init__.py
- [x] T010 [P] Create pytest conftest with TestClient fixture in backend/tests/conftest.py
- [x] T011 [P] Create frontend API client configuration in frontend/src/lib/api.ts
- [x] T012 Verify backend server starts and Swagger UI accessible at http://localhost:8000/docs

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Repository Dashboard (Priority: P1) 🎯 MVP

**Goal**: Provide GET /api/v1/repositories endpoint returning all repositories with metrics

**Independent Test**: Call GET /repositories and verify 5 repositories returned with all fields

### Tests for User Story 1 (TDD Required)

> **Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Write unit test for Repository model validation in backend/tests/unit/test_models.py
- [x] T014 [P] [US1] Write integration test for GET /repositories endpoint in backend/tests/integration/test_api.py

### Implementation for User Story 1

- [x] T015 [P] [US1] Create ActivityLevel, TopContributor, Hotspot models in backend/src/nexus_api/models/repository.py
- [x] T016 [US1] Create Repository model with all fields in backend/src/nexus_api/models/repository.py
- [x] T017 [US1] Create repositories mocked data (5 repos) in backend/src/nexus_api/data/mock_data.py
- [x] T018 [US1] Create repositories router with GET /repositories in backend/src/nexus_api/routers/repositories.py
- [x] T019 [US1] Register repositories router in main.py with /api/v1 prefix
- [x] T020 [US1] Add validation block to repository.py module
- [x] T021 [US1] Verify T013, T014 tests now pass

### Frontend Service for User Story 1

- [x] T022 [P] [US1] Create useRepositories hook in frontend/src/services/repositories.ts
- [x] T023 [US1] Export Repository types from frontend/src/services/repositories.ts

**Checkpoint**: Repository list endpoint functional, frontend hook ready

---

## Phase 4: User Story 2 - View Person Dashboard (Priority: P1)

**Goal**: Provide GET /api/v1/people endpoint returning all people with expertise metrics

**Independent Test**: Call GET /people and verify 5 people returned with all fields

### Tests for User Story 2 (TDD Required)

- [x] T024 [P] [US2] Write unit test for Person model validation in backend/tests/unit/test_models.py
- [x] T025 [P] [US2] Write integration test for GET /people endpoint in backend/tests/integration/test_api.py

### Implementation for User Story 2

- [x] T026 [P] [US2] Create PersonRepository, Technology models in backend/src/nexus_api/models/person.py
- [x] T027 [US2] Create Person model with all fields in backend/src/nexus_api/models/person.py
- [x] T028 [US2] Create people mocked data (5 people) in backend/src/nexus_api/data/mock_data.py
- [x] T029 [US2] Create people router with GET /people in backend/src/nexus_api/routers/people.py
- [x] T030 [US2] Register people router in main.py
- [x] T031 [US2] Add validation block to person.py module
- [x] T032 [US2] Verify T024, T025 tests now pass

### Frontend Service for User Story 2

- [x] T033 [P] [US2] Create usePeople hook in frontend/src/services/people.ts
- [x] T034 [US2] Export Person types from frontend/src/services/people.ts

**Checkpoint**: People list endpoint functional, frontend hook ready

---

## Phase 5: User Story 3 - Analyze Feature Impact (Priority: P2)

**Goal**: Provide POST /api/v1/analysis endpoint returning static feature analysis

**Independent Test**: POST feature description and verify analysis response with all sections

### Tests for User Story 3 (TDD Required)

- [x] T035 [P] [US3] Write unit test for FeatureAnalysis model validation in backend/tests/unit/test_models.py
- [x] T036 [P] [US3] Write integration test for POST /analysis endpoint in backend/tests/integration/test_api.py
- [x] T037 [P] [US3] Write test for empty description validation (400 error) in backend/tests/integration/test_api.py

### Implementation for User Story 3

- [x] T038 [P] [US3] Create ImpactedRepo, RecommendedPerson, Risk, SuggestedStep models in backend/src/nexus_api/models/analysis.py
- [x] T039 [US3] Create FeatureAnalysis and AnalyzeFeatureRequest models in backend/src/nexus_api/models/analysis.py
- [x] T040 [US3] Create example analysis mocked data in backend/src/nexus_api/data/mock_data.py
- [x] T041 [US3] Create analysis router with POST /analysis in backend/src/nexus_api/routers/analysis.py
- [x] T042 [US3] Register analysis router in main.py
- [x] T043 [US3] Add validation block to analysis.py module
- [x] T044 [US3] Verify T035, T036, T037 tests now pass

### Frontend Service for User Story 3

- [x] T045 [P] [US3] Create useAnalyzeFeature mutation hook in frontend/src/services/analysis.ts
- [x] T046 [US3] Export FeatureAnalysis types from frontend/src/services/analysis.ts

**Checkpoint**: Analysis endpoint functional, frontend hook ready

---

## Phase 6: User Story 4 - Get Repository Details (Priority: P2)

**Goal**: Provide GET /api/v1/repositories/{id} endpoint returning single repository

**Independent Test**: Call GET /repositories/1 and verify repository details; GET /repositories/999 returns 404

### Tests for User Story 4 (TDD Required)

- [x] T047 [P] [US4] Write integration test for GET /repositories/{id} success in backend/tests/integration/test_api.py
- [x] T048 [P] [US4] Write integration test for GET /repositories/{id} 404 error in backend/tests/integration/test_api.py

### Implementation for User Story 4

- [x] T049 [US4] Add GET /repositories/{id} route to backend/src/nexus_api/routers/repositories.py
- [x] T050 [US4] Implement get_repository_by_id function with 404 handling
- [x] T051 [US4] Verify T047, T048 tests now pass

### Frontend Service for User Story 4

- [x] T052 [US4] Add useRepository(id) hook to frontend/src/services/repositories.ts

**Checkpoint**: Repository detail endpoint functional

---

## Phase 7: User Story 5 - Get Person Details (Priority: P2)

**Goal**: Provide GET /api/v1/people/{id} endpoint returning single person

**Independent Test**: Call GET /people/1 and verify person details; GET /people/999 returns 404

### Tests for User Story 5 (TDD Required)

- [x] T053 [P] [US5] Write integration test for GET /people/{id} success in backend/tests/integration/test_api.py
- [x] T054 [P] [US5] Write integration test for GET /people/{id} 404 error in backend/tests/integration/test_api.py

### Implementation for User Story 5

- [x] T055 [US5] Add GET /people/{id} route to backend/src/nexus_api/routers/people.py
- [x] T056 [US5] Implement get_person_by_id function with 404 handling
- [x] T057 [US5] Verify T053, T054 tests now pass

### Frontend Service for User Story 5

- [x] T058 [US5] Add usePerson(id) hook to frontend/src/services/people.ts

**Checkpoint**: Person detail endpoint functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T059 [P] Run mypy type checking on backend/src/
- [ ] T060 [P] Run ruff linting and formatting on backend/src/
- [ ] T061 [P] Verify all backend tests pass with coverage report
- [ ] T062 [P] Export all services from frontend/src/services/index.ts
- [ ] T063 Verify Swagger UI documents all endpoints at http://localhost:8000/docs
- [ ] T064 Run quickstart.md validation (both backend and frontend start successfully)
- [ ] T065 Verify frontend can fetch data from all API endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 (P1): Can proceed in parallel after Foundational
  - US3, US4, US5 (P2): Can proceed after Foundational (US4 depends on US1 router, US5 depends on US2 router)
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

| Story | Priority | Backend Dependency | Frontend Dependency |
|-------|----------|-------------------|---------------------|
| US1 - Repository List | P1 | Foundational only | api.ts |
| US2 - People List | P1 | Foundational only | api.ts |
| US3 - Feature Analysis | P2 | Foundational only | api.ts |
| US4 - Repository Detail | P2 | US1 router exists | repositories.ts |
| US5 - Person Detail | P2 | US2 router exists | people.ts |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD)
2. Models before routers
3. Mocked data before routes
4. Backend complete before frontend service
5. Verify tests pass after implementation

### Parallel Opportunities

**Setup Phase (T001-T006)**:
- T003, T004, T005, T006 can run in parallel after T001, T002

**Foundational Phase (T007-T012)**:
- T009, T010, T011 can run in parallel after T007, T008

**User Story 1 + 2 (P1 priority)**:
- US1 and US2 can be implemented in parallel by different developers

**Within Each User Story**:
- All tests marked [P] can run in parallel
- Frontend service can start after backend endpoint works

---

## Parallel Example: User Stories 1 & 2 (P1 Priority)

```bash
# Developer A: User Story 1 (Repositories)
Task: T013-T023

# Developer B: User Story 2 (People)
Task: T024-T034

# Both can run simultaneously after Foundational phase completes
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Repository Dashboard)
4. **STOP and VALIDATE**: Test independently via Swagger UI
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 (P1) → Both dashboards work → Deploy/Demo (MVP!)
3. Add US3 → Planning Assistant works → Deploy/Demo
4. Add US4 + US5 → Detail views work → Deploy/Demo
5. Polish → Production ready

---

## Summary

| Phase | Tasks | User Story | Parallel |
|-------|-------|------------|----------|
| Setup | T001-T006 | - | 4 |
| Foundational | T007-T012 | - | 3 |
| US1 Repository List | T013-T023 | P1 | 4 |
| US2 People List | T024-T034 | P1 | 4 |
| US3 Feature Analysis | T035-T046 | P2 | 5 |
| US4 Repository Detail | T047-T052 | P2 | 2 |
| US5 Person Detail | T053-T058 | P2 | 2 |
| Polish | T059-T065 | - | 4 |

**Total Tasks**: 65
**Parallel Opportunities**: 28 tasks can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- TDD required: Write test → Verify FAIL → Implement → Verify PASS
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
