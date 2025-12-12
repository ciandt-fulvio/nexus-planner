# Feature Specification: Backend API with Mocked Data

**Feature Branch**: `001-backend-api`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Create backend API with mocked data to serve as data source for the frontend prototype"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Repository Dashboard (Priority: P1)

As a development team lead, I want to view a list of all repositories with their key metrics (activity level, last commit, contributors count) so that I can quickly assess the health of my organization's codebase.

**Why this priority**: This is the core data that powers the Repository Dashboard tab - the primary view of the application. Without repository data, the frontend cannot display any meaningful information.

**Independent Test**: Can be fully tested by accessing the repository list endpoint and verifying that repository cards display with activity badges, commit counts, and contributor information.

**Acceptance Scenarios**:

1. **Given** the user opens the Repository Dashboard, **When** the page loads, **Then** all repositories are displayed as cards with name, description, activity level badge, last commit date, total commits, and contributor count.
2. **Given** the user selects a repository card, **When** they click on it, **Then** detailed information appears including alerts, knowledge concentration, top contributors, hotspots, and dependencies.
3. **Given** the repositories endpoint is called, **When** the request completes, **Then** the response time is under 1 second.

---

### User Story 2 - View Person Dashboard (Priority: P1)

As a development team lead, I want to view a list of all team members with their expertise levels, recent activity, and repository contributions so that I can understand knowledge distribution and identify concentration risks.

**Why this priority**: People data is equally critical as repository data - it powers the Person Dashboard tab and provides the human context for planning decisions.

**Independent Test**: Can be fully tested by accessing the people list endpoint and verifying that person cards display with avatar, activity badges, repository count, and technology count.

**Acceptance Scenarios**:

1. **Given** the user opens the Person Dashboard, **When** the page loads, **Then** all team members are displayed as cards with name, email, avatar initials, recent activity badge, and summary counts.
2. **Given** the user selects a person card, **When** they click on it, **Then** detailed information appears including alerts, technologies with expertise levels, repositories with contribution details, and business domains.
3. **Given** a person has no recent activity, **When** their card is displayed, **Then** an "Inactive" badge is shown and relevant alerts highlight this risk.

---

### User Story 3 - Analyze Feature Impact with Planning Assistant (Priority: P2)

As a product manager or tech lead, I want to describe a new feature in natural language and receive an AI-generated analysis of impacted repositories, recommended team members, identified risks, and suggested implementation order so that I can make informed planning decisions.

**Why this priority**: This is the most valuable feature of the platform but depends on repository and people data being available first. It transforms raw data into actionable planning insights.

**Independent Test**: Can be fully tested by submitting a feature description to the analysis endpoint and verifying the response contains impacted repos, recommended people, risks, suggested order, and recommendations.

**Acceptance Scenarios**:

1. **Given** the user enters a feature description, **When** they click "Analyze", **Then** the system returns a list of impacted repositories with confidence percentages and affected modules.
2. **Given** the feature analysis completes, **When** results are displayed, **Then** recommended people are shown with relevance scores and reasoning for their inclusion.
3. **Given** repositories involved have risk factors (stale, high concentration), **When** the analysis is shown, **Then** these risks are highlighted with severity levels and descriptive messages.
4. **Given** multiple repositories are impacted, **When** the analysis completes, **Then** a suggested implementation order is provided with step numbers, actions, repository names, and reasoning.

---

### User Story 4 - Get Repository Details (Priority: P2)

As a developer preparing to work on a repository, I want to view detailed information about a specific repository including hotspots, dependencies, and contributor distribution so that I can understand where to focus attention and who to consult.

**Why this priority**: Detailed repository views enable deeper analysis beyond the list view, supporting informed decision-making during sprint planning.

**Independent Test**: Can be fully tested by requesting a specific repository by ID and verifying all detail fields are present and accurate.

**Acceptance Scenarios**:

1. **Given** a repository ID, **When** the detail endpoint is called, **Then** the response includes all repository fields: name, description, activity, commits, contributors, alerts, hotspots, dependencies, and top contributors.
2. **Given** a non-existent repository ID, **When** the detail endpoint is called, **Then** a clear "not found" response is returned.

---

### User Story 5 - Get Person Details (Priority: P2)

As a team lead evaluating team member assignments, I want to view detailed information about a specific person including their technology expertise, repository contributions over time, and business domain knowledge so that I can make optimal task assignments.

**Why this priority**: Detailed person views support individual assessment and team composition decisions.

**Independent Test**: Can be fully tested by requesting a specific person by ID and verifying all detail fields are present and accurate.

**Acceptance Scenarios**:

1. **Given** a person ID, **When** the detail endpoint is called, **Then** the response includes all person fields: name, email, avatar, repositories with expertise levels, technologies with proficiency scores, domains, recent activity, and alerts.
2. **Given** a non-existent person ID, **When** the detail endpoint is called, **Then** a clear "not found" response is returned.

