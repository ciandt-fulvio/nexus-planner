# Database Schema - Nexus Planner

Arquitetura simplificada: **SQLite** com suporte JSON nativo e cache em memória (Python dict).

**Arquivo**: `nexus_planner.db`

---

## 1. Tabelas

### 1.1 `repositories`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | UUID do repositório | Repository.id |
| `name` | TEXT | NOT NULL | Nome do repositório | Repository.name |
| `description` | TEXT | NULL | Descrição do propósito | Repository.description |
| `git_url` | TEXT | NOT NULL | URL do repositório Git | - |
| `last_commit_date` | TEXT | NULL | ISO timestamp do último commit | Repository.lastCommit |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de criação | - |
| `updated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de atualização | - |

**Índices**:
```sql
CREATE INDEX idx_repositories_name ON repositories(name);
CREATE INDEX idx_repositories_last_commit_date ON repositories(last_commit_date);
```

**Campos Calculados** (não armazenados, calculados em tempo real com cache em memória):
- `totalCommits` – COUNT de commits na janela móvel
- `contributors` – COUNT DISTINCT de author_email na janela móvel
- `activity` – Baseado em commits nos últimos 30 dias
- `knowledgeConcentration` – % do maior contribuidor
- `topContributors` – Top 3-5 autores por commits
- `hotspots` – Top arquivos por modificações
- `dependencies` – Análise de package.json, requirements.txt, go.mod

**Campos Gerados por IA** (armazenados em tabela separada):
- `alerts` – Tabela `repository_alerts`

---

### 1.2 `commits`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | SHA-1 do commit | Commit.id |
| `repository_id` | TEXT | NOT NULL | FK à repositories(id) | Commit.repositoryId |
| `author_name` | TEXT | NOT NULL | Nome do autor | Commit.authorName |
| `author_email` | TEXT | NOT NULL | Email do autor | Commit.authorEmail |
| `committer_name` | TEXT | NOT NULL | Nome do committer | Commit.committerName |
| `committer_email` | TEXT | NOT NULL | Email do committer | Commit.committerEmail |
| `author_date` | TEXT | NOT NULL | ISO timestamp de autoria | Commit.authorDate |
| `commit_date` | TEXT | NOT NULL | ISO timestamp do commit | Commit.commitDate |
| `message` | TEXT | NOT NULL | Mensagem do commit | Commit.message |
| `additions` | INTEGER | NOT NULL DEFAULT 0 | Linhas adicionadas | Commit.additions |
| `deletions` | INTEGER | NOT NULL DEFAULT 0 | Linhas removidas | Commit.deletions |
| `parent_shas` | TEXT | NOT NULL DEFAULT '[]' | JSON array de SHAs pais | Commit.parentShas |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de ingestão | - |

**Índices**:
```sql
CREATE INDEX idx_commits_repository_id ON commits(repository_id);
CREATE INDEX idx_commits_commit_date ON commits(commit_date DESC);
CREATE INDEX idx_commits_author_email ON commits(author_email);
CREATE INDEX idx_commits_repo_date ON commits(repository_id, commit_date DESC);
```

**Foreign Key**:
```sql
FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
```

---

### 1.3 `commit_files`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID único | - |
| `commit_id` | TEXT | NOT NULL | FK à commits(id) | - |
| `file_path` | TEXT | NOT NULL | Caminho completo do arquivo | Commit.filesChanged[].path |
| `status` | TEXT | NOT NULL CHECK (status IN ('added', 'modified', 'deleted')) | Status da modificação | Commit.filesChanged[].status |
| `additions` | INTEGER | NOT NULL DEFAULT 0 | Linhas adicionadas | - |
| `deletions` | INTEGER | NOT NULL DEFAULT 0 | Linhas removidas | - |

**Índices**:
```sql
CREATE INDEX idx_commit_files_commit_id ON commit_files(commit_id);
CREATE INDEX idx_commit_files_file_path ON commit_files(file_path);
CREATE INDEX idx_commit_files_status ON commit_files(status);
```

**Foreign Key**:
```sql
FOREIGN KEY (commit_id) REFERENCES commits(id) ON DELETE CASCADE
```

---

### 1.4 `people`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | UUID da pessoa | Person.id |
| `name` | TEXT | NOT NULL | Nome completo | Person.name |
| `email` | TEXT | NOT NULL UNIQUE | Email (identificador único) | Person.email |
| `avatar` | TEXT | NULL | Iniciais ou URL do avatar | Person.avatar |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de criação | - |
| `updated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de atualização | - |

