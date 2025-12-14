# Research: Data Models e Persistência

**Feature**: 001-data-models
**Date**: 2025-12-13
**Status**: Complete

## 1. SQLite vs SQLite-vec

### Decision
Usar **SQLite puro** (via SQLAlchemy + aiosqlite).

### Rationale
- SQLite-vec é focado em busca vetorial para embeddings/similaridade
- Nossa aplicação não requer busca vetorial - apenas queries SQL tradicionais
- SQLAlchemy oferece ORM maduro com suporte completo a SQLite
- aiosqlite permite operações assíncronas compatíveis com FastAPI
- SQLite é suficiente para escala esperada (milhares de commits por repositório)

### Alternatives Considered
1. **SQLite-vec**: Descartado - overhead desnecessário, focado em casos de uso de IA/ML
2. **PostgreSQL**: Descartado - complexidade de infraestrutura desnecessária para MVP
3. **MongoDB**: Descartado - dados são majoritariamente relacionais

## 2. ORM vs Raw SQL

### Decision
Usar **SQLAlchemy 2.0** com async support via aiosqlite.

### Rationale
- SQLAlchemy 2.0 oferece melhor type hints e integração com Pydantic
- Async sessions via aiosqlite são compatíveis com FastAPI async
- ORM simplifica queries complexas (joins, agregações)
- Migrations podem ser gerenciadas via Alembic (futuramente)
- Comunidade ativa e documentação extensa

### Alternatives Considered
1. **Raw SQL**: Descartado - mais verboso, propenso a SQL injection se mal utilizado
2. **Tortoise ORM**: Descartado - menos maduro que SQLAlchemy
3. **SQLModel**: Considerado - híbrido Pydantic+SQLAlchemy, mas adiciona camada extra

## 3. Arquitetura de Camadas

### Decision
Implementar **4 camadas** distintas: db → models → services → routers.

