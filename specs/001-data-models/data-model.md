# Data Model: Data Models e Persistência

**Feature**: 001-data-models
**Date**: 2025-12-13
**Source**: [docs/data_dictionary.md](/docs/data_dictionary.md)

## Entities Overview

```
┌─────────────┐     ┌─────────────┐
│ Repository  │────<│   Commit    │
└─────────────┘     └─────────────┘
       │                   │
       │                   │
       v                   v
┌─────────────┐     ┌─────────────┐
│    Alert    │     │   Person    │
└─────────────┘     └─────────────┘
                          │
                          v
                   ┌─────────────┐
                   │    Alert    │
                   └─────────────┘

┌──────────────────┐
│ FeatureAnalysis  │ (standalone)
└──────────────────┘
```

## 1. Commit (Tabela Base)

Unidade fundamental de armazenamento. Representa um commit Git sincronizado.

### Campos

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| `id` | String(40) | No | SHA-1 do commit (PK) |
| `repository_id` | String(36) | No | FK para Repository |
| `author_name` | String(255) | No | Nome do autor |
| `author_email` | String(255) | No | Email do autor (usado para identificar Person) |
| `committer_name` | String(255) | No | Nome do committer |
| `committer_email` | String(255) | No | Email do committer |
| `author_date` | DateTime | No | Data de autoria (timezone-aware) |
| `commit_date` | DateTime | No | Data do commit (timezone-aware) |
| `message` | Text | No | Mensagem do commit |
| `files_changed` | JSON | No | Lista de arquivos: `[{"path": "...", "status": "added|modified|deleted"}]` |
| `additions` | Integer | No | Linhas adicionadas |
| `deletions` | Integer | No | Linhas removidas |
| `parent_shas` | JSON | Yes | Lista de SHAs dos pais: `["sha1", "sha2"]` |

### Índices

- `idx_commits_repository_date`: (repository_id, commit_date DESC) - Para janela móvel
- `idx_commits_author_email`: (author_email) - Para agregação por pessoa

### Constraints

- PK: id
- FK: repository_id → repositories.id

---

## 2. Repository

Representa um repositório Git com metadados e referência para cache de alertas.

### Campos

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| `id` | String(36) | No | UUID (PK) |
| `name` | String(255) | No | Nome do repositório |
| `description` | Text | Yes | Descrição do repositório |
| `git_url` | String(500) | No | URL do repositório Git |
| `last_alerts_pr_id` | String(100) | Yes | ID da última PR usada para gerar alertas |
| `created_at` | DateTime | No | Data de criação no sistema |
| `updated_at` | DateTime | No | Data da última atualização |

### Campos Calculados (não persistidos)

Calculados em tempo real a partir dos commits na janela móvel:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `lastCommit` | Date | Data do commit mais recente |
| `totalCommits` | Integer | Contagem de commits na janela |
| `contributors` | Integer | Contagem de author_email únicos |
| `activity` | Enum | HIGH, MEDIUM, LOW, STALE |
| `knowledgeConcentration` | Integer | % do maior contribuidor |
| `topContributors` | List | Top N contribuidores |
| `hotspots` | List | Top N arquivos modificados |
| `dependencies` | List | Repositórios dependentes |

### Índices

- `idx_repositories_name`: (name) - Para busca por nome

---

## 3. Person

Representa um desenvolvedor identificado por email.

### Campos

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| `id` | String(36) | No | UUID (PK) |
| `email` | String(255) | No | Email único (identificador) |
| `name` | String(255) | No | Nome mais recente encontrado |
| `avatar` | String(10) | Yes | Iniciais para avatar |
| `last_alert_commit_sha` | String(40) | Yes | SHA do último commit usado para alertas |
| `created_at` | DateTime | No | Data de criação no sistema |
| `updated_at` | DateTime | No | Data da última atualização |

### Campos Calculados (não persistidos)

Calculados em tempo real a partir dos commits:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `repositories` | List | Repositórios com commits e expertise |
| `technologies` | List | Tecnologias detectadas com níveis |
| `domains` | List | Áreas de conhecimento |
| `recentActivity` | Integer | Commits nos últimos 30 dias |

### Índices

- `idx_persons_email`: (email) UNIQUE - Identificador único

### Constraints

- UNIQUE: email

---

## 4. Alert

Cache de alertas gerados por IA.

### Campos

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| `id` | String(36) | No | UUID (PK) |
| `entity_type` | String(20) | No | "repository" ou "person" |
| `entity_id` | String(36) | No | ID da entidade relacionada |
| `reference_id` | String(100) | Yes | PR ID ou commit SHA que triggou geração |
| `title` | String(100) | No | Título do alerta |
| `description` | Text | No | Descrição em Markdown |
| `severity` | String(10) | No | "info", "warning", "critical" |
| `category` | String(50) | Yes | Categoria do alerta |
| `suggested_actions` | Text | Yes | Ações sugeridas em Markdown |
| `created_at` | DateTime | No | Data de criação |