**Índices**:
```sql
CREATE UNIQUE INDEX idx_people_email ON people(email);
CREATE INDEX idx_people_name ON people(name);
```

**Campos Calculados** (não armazenados, calculados em tempo real com cache em memória):
- `repositories` – Agregação de commits por repositório
- `technologies` – Análise de extensões de arquivo
- `domains` – Baseado em paths frequentes
- `recentActivity` – Commits nos últimos 30 dias

**Campos Gerados por IA** (armazenados em tabela separada):
- `alerts` – Tabela `person_alerts`

---

### 1.5 `feature_analyses`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | UUID da análise | FeatureAnalysis.id |
| `feature_description` | TEXT | NOT NULL | Descrição da feature | FeatureAnalysis.featureDescription |
| `analysis_text` | TEXT | NULL | Markdown com análise completa | FeatureAnalysis.analysisText |
| `metadata` | TEXT | NULL | JSON com repos, pessoas, riscos | - |
| `created_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Data de criação | FeatureAnalysis.createdAt |

**Índices**:
```sql
CREATE INDEX idx_feature_analyses_created_at ON feature_analyses(created_at DESC);
```

**Estrutura do campo `metadata`** (JSON):
```json
{
  "impactedRepositories": [
    {"id": "...", "name": "finance-core", "confidence": 88}
  ],
  "recommendedPeople": [
    {"id": "...", "name": "Ana Silva", "relevance": 95}
  ],
  "risksCount": 4,
  "estimatedComplexity": "high"
}
```

---

### 1.6 `repository_alerts`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | UUID do registro | - |
| `repository_id` | TEXT | NOT NULL | FK à repositories(id) | - |
| `alerts` | TEXT | NOT NULL | JSON array de alertas | Repository.alerts |
| `last_pr_id` | TEXT | NULL | SHA/ID da última PR | Repository.lastAlertsWasForPRId |
| `generated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Timestamp de geração | - |
| `context_hash` | TEXT | NOT NULL | Hash MD5 do contexto | - |

**Estrutura do campo `alerts`** (JSON Array):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Concentração crítica de conhecimento",
    "description": "[person:2:Marcos Oliveira] é responsável por **75% das alterações**...",
    "severity": "critical",
    "category": "knowledge-concentration",
    "suggestedActions": "- Agendar pair programming..."
  }
]
```

**Mapeamento de Alert**:
- `id` – Alert.id
- `title` – Alert.title
- `description` – Alert.description (Markdown)
- `severity` – Alert.severity (info, warning, critical)
- `category` – Alert.category
- `suggestedActions` – Alert.suggestedActions (Markdown, opcional)

**Índices**:
```sql
CREATE INDEX idx_repository_alerts_repo_id ON repository_alerts(repository_id);
CREATE INDEX idx_repository_alerts_generated_at ON repository_alerts(generated_at DESC);
```

**Foreign Key**:
```sql
FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
```

---

### 1.7 `person_alerts`

| Coluna | Tipo | Restrições | Descrição | Fonte (data_dictionary.md) |
|--------|------|------------|-----------|----------------------------|
| `id` | TEXT | PRIMARY KEY | UUID do registro | - |
| `person_id` | TEXT | NOT NULL | FK à people(id) | - |
| `alerts` | TEXT | NOT NULL | JSON array de alertas | Person.alerts |
| `last_commit_sha` | TEXT | NULL | SHA do último commit | Person.lastAlertWasForCommitSha |
| `generated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Timestamp de geração | - |
| `context_hash` | TEXT | NOT NULL | Hash MD5 do contexto | - |

**Estrutura do campo `alerts`**: Mesma estrutura de `repository_alerts.alerts`

**Índices**:
```sql
CREATE INDEX idx_person_alerts_person_id ON person_alerts(person_id);
CREATE INDEX idx_person_alerts_generated_at ON person_alerts(generated_at DESC);
```

**Foreign Key**:
```sql
FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
```

---

### 1.8 `app_settings`