### Rationale
- **db/**: Isola acesso ao banco, facilita troca de database futuramente
- **models/**: Schemas Pydantic para API (request/response) e validação
- **services/**: Lógica de negócio pura, testável sem HTTP
- **routers/**: Thin layer, apenas HTTP handling e injeção de dependências

### Layer Responsibilities

| Camada | Responsabilidade | Dependências |
|--------|-----------------|--------------|
| db/ | Engine, sessions, tabelas SQLAlchemy | SQLAlchemy, aiosqlite |
| models/ | Schemas Pydantic, validação, serialização | Pydantic |
| services/ | Lógica de negócio, cálculos, orquestração | db/, models/ |
| routers/ | Endpoints HTTP, injeção de dependências | services/, models/ |

## 4. Tabelas SQLAlchemy vs Modelos Pydantic

### Decision
Manter **separação clara** entre tabelas (ORM) e schemas (Pydantic).

### Rationale
- Tabelas SQLAlchemy representam a estrutura do banco
- Modelos Pydantic representam contratos de API
- Separação permite evoluir banco e API independentemente
- Services fazem a conversão entre tabelas e schemas

### Implementation Pattern
```python
# db/tables.py - SQLAlchemy ORM
class CommitTable(Base):
    __tablename__ = "commits"
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    # ...

# models/commit.py - Pydantic Schema
class Commit(BaseModel):
    id: str
    repositoryId: str  # camelCase para API
    # ...

# services/commit_service.py - Conversão
def table_to_model(table: CommitTable) -> Commit:
    return Commit(id=table.id, repositoryId=table.repository_id, ...)
```

## 5. Thresholds via .env

### Decision
Usar **pydantic-settings** (já existente) para todos os thresholds.

### Rationale
- Padrão já estabelecido no projeto (config.py)
- Type-safe com validação automática
- Suporte a valores default
- Fácil override via variáveis de ambiente

### Implementation
```python
# config.py (adicionar a Settings existente)
class Settings(BaseSettings):
    # ... campos existentes ...

    # Thresholds para janela móvel
    window_size: int = 300

    # Thresholds para atividade (commits em 30 dias)
    activity_high_threshold: int = 30
    activity_medium_threshold: int = 10
    activity_low_threshold: int = 1

    # Thresholds para concentração de conhecimento
    concentration_warning_threshold: int = 50
    concentration_critical_threshold: int = 70

    # Limites de exibição
    top_contributors_limit: int = 3
    top_hotspots_limit: int = 5
```

## 6. Cálculo de Métricas

### Decision
Implementar funções puras em **services/metrics.py**.

### Rationale
- Funções puras são facilmente testáveis
- Sem dependência de banco - recebem dados, retornam resultados
- Reutilizáveis por diferentes services

### Key Functions
```python
# services/metrics.py

def calculate_activity_level(commits_last_30_days: int, settings: Settings) -> ActivityLevel:
    """Determina nível de atividade baseado em thresholds."""

def calculate_knowledge_concentration(top_contributor_percentage: int) -> int:
    """Retorna porcentagem de concentração (0-100)."""

def calculate_expertise(commits: int, recency_days: int, unique_files: int) -> int:
    """Calcula score de expertise (0-100) para pessoa em repositório."""

def detect_technologies(file_paths: list[str]) -> list[Technology]:
    """Detecta tecnologias a partir de extensões de arquivos."""
```

## 7. Cache de Alertas

### Decision
Armazenar alertas em **tabela dedicada** com referência a PR/commit.

### Rationale
- Alertas são gerados por IA (custo computacional)
- Cache evita regeneração desnecessária
- Invalidação baseada em mudança de PR/commit

### Implementation
```python
# db/tables.py
class AlertTable(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)  # UUID
    entity_type = Column(String)  # "repository" ou "person"
    entity_id = Column(String)
    reference_id = Column(String, nullable=True)  # PR ID ou commit SHA
    data = Column(JSON)  # Alert JSON flexível
    created_at = Column(DateTime)
```

## 8. Migrations Strategy

### Decision
**Não usar Alembic** inicialmente - criar tabelas via `create_all()`.

### Rationale
- MVP não requer migrations complexas
- Tabelas serão criadas do zero
- Alembic pode ser adicionado posteriormente quando necessário
- Simplifica setup inicial

### Future Considerations
- Adicionar Alembic antes de produção
- Gerar migrations a partir das tabelas existentes
- Manter histórico de schema changes

## 9. Async vs Sync

### Decision
Usar **operações async** com aiosqlite.

### Rationale
- FastAPI é async-first
- aiosqlite permite SQLite não bloqueante
- SQLAlchemy 2.0 suporta async sessions nativamente
- Melhor performance para I/O bound operations

### Pattern
```python
# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///nexus.db")
async_session = sessionmaker(engine, class_=AsyncSession)

# services/commit_service.py
async def get_commits(db: AsyncSession, repo_id: str, limit: int) -> list[CommitTable]:
    result = await db.execute(
        select(CommitTable)
        .where(CommitTable.repository_id == repo_id)
        .order_by(CommitTable.commit_date.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

## 10. Dependencies to Add

### New Dependencies (pyproject.toml)
```toml
[project.dependencies]
# ... existing ...
sqlalchemy = "^2.0"
aiosqlite = "^0.19"

[project.optional-dependencies]
dev = [
    # ... existing ...
    "pytest-asyncio>=0.21"
]
```

## Summary

| Aspect | Decision |
|--------|----------|
| Database | SQLite via SQLAlchemy + aiosqlite |
| ORM | SQLAlchemy 2.0 (async) |
| Architecture | 4 layers: db → models → services → routers |
| Schema Separation | Tables (ORM) ≠ Models (Pydantic) |
| Configuration | pydantic-settings para thresholds |
| Metrics | Funções puras em services/metrics.py |
| Alerts Cache | Tabela dedicada com referência a PR/commit |
| Migrations | create_all() inicial, Alembic futuro |
| Async | Sim, via aiosqlite |