### Índices

- `idx_alerts_entity`: (entity_type, entity_id) - Para busca por entidade
- `idx_alerts_reference`: (reference_id) - Para invalidação de cache

---

## 5. FeatureAnalysis

Análise de impacto de feature gerada por IA.

### Campos

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| `id` | String(36) | No | UUID (PK) |
| `feature_description` | Text | No | Descrição da feature (input do usuário) |
| `analysis_text` | Text | No | Análise completa em Markdown |
| `created_at` | DateTime | No | Data de criação |

### Índices

- `idx_feature_analysis_created`: (created_at DESC) - Para ordenação

---

## Pydantic Models (API Layer)

### CommitCreate (Input)

```python
class CommitCreate(BaseModel):
    id: str = Field(..., min_length=40, max_length=40)
    repository_id: str = Field(..., alias="repositoryId")
    author_name: str = Field(..., alias="authorName")
    author_email: str = Field(..., alias="authorEmail")
    committer_name: str = Field(..., alias="committerName")
    committer_email: str = Field(..., alias="committerEmail")
    author_date: datetime = Field(..., alias="authorDate")
    commit_date: datetime = Field(..., alias="commitDate")
    message: str
    files_changed: list[FileChange] = Field(..., alias="filesChanged")
    additions: int = Field(..., ge=0)
    deletions: int = Field(..., ge=0)
    parent_shas: list[str] | None = Field(None, alias="parentShas")
```

### Repository (Output)

```python
class Repository(BaseModel):
    id: str
    name: str
    description: str | None
    last_commit: date = Field(..., alias="lastCommit")
    total_commits: int = Field(..., alias="totalCommits")
    contributors: int
    activity: ActivityLevel
    knowledge_concentration: int = Field(..., alias="knowledgeConcentration")
    top_contributors: list[TopContributor] = Field(..., alias="topContributors")
    hotspots: list[Hotspot]
    dependencies: list[str]
    alerts: list[Alert]
```

### Person (Output)

```python
class Person(BaseModel):
    id: str
    name: str
    email: str
    avatar: str
    repositories: list[PersonRepository]
    technologies: list[Technology]
    domains: list[str]
    recent_activity: int = Field(..., alias="recentActivity")
    alerts: list[Alert]
```

### Alert (Output)

```python
class Alert(BaseModel):
    id: str
    title: str
    description: str  # Markdown com links dinâmicos
    severity: AlertSeverity
    category: str | None = None
    suggested_actions: str | None = Field(None, alias="suggestedActions")
```

### FeatureAnalysis (Output)

```python
class FeatureAnalysis(BaseModel):
    id: str
    feature_description: str = Field(..., alias="featureDescription")
    analysis_text: str = Field(..., alias="analysisText")
    created_at: datetime = Field(..., alias="createdAt")
```

---

## Subestruturas (Calculadas)

### TopContributor

```python
class TopContributor(BaseModel):
    name: str
    email: str
    commits: int
    percentage: int
```

### Hotspot

```python
class Hotspot(BaseModel):
    path: str
    changes: int
    last_modified: date = Field(..., alias="lastModified")
    contributors: int
```

### Technology

```python
class Technology(BaseModel):
    name: str
    level: int = Field(..., ge=0, le=100)
    files_count: int = Field(..., alias="filesCount")
    lines_changed: int = Field(..., alias="linesChanged")
```

### PersonRepository

```python
class PersonRepository(BaseModel):
    name: str
    repository_id: str = Field(..., alias="repositoryId")
    commits: int
    last_activity: date = Field(..., alias="lastActivity")
    expertise: int = Field(..., ge=0, le=100)
```

### FileChange

```python
class FileChange(BaseModel):
    path: str
    status: Literal["added", "modified", "deleted"]
```

---

## Enums

### ActivityLevel

```python
class ActivityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STALE = "stale"
```

### AlertSeverity

```python
class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
```

---

## Relacionamentos

```
Repository 1 ──< * Commit   (um repositório tem muitos commits)
Person     1 ──< * Commit   (uma pessoa faz muitos commits, via author_email)
Repository 1 ──< * Alert    (um repositório pode ter muitos alertas)
Person     1 ──< * Alert    (uma pessoa pode ter muitos alertas)
```

## Notas de Implementação

1. **Janela Móvel**: Queries de commits sempre usam `ORDER BY commit_date DESC LIMIT {WINDOW_SIZE}`
2. **camelCase vs snake_case**: Tabelas usam snake_case, API usa camelCase (via Pydantic alias)
3. **JSON Fields**: files_changed e parent_shas são armazenados como JSON no SQLite
4. **UUIDs**: Gerados com `uuid.uuid4()` para novas entidades
5. **Timestamps**: Sempre timezone-aware (UTC)