Configurações da aplicação (window_size, thresholds, etc.).

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `key` | TEXT | PRIMARY KEY | Chave de configuração |
| `value` | TEXT | NOT NULL | JSON value |
| `updated_at` | TEXT | NOT NULL DEFAULT (datetime('now')) | Timestamp de atualização |

**Exemplos de configurações**:
```sql
INSERT INTO app_settings (key, value) VALUES
  ('window_size_default', '{"value": 300}'),
  ('activity_thresholds', '{"HIGH": 30, "MEDIUM": 10, "LOW": 1}'),
  ('cache_ttl_seconds', '{"metrics": 3600, "technologies": 7200}'),
  ('ai_model', '{"provider": "openai", "model": "gpt-4-turbo"}');
```

---

## 2. Cache em Memória (Python)

Métricas calculadas são cacheadas em memória usando dicionário Python com TTL.

### 2.1 Estrutura de Cache

```python
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

class SimpleCache:
    """Cache em memória com TTL"""
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}

    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        self._cache[key] = (value, datetime.now())

    def invalidate(self, pattern: str):
        """Invalida chaves que começam com pattern"""
        keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

# Instância global
cache = SimpleCache()
```

### 2.2 Chaves de Cache

**Repository Metrics**:
- `repo:metrics:{repository_id}` → `{"totalCommits": 450, "contributors": 12, "activity": "HIGH", "knowledgeConcentration": 75}`

**Repository Top Contributors**:
- `repo:topcontributors:{repository_id}` → `[{"name": "Ana", "email": "...", "commits": 135, "percentage": 45.0}]`

**Repository Hotspots**:
- `repo:hotspots:{repository_id}` → `[{"path": "src/core.py", "changes": 124, "lastModified": "...", "contributors": 8}]`

**Repository Dependencies**:
- `repo:dependencies:{repository_id}` → `[{"repositoryId": "...", "name": "analytics-service", "type": "internal"}]`

**Person Metrics**:
- `person:metrics:{person_id}` → `{"recentActivity": 18, "totalCommits": 450}`

**Person Technologies**:
- `person:technologies:{person_id}` → `[{"name": "Python", "level": 95, "filesCount": 284, "linesChanged": 12450}]`

**Person Repositories**:
- `person:repositories:{person_id}` → `[{"repositoryId": "...", "name": "nexus-planner", "commits": 135, "expertise": 92}]`

**Person Domains**:
- `person:domains:{person_id}` → `["Authentication", "Payment Processing"]`

### 2.3 Invalidação de Cache

Quando novos commits são adicionados:
```python
def on_commit_added(repository_id: str, author_email: str):
    # Invalida cache do repositório
    cache.invalidate(f"repo:{repository_id}")

    # Invalida cache da pessoa
    person = get_person_by_email(author_email)
    if person:
        cache.invalidate(f"person:{person.id}")
```

---

## 3. Queries Comuns

### 3.1 Obter Commits da Janela Móvel

```sql
-- Buscar últimos N commits de um repositório
-- N vem de app_settings (window_size_default)
SELECT *
FROM commits
WHERE repository_id = ?
ORDER BY commit_date DESC
LIMIT ?;
```

### 3.2 Calcular Top Contributors

```sql
-- Top 5 contribuidores na janela móvel
WITH recent_commits AS (
  SELECT *
  FROM commits
  WHERE repository_id = ?
  ORDER BY commit_date DESC
  LIMIT ?
)
SELECT
  author_name,
  author_email,
  COUNT(*) as commits,
  ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM recent_commits)), 2) as percentage
FROM recent_commits
GROUP BY author_name, author_email
ORDER BY commits DESC
LIMIT 5;
```

### 3.3 Calcular Hotspots

```sql
-- Top 10 arquivos mais modificados na janela móvel
WITH recent_commits AS (
  SELECT id
  FROM commits
  WHERE repository_id = ?
  ORDER BY commit_date DESC
  LIMIT ?
)
SELECT
  cf.file_path,
  COUNT(*) as changes,
  MAX(c.commit_date) as last_modified,
  COUNT(DISTINCT c.author_email) as contributors
FROM commit_files cf
JOIN commits c ON cf.commit_id = c.id
WHERE c.id IN (SELECT id FROM recent_commits)
GROUP BY cf.file_path
ORDER BY changes DESC
LIMIT 10;
```

### 3.4 Calcular Person Technologies

