# Data Model: Backend API with Mocked Data

**Date**: 2025-12-11
**Feature**: 001-backend-api

## Overview

This document defines the Pydantic models that mirror the existing TypeScript interfaces in `frontend/src/data/mockData.ts`. These models serve as:
1. API response schemas (automatic OpenAPI generation)
2. Data validation contracts
3. Type safety enforcement

## Entities

### Alert

Shared model for risk/informational indicators used by Repository and Person.

```python
class AlertType(str, Enum):
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"

class Alert(BaseModel):
    type: AlertType
    message: str
```

**Validation Rules**:
- `type`: Must be one of "warning", "danger", "info"
- `message`: Non-empty string

---

### Repository

Represents a Git repository with metrics.

```python
class ActivityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STALE = "stale"

class TopContributor(BaseModel):
    name: str
    percentage: int  # 0-100

class Hotspot(BaseModel):
    path: str
    changes: int  # Positive integer

class Repository(BaseModel):
    id: str
    name: str
    description: str
    lastCommit: str  # Date string (e.g., "2024-01-15")
    totalCommits: int
    contributors: int
    activity: ActivityLevel
    knowledgeConcentration: int  # 0-100
    topContributors: list[TopContributor]
    hotspots: list[Hotspot]
    dependencies: list[str]  # Repository names
    alerts: list[Alert]
```

**Validation Rules**:
- `id`: Non-empty unique identifier
- `knowledgeConcentration`: Integer 0-100
- `topContributors.percentage`: Integer 0-100
- `hotspots.changes`: Positive integer
- `activity`: Must be one of "high", "medium", "low", "stale"

---

### Person

Represents a team member with expertise metrics.

```python
class PersonRepository(BaseModel):
    name: str
    commits: int
    lastActivity: str  # Date string
    expertise: int  # 0-100

class Technology(BaseModel):
    name: str
    level: int  # 0-100

class Person(BaseModel):
    id: str
    name: str
    email: str
    avatar: str  # Initials (e.g., "AS")
    repositories: list[PersonRepository]
    technologies: list[Technology]
    domains: list[str]  # Business domain names
    recentActivity: int  # Commits in last 30 days
    alerts: list[Alert]
```

**Validation Rules**:
- `id`: Non-empty unique identifier
- `email`: Valid email format
- `expertise`: Integer 0-100
- `level`: Integer 0-100
- `recentActivity`: Non-negative integer

---

### FeatureAnalysis

Represents the result of analyzing a feature description.

```python
class ImpactedRepo(BaseModel):
    name: str
    confidence: int  # 0-100
    reasoning: str
    modules: list[str]  # Affected module paths

class RecommendedPerson(BaseModel):
    name: str
    relevance: int  # 0-100
    reasoning: str

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Risk(BaseModel):
    type: RiskLevel
    message: str

class SuggestedStep(BaseModel):
    step: int  # 1-based order
    action: str
    repository: str
    reasoning: str

class FeatureAnalysis(BaseModel):
    feature: str  # The input feature description
    impactedRepos: list[ImpactedRepo]
    recommendedPeople: list[RecommendedPerson]
    risks: list[Risk]
    suggestedOrder: list[SuggestedStep]
    additionalRecommendations: list[str]
```

**Validation Rules**:
- `confidence`: Integer 0-100
- `relevance`: Integer 0-100
- `step`: Positive integer (1-based)
- `type`: Must be one of "high", "medium", "low"

---

### API Request/Response Models

```python
class AnalyzeFeatureRequest(BaseModel):
    description: str  # Feature description text

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v

class ErrorResponse(BaseModel):
    detail: str  # Error message
```

## Entity Relationships

```
Repository
├── has many → TopContributor
├── has many → Hotspot
├── has many → Alert
└── references → Repository (dependencies)

Person
├── has many → PersonRepository
├── has many → Technology
└── has many → Alert

FeatureAnalysis
├── has many → ImpactedRepo
├── has many → RecommendedPerson
├── has many → Risk
└── has many → SuggestedStep
```

## TypeScript Interface Mapping

| TypeScript (frontend) | Python (backend) | Notes |
|-----------------------|------------------|-------|
| `Repository` | `Repository` | Exact field match |
| `Person` | `Person` | Exact field match |
| `FeatureAnalysis` | `FeatureAnalysis` | Exact field match |
| `{ type, message }` | `Alert` | Shared by both entities |

## Pydantic Configuration

All models use:
```python
class Config:
    str_strip_whitespace = True
    validate_assignment = True
    extra = "forbid"  # Reject unknown fields
```
