# Quickstart: Data Models e Persistência

**Feature**: 001-data-models
**Date**: 2025-12-13

## Pré-requisitos

- Python 3.13+
- uv (package manager)
- Backend do Nexus Planner já configurado

## 1. Configuração de Thresholds

Adicione ao arquivo `backend/.env`:

```bash
# Janela móvel de commits
WINDOW_SIZE=300

# Thresholds de atividade (commits em 30 dias)
ACTIVITY_HIGH_THRESHOLD=30
ACTIVITY_MEDIUM_THRESHOLD=10
ACTIVITY_LOW_THRESHOLD=1

# Thresholds de concentração de conhecimento (%)
CONCENTRATION_WARNING_THRESHOLD=50
CONCENTRATION_CRITICAL_THRESHOLD=70

# Limites de exibição
TOP_CONTRIBUTORS_LIMIT=3
TOP_HOTSPOTS_LIMIT=5
```

## 2. Instalação de Dependências

```bash
cd backend
uv add sqlalchemy aiosqlite
uv add --dev pytest-asyncio
```

## 3. Inicialização do Banco de Dados

```bash
# O banco é criado automaticamente na primeira execução
cd backend
uv run uvicorn src.nexus_api.main:app --reload
```

Arquivo de banco: `backend/nexus.db`

## 4. Estrutura de Camadas

```
backend/src/nexus_api/
├── db/                    # Acesso ao banco
│   ├── database.py        # Engine, sessions
│   └── tables.py          # Tabelas SQLAlchemy
├── models/                # Schemas Pydantic
│   ├── commit.py
│   ├── repository.py
│   ├── person.py
│   └── alert.py
├── services/              # Lógica de negócio
│   ├── commit_service.py
│   ├── repository_service.py
│   ├── person_service.py
│   └── metrics.py
└── routers/               # Endpoints (existente)
```

## 5. Uso das APIs

### Listar Repositórios

```bash
curl http://localhost:8000/api/v1/repositories
```

Resposta:
```json
[
  {
    "id": "uuid",
    "name": "reports-service",
    "lastCommit": "2024-01-15",
    "totalCommits": 300,
    "activity": "high",
    "topContributors": [...],
    "hotspots": [...],
    "alerts": [...]
  }
]
```

### Obter Repositório

```bash
curl http://localhost:8000/api/v1/repositories/{id}
```

### Listar Pessoas

```bash
curl http://localhost:8000/api/v1/people
```

### Obter Pessoa

```bash
curl http://localhost:8000/api/v1/people/{id}
```

### Criar Análise de Feature

```bash
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{"featureDescription": "Implementar exportação de relatórios"}'
```

## 6. Executar Testes

```bash
cd backend

# Testes rápidos (< 5s)
uv run pytest tests/unit -v

# Todos os testes
uv run pytest -v

# Com cobertura
uv run pytest --cov=src/nexus_api
```

## 7. Alterar Thresholds

Basta modificar o `.env` e reiniciar o servidor:

```bash
# Exemplo: aumentar janela para 500 commits
WINDOW_SIZE=500
```

Não é necessário modificar código.

## 8. Links Dinâmicos

Alertas e análises contêm links no formato:

```markdown
[person:2:Marcos Oliveira] é responsável por 75% de [repo:2:finance-core]
```

O frontend deve parsear e renderizar como links navegáveis:

- `[repo:{id}:{name}]` → `/repositories/{id}`
- `[person:{id}:{name}]` → `/people/{id}`
- `[file:{repo}:{path}]` → Link para arquivo
- `[commit:{sha}]` → Link para commit
- `[tag:{name}]` → Badge colorida

## Troubleshooting

### Banco não é criado

Verifique permissões de escrita no diretório `backend/`.

### Métricas zeradas

1. Verifique se há commits sincronizados
2. Confirme que `WINDOW_SIZE` está configurado
3. Verifique logs para erros de cálculo

### Thresholds não aplicados

1. Reinicie o servidor após modificar `.env`
2. Verifique que as variáveis estão no formato correto (sem aspas)