```sql
-- Tecnologias de uma pessoa (baseado em extensões)
WITH person_commits AS (
  SELECT id
  FROM commits
  WHERE author_email = ?
  ORDER BY commit_date DESC
  LIMIT ?
),
file_extensions AS (
  SELECT
    LOWER(SUBSTR(cf.file_path, INSTR(cf.file_path, '.') + 1)) as ext,
    SUM(cf.additions + cf.deletions) as lines_changed,
    COUNT(DISTINCT cf.file_path) as files_count
  FROM commit_files cf
  WHERE cf.commit_id IN (SELECT id FROM person_commits)
  GROUP BY ext
)
SELECT
  CASE ext
    WHEN 'py' THEN 'Python'
    WHEN 'ts' THEN 'TypeScript'
    WHEN 'js' THEN 'JavaScript'
    WHEN 'java' THEN 'Java'
    WHEN 'go' THEN 'Go'
    ELSE ext
  END as name,
  files_count,
  lines_changed,
  MIN(100, CAST((files_count * 10 + lines_changed / 100.0) AS INTEGER)) as level
FROM file_extensions
WHERE ext IS NOT NULL
ORDER BY lines_changed DESC
LIMIT 10;
```

### 3.5 Buscar Alertas (usando JSON functions)

```sql
-- Alertas críticos de um repositório
SELECT
  id,
  json_extract(value, '$.title') as title,
  json_extract(value, '$.severity') as severity,
  json_extract(value, '$.description') as description
FROM repository_alerts,
     json_each(repository_alerts.alerts)
WHERE repository_id = ?
  AND json_extract(value, '$.severity') = 'critical'
ORDER BY generated_at DESC;
```

---

## 4. Mapeamento Completo: data_dictionary.md ↔ database.md

### Commit

| Campo (data_dictionary.md) | Armazenamento | Localização |
|----------------------------|---------------|-------------|
| `id` | SQLite | `commits.id` |
| `repositoryId` | SQLite | `commits.repository_id` |
| `authorName` | SQLite | `commits.author_name` |
| `authorEmail` | SQLite | `commits.author_email` |
| `committerName` | SQLite | `commits.committer_name` |
| `committerEmail` | SQLite | `commits.committer_email` |
| `authorDate` | SQLite | `commits.author_date` |
| `commitDate` | SQLite | `commits.commit_date` |
| `message` | SQLite | `commits.message` |
| `filesChanged` | SQLite | `commit_files` (tabela relacionada) |
| `additions` | SQLite | `commits.additions` |
| `deletions` | SQLite | `commits.deletions` |
| `parentShas` | SQLite (JSON) | `commits.parent_shas` |

### Repository

| Campo (data_dictionary.md) | Armazenamento | Localização |
|----------------------------|---------------|-------------|
| `id` | SQLite | `repositories.id` |
| `name` | SQLite | `repositories.name` |
| `description` | SQLite | `repositories.description` |
| `lastCommit` | SQLite | `repositories.last_commit_date` |
| `totalCommits` | Cache (memória) | `cache["repo:metrics:{id}"].totalCommits` |
| `contributors` | Cache (memória) | `cache["repo:metrics:{id}"].contributors` |
| `activity` | Cache (memória) | `cache["repo:metrics:{id}"].activity` |
| `knowledgeConcentration` | Cache (memória) | `cache["repo:metrics:{id}"].knowledgeConcentration` |
| `topContributors` | Cache (memória) | `cache["repo:topcontributors:{id}"]` |
| `hotspots` | Cache (memória) | `cache["repo:hotspots:{id}"]` |
| `dependencies` | Cache (memória) | `cache["repo:dependencies:{id}"]` |
| `alerts` | SQLite (JSON) | `repository_alerts.alerts` |
| `lastAlertsWasForPRId` | SQLite | `repository_alerts.last_pr_id` |

### Person

| Campo (data_dictionary.md) | Armazenamento | Localização |
|----------------------------|---------------|-------------|
| `id` | SQLite | `people.id` |
| `name` | SQLite | `people.name` |
| `email` | SQLite | `people.email` |
| `avatar` | SQLite | `people.avatar` |
| `repositories` | Cache (memória) | `cache["person:repositories:{id}"]` |
| `technologies` | Cache (memória) | `cache["person:technologies:{id}"]` |
| `domains` | Cache (memória) | `cache["person:domains:{id}"]` |
| `recentActivity` | Cache (memória) | `cache["person:metrics:{id}"].recentActivity` |
| `alerts` | SQLite (JSON) | `person_alerts.alerts` |
| `lastAlertWasForCommitSha` | SQLite | `person_alerts.last_commit_sha` |