---

### Edge Cases

- What happens when the feature description for analysis is empty? System returns a validation error prompting for input.
- What happens when a repository has no alerts? The alerts array is empty but the response structure remains consistent.
- What happens when a person has zero recent commits? The recentActivity field is 0 and appropriate "Inactive" status is reflected.
- How does the system handle special characters in feature descriptions? Text is accepted as-is for the mocked version.

## Requirements *(mandatory)*

### Functional Requirements

**Repository Endpoints**:
- **FR-001**: System MUST provide an endpoint to list all repositories with summary information (id, name, description, lastCommit, totalCommits, contributors, activity level)
- **FR-002**: System MUST provide an endpoint to retrieve detailed repository information by ID including knowledgeConcentration, topContributors, hotspots, dependencies, and alerts
- **FR-003**: Repository activity levels MUST be one of: "high", "medium", "low", or "stale"
- **FR-004**: Repository alerts MUST include a type ("warning", "danger", or "info") and a message string

**Person Endpoints**:
- **FR-005**: System MUST provide an endpoint to list all people with summary information (id, name, email, avatar, recentActivity, repository count, technology count)
- **FR-006**: System MUST provide an endpoint to retrieve detailed person information by ID including full repositories list with expertise levels, technologies with proficiency levels, domains, and alerts
- **FR-007**: Person alerts MUST include a type ("warning", "danger", or "info") and a message string

**Feature Analysis Endpoint**:
- **FR-008**: System MUST provide an endpoint to analyze a feature description and return impacted repositories with confidence scores (0-100) and affected modules
- **FR-009**: System MUST return recommended people for a feature with relevance scores (0-100) and reasoning
- **FR-010**: System MUST return identified risks with severity levels ("high", "medium", "low") and descriptive messages
- **FR-011**: System MUST return a suggested implementation order with step numbers, actions, repository names, and reasoning
- **FR-012**: System MUST return additional recommendations as a list of actionable strings
- **FR-018**: For MVP (mocked phase), the analysis endpoint MUST return the same static example analysis data regardless of input text

**Data Consistency**:
- **FR-013**: All mocked data MUST be consistent with the existing frontend mockData.ts types (Repository, Person, FeatureAnalysis interfaces)
- **FR-014**: All endpoints MUST return JSON responses with consistent structure
- **FR-015**: All list endpoints MUST support future pagination (return array directly for MVP, structure allows wrapping)

**Frontend Integration**:
- **FR-019**: Frontend MUST include an API service layer (hooks/services) to fetch data from the backend
- **FR-020**: Frontend API services MUST use TanStack Query for data fetching and caching
- **FR-021**: Existing frontend components MUST remain unchanged - services return data in the same shape components expect
- **FR-022**: Frontend MUST support environment-based API URL configuration (development vs production)

**Error Handling**:
- **FR-016**: System MUST return appropriate error responses for invalid requests (404 for not found, 400 for bad request)
- **FR-017**: All error responses MUST include an error message field

### Key Entities

- **Repository**: Represents a Git repository with metrics including activity level, commit history, contributor distribution, code hotspots, inter-repository dependencies, and risk alerts
- **Person**: Represents a team member with expertise metrics including technology proficiencies, repository contributions with expertise levels, business domain knowledge, and risk alerts
- **FeatureAnalysis**: Represents the result of analyzing a feature description, containing impacted repositories, recommended people, identified risks, suggested implementation order, and additional recommendations
- **Alert**: A risk or informational indicator with severity type and descriptive message, used by both Repository and Person entities

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frontend can successfully fetch and display all repository data within 2 seconds of page load
- **SC-002**: Frontend can successfully fetch and display all person data within 2 seconds of page load
- **SC-003**: Feature analysis requests return complete results within 3 seconds
- **SC-004**: 100% of frontend components that currently use mockData.ts can be migrated to API calls without UI changes
- **SC-005**: All API responses match the TypeScript interfaces already defined in the frontend (Repository, Person, FeatureAnalysis)
- **SC-006**: Zero breaking changes to the existing frontend component contracts - components receive data in the same shape they expect

## Assumptions

- The mocked data will replicate the exact structure from `frontend/src/data/mockData.ts`
- The API will run on port 8000 with `/api/v1` prefix (e.g., `http://localhost:8000/api/v1/repositories`)
- CORS will be configured to allow requests from the frontend development server (port 8080)
- Authentication is not required for the MVP (mocked data phase)
- The frontend will use TanStack Query to manage API state and caching

## Clarifications

### Session 2025-12-11

- Q: What API base URL configuration should be used (port and path prefix)? → A: Port 8000 with `/api/v1` prefix
- Q: How should the feature analysis endpoint behave in the mocked phase? → A: Always return static exampleAnalysis data regardless of input
- Q: What scope of frontend changes should be included? → A: Backend API + frontend API service layer (hooks/services), components unchanged
