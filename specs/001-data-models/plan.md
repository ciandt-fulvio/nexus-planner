# Implementation Plan: Data Models e Persistência

**Branch**: `001-data-models` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-data-models/spec.md`

## Summary

Implementar camada de persistência com SQLite para armazenar commits Git e calcular métricas de repositórios e pessoas, substituindo dados mockados por dados reais. Arquitetura em camadas (db, models, services, routers) com thresholds configuráveis via .env.

## Technical Context

**Language/Version**: Python 3.13+ (conforme pyproject.toml existente)
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy (para ORM), aiosqlite (async SQLite)
**Storage**: SQLite (arquivo local) - conforme solicitado pelo usuário
**Testing**: pytest com pytest-asyncio para testes assíncronos
**Target Platform**: Linux/macOS server (backend API)
**Project Type**: Web application (backend FastAPI + frontend React)
**Performance Goals**: APIs < 2s response time com 1000+ commits/repositório
**Constraints**: Thresholds configuráveis via .env, janela móvel de N commits
**Scale/Scope**: Múltiplos repositórios Git, centenas de desenvolvedores, milhares de commits

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

- [x] **Principle I: Test-First (TDD/BDD)** - Testes definidos para cada camada antes da implementação
- [x] **Principle II: Fast Test Battery** - Testes unitários para models/services < 0.5s cada
- [x] **Principle III: Complete Test Battery** - Suite completa planejada: unit + integration + contract
- [x] **Principle IV: Frequent Commits** - Commits por camada: db → models → services → routers
- [x] **Principle V: Simplicity** - Arquitetura em camadas clara, funções < 30 linhas, files < 500 linhas

**Status**: ✅ Aprovado - Prosseguir para Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-data-models/
├── plan.md              # Este arquivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-v1.yaml      # OpenAPI spec
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/nexus_api/
│   ├── db/                    # Camada de banco de dados
│   │   ├── __init__.py
│   │   ├── database.py        # Engine SQLite, session factory
│   │   └── tables.py          # Definição de tabelas SQLAlchemy
│   │
│   ├── models/                # Modelos Pydantic (API/domain)
│   │   ├── __init__.py        # Exports públicos
│   │   ├── commit.py          # Commit model
│   │   ├── repository.py      # Repository model (existente, adaptar)
│   │   ├── person.py          # Person model (existente, adaptar)
│   │   ├── alert.py           # Alert model (novo, estrutura flexível)
│   │   └── analysis.py        # FeatureAnalysis model (existente, adaptar)
│   │
│   ├── services/              # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── commit_service.py  # CRUD commits, sync
│   │   ├── repository_service.py  # Cálculo métricas repositório
│   │   ├── person_service.py  # Cálculo métricas pessoa
│   │   ├── alert_service.py   # Cache e regeneração de alertas
│   │   └── metrics.py         # Funções de cálculo (activity, expertise)
│   │
│   ├── routers/               # Endpoints API (existente)
│   │   ├── repositories.py    # Adaptar para usar services
│   │   ├── people.py          # Adaptar para usar services
│   │   └── analysis.py        # Adaptar para usar services
│   │
│   ├── config.py              # Settings (existente, adicionar thresholds)
│   └── main.py                # FastAPI app (existente)
│
└── tests/
    ├── unit/
    │   ├── test_models.py     # Testes modelos Pydantic
    │   ├── test_metrics.py    # Testes funções cálculo
    │   └── test_services.py   # Testes services (mocked DB)
    │
    ├── integration/
    │   ├── test_db.py         # Testes SQLite real
    │   └── test_api.py        # Testes endpoints com DB
    │
    └── conftest.py            # Fixtures compartilhadas
```

**Structure Decision**: Arquitetura em camadas dentro do backend existente:
- **db/**: Abstração de acesso ao banco (SQLAlchemy + SQLite)
- **models/**: Schemas Pydantic para validação e serialização (API layer)
- **services/**: Lógica de negócio, cálculos, orquestração
- **routers/**: Endpoints HTTP (já existente, adaptar para injetar services)