### FeatureAnalysis

| Campo (data_dictionary.md) | Armazenamento | Localização |
|----------------------------|---------------|-------------|
| `id` | SQLite | `feature_analyses.id` |
| `featureDescription` | SQLite | `feature_analyses.feature_description` |
| `analysisText` | SQLite | `feature_analyses.analysis_text` |
| `createdAt` | SQLite | `feature_analyses.created_at` |

---

## 5. Schema SQL Completo

```sql
-- repositories
CREATE TABLE repositories (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  git_url TEXT NOT NULL,
  last_commit_date TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_repositories_name ON repositories(name);
CREATE INDEX idx_repositories_last_commit_date ON repositories(last_commit_date);

-- commits
CREATE TABLE commits (
  id TEXT PRIMARY KEY,
  repository_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  author_email TEXT NOT NULL,
  committer_name TEXT NOT NULL,
  committer_email TEXT NOT NULL,
  author_date TEXT NOT NULL,
  commit_date TEXT NOT NULL,
  message TEXT NOT NULL,
  additions INTEGER NOT NULL DEFAULT 0,
  deletions INTEGER NOT NULL DEFAULT 0,
  parent_shas TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
CREATE INDEX idx_commits_repository_id ON commits(repository_id);
CREATE INDEX idx_commits_commit_date ON commits(commit_date DESC);
CREATE INDEX idx_commits_author_email ON commits(author_email);
CREATE INDEX idx_commits_repo_date ON commits(repository_id, commit_date DESC);

-- commit_files
CREATE TABLE commit_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  commit_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('added', 'modified', 'deleted')),
  additions INTEGER NOT NULL DEFAULT 0,
  deletions INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (commit_id) REFERENCES commits(id) ON DELETE CASCADE
);
CREATE INDEX idx_commit_files_commit_id ON commit_files(commit_id);
CREATE INDEX idx_commit_files_file_path ON commit_files(file_path);
CREATE INDEX idx_commit_files_status ON commit_files(status);

-- people
CREATE TABLE people (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  avatar TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX idx_people_email ON people(email);
CREATE INDEX idx_people_name ON people(name);

-- feature_analyses
CREATE TABLE feature_analyses (
  id TEXT PRIMARY KEY,
  feature_description TEXT NOT NULL,
  analysis_text TEXT,
  metadata TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_feature_analyses_created_at ON feature_analyses(created_at DESC);

-- repository_alerts
CREATE TABLE repository_alerts (
  id TEXT PRIMARY KEY,
  repository_id TEXT NOT NULL,
  alerts TEXT NOT NULL,
  last_pr_id TEXT,
  generated_at TEXT NOT NULL DEFAULT (datetime('now')),
  context_hash TEXT NOT NULL,
  FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);
CREATE INDEX idx_repository_alerts_repo_id ON repository_alerts(repository_id);
CREATE INDEX idx_repository_alerts_generated_at ON repository_alerts(generated_at DESC);

-- person_alerts
CREATE TABLE person_alerts (
  id TEXT PRIMARY KEY,
  person_id TEXT NOT NULL,
  alerts TEXT NOT NULL,
  last_commit_sha TEXT,
  generated_at TEXT NOT NULL DEFAULT (datetime('now')),
  context_hash TEXT NOT NULL,
  FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
);
CREATE INDEX idx_person_alerts_person_id ON person_alerts(person_id);
CREATE INDEX idx_person_alerts_generated_at ON person_alerts(generated_at DESC);

-- app_settings
CREATE TABLE app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Configurações iniciais
INSERT INTO app_settings (key, value) VALUES
  ('window_size_default', '{"value": 300}'),
  ('activity_thresholds', '{"HIGH": 30, "MEDIUM": 10, "LOW": 1}'),
  ('cache_ttl_seconds', '{"metrics": 3600, "technologies": 7200}'),
  ('ai_model', '{"provider": "openai", "model": "gpt-4-turbo"}');
```
