# Dicionário de Dados - Nexus Planner

Este documento descreve todos os campos de dados utilizados no Nexus Planner, organizados por estrutura.

## 0. Commit (Estrutura Base de Armazenamento)

Representa um commit Git armazenado no banco de dados para análises com janela móvel.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `id` | Identificador único do commit (SHA-1) | Git Integration | Git API: SHA do commit |
| `repositoryId` | ID do repositório ao qual pertence | Git Integration | Relacionamento com Repository |
| `authorName` | Nome do autor do commit | Git Integration | Git API: `commit.author.name` |
| `authorEmail` | Email do autor do commit | Git Integration | Git API: `commit.author.email` |
| `committerName` | Nome do committer | Git Integration | Git API: `commit.committer.name` |
| `committerEmail` | Email do committer | Git Integration | Git API: `commit.committer.email` |
| `authorDate` | Data de autoria do commit (formato ISO) | Git Integration | Git API: `commit.author.date` |
| `commitDate` | Data do commit (formato ISO) | Git Integration | Git API: `commit.committer.date` |
| `message` | Mensagem do commit | Git Integration | Git API: `commit.message` |
| `filesChanged` | Lista de arquivos modificados | Git Integration | Git API: arquivos no commit com status (added, modified, deleted) |
| `additions` | Número de linhas adicionadas | Git Integration | Git API: `stats.additions` |
| `deletions` | Número de linhas removidas | Git Integration | Git API: `stats.deletions` |
| `parentShas` | Lista de SHAs dos commits pais | Git Integration | Git API: `commit.parents` |

**Estratégia de Janela Móvel**:
- Ao alimentar a tabela, sempre trazer apenas os N commits mais recentes (configurável, ex: 300-1000)
- Commits armazenados permanecem no DB para histórico
- Métricas (hotspots, topContributors) calculadas sempre sobre os últimos N commits

## 1. Repository (Repositório)

Representa um repositório Git com métricas e análises.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `id` | Identificador único do repositório | Config | Gerado internamente ou UUID |
| `name` | Nome do repositório | Git Integration | Git API: `GET /repos/{owner}/{repo}` (campo `name`) |
| `description` | Descrição breve do propósito do repositório | Git Integration | Git API: `GET /repos/{owner}/{repo}` (campo `description`) |
| `lastCommit` | Data do commit mais recente (formato ISO) | Git Integration | Commit mais recente armazenado no DB (campo `commitDate`) |
| `totalCommits` | Número total de commits no repositório | Git Integration | Contagem de commits armazenados na janela móvel |
| `contributors` | Número total de contribuidores únicos | Calculado | Contagem de `authorEmail` únicos nos commits da janela |
| `activity` | Nível de atividade (HIGH, MEDIUM, LOW, STALE) | Calculado | Baseado em commits nos últimos 30 dias na janela móvel |
| `knowledgeConcentration` | Porcentagem de concentração de conhecimento (0-100) | Calculado | % de commits do maior contribuidor na janela móvel |
| `topContributors` | Lista dos 3 principais contribuidores | Calculado | Top 3 autores por commits na janela móvel (últimos N commits) |
| `hotspots` | Arquivos/paths com mais mudanças | Calculado | Top arquivos por modificações na janela móvel (últimos N commits) |
| `dependencies` | Lista de repositórios dependentes | Calculado | Análise de package.json, requirements.txt, go.mod |
| `alerts` | Alertas gerados por IA sobre o repositório | AI Generated | IA analisa métricas e retorna JSON flexível (cacheado em DB) |
| `lastAlertsWasForPRId` | ID da última PR usada na geração de alertas | Calculado | SHA ou ID da PR (NULL se nunca gerado). Regenerar se PR atual ≠ PR armazenada |

### 1.1 TopContributor (Contribuidor Principal)

Subestrutura de `Repository.topContributors`.

**Janela Móvel**: Calculado sobre os últimos N commits (ex: 300) armazenados no DB.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `name` | Nome do contribuidor | Git Integration | Campo `authorName` dos commits |
| `email` | Email do contribuidor | Git Integration | Campo `authorEmail` dos commits |
| `commits` | Número de commits na janela móvel | Calculado | Contagem de commits do autor na janela |
| `percentage` | Porcentagem de contribuições em relação ao total | Calculado | (commits do autor / total commits na janela) × 100 |

### 1.2 Hotspot (Arquivo com Alta Atividade)

Subestrutura de `Repository.hotspots`.

**Janela Móvel**: Calculado sobre os últimos N commits (ex: 300) armazenados no DB.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `path` | Caminho completo do arquivo no repositório | Git Integration | Campo `filesChanged` dos commits |
| `changes` | Número de vezes que o arquivo foi modificado | Calculado | Contagem de commits que modificaram este arquivo na janela |
| `lastModified` | Data da última modificação | Calculado | `commitDate` do commit mais recente que modificou o arquivo |
| `contributors` | Número de autores únicos que modificaram | Calculado | Contagem de `authorEmail` únicos nos commits do arquivo |

### 1.3 Alert (Alerta Gerado por IA)

Subestrutura de `Repository.alerts` e `Person.alerts`.

**Fonte**: Gerado por modelo de IA generativa (GPT-4, Claude, etc.) a partir de métricas.

**Cache**: Armazenado em DB e regerado quando `lastAlertsPRId` mudar.

**Estrutura JSON Simplificada**:

| Campo | Obrigatório | Descrição | Tipo | Exemplo |
|-------|-------------|-----------|------|---------|
| `id` | ✅ | Identificador único do alerta | String (UUID) | `"550e8400-e29b-41d4-a716-446655440000"` |
| `title` | ✅ | Título curto e descritivo do alerta | String (max 100 chars) | `"Concentração crítica de conhecimento"` |
| `description` | ✅ | Descrição detalhada em Markdown com links dinâmicos | String (Markdown) | Ver exemplo abaixo |
| `severity` | ✅ | Nível de criticidade | Enum: `info`, `warning`, `critical` | `"critical"` |
| `category` | ✅ | Categoria/tipo do alerta (lista no prompt da IA) | String | `"knowledge-concentration"`, `"inactivity"`, `"hotspot"` |
| `suggestedActions` | ❌ | Ações sugeridas em Markdown com links dinâmicos | String (Markdown) | Ver exemplo abaixo |

**Links Dinâmicos** (usados em `description` e `suggestedActions`):
- `[repo:{id}:{name}]` → Link para página do repositório
- `[person:{id}:{name}]` → Link para perfil da pessoa
- `[file:{repo}:{path}]` → Link para arquivo no repositório
- `[commit:{sha}]` → Link para commit
- `[tag:{name}]` → Tag/label colorida

**Exemplo de JSON de Alerta Completo**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Concentração crítica de conhecimento",
  "description": "[person:2:Marcos Oliveira] é responsável por **75% das alterações** em [repo:2:finance-core] nos últimos 300 commits. Sem atividade há **10 meses** desde [commit:a1b2c3d].\n\nArquivos críticos: [file:finance-core:src/ledger/transactions.ts], [file:finance-core:src/models/account.ts].\n\n[tag:risco-pessoa] [tag:ação-requerida]",
  "severity": "critical",
  "category": "knowledge-concentration",
  "suggestedActions": "- Agendar **pair programming** entre [person:2:Marcos Oliveira] e outro desenvolvedor\n- Criar documentação técnica do módulo [file:finance-core:src/ledger/]\n- Identificar backup person para [repo:2:finance-core]"
}
```

**Payload para IA** (dados enviados para gerar alertas):
```json
{
  "repository": {
    "name": "finance-core",
    "totalCommits": 300,
    "contributors": 5,
    "lastCommitDate": "2023-03-22",
    "topContributors": [...],
    "hotspots": [...],
    "dependencies": [...]
  },
  "context": {
    "currentDate": "2024-01-15",
    "organizationSize": 50,
    "projectCriticality": "high"
  },
  "availableCategories": [
    "knowledge-concentration",
    "inactivity",
    "hotspot",
    "dependency-risk",
    "high-activity"
  ]
}
```

## 2. Person (Pessoa/Desenvolvedor)

Representa um desenvolvedor com expertise e histórico.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `id` | Identificador único da pessoa | Config | Gerado internamente ou UUID |
| `name` | Nome completo do desenvolvedor | Git Integration | Extraído de `authorName` dos commits ou Git API user profile |
| `email` | Email do desenvolvedor | Git Integration | Campo `authorEmail` dos commits |
| `avatar` | Iniciais ou URL da imagem de avatar | Calculado/Git | Iniciais do nome ou Git API: user `avatar_url` |
| `repositories` | Lista de repositórios em que a pessoa contribui | Calculado | Agregação de commits por `repositoryId` para este `authorEmail` |
| `technologies` | Tecnologias que a pessoa domina com níveis | Calculado | Análise de extensões em `filesChanged` dos commits do autor |
| `domains` | Áreas de domínio/conhecimento | Calculado | Baseado em paths frequentes e descrições de repositórios |
| `recentActivity` | Número de commits nos últimos 30 dias | Calculado | Contagem de commits do autor nos últimos 30 dias |
| `alerts` | Alertas gerados por IA sobre a pessoa | AI Generated | IA analisa métricas e retorna JSON flexível (cacheado em DB) |
| `lastAlertWasForCommitSha` | SHA do último commit da pessoa | Git Integration | Buscar no DB o commit mais recente do autor (`id` do Commit) |


### 2.1 PersonRepository (Repositório da Pessoa)

Subestrutura de `Person.repositories`.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `name` | Nome do repositório | Git Integration | Nome do repositório onde a pessoa contribui |
| `repositoryId` | ID do repositório | Config | Relacionamento com Repository |
| `commits` | Número de commits da pessoa neste repositório | Calculado | Contagem de commits do autor no repositório (janela móvel) |
| `lastActivity` | Data do último commit da pessoa (formato ISO) | Calculado | `commitDate` do commit mais recente do autor |
| `expertise` | Nível de expertise (0-100) | Calculado | Score baseado em: commits, recência, arquivos únicos, complexidade |

### 2.2 Technology (Tecnologia)

Subestrutura de `Person.technologies`.

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `name` | Nome da tecnologia/linguagem | Calculado | Detectado por extensões (.ts, .py, .java) em `filesChanged` |
| `level` | Nível de domínio (0-100) | Calculado | Score baseado em commits, linhas modificadas, recência |
| `filesCount` | Número de arquivos únicos modificados | Calculado | Contagem de arquivos únicos desta tecnologia nos commits |
| `linesChanged` | Total de linhas modificadas (add + del) | Calculado | Soma de `additions` + `deletions` em arquivos desta tecnologia |

## 3. FeatureAnalysis (Análise de Feature)

Resultado da análise de impacto de uma nova feature, retornado como texto livre em Markdown com links dinâmicos.

**Estrutura Anêmica** (armazena apenas ID e texto):

| Campo | Descrição | Fonte | Como Obter/Calcular |
|-------|-----------|-------|---------------------|
| `id` | Identificador único da análise | Config | UUID gerado internamente |
| `featureDescription` | Descrição da feature fornecida pelo usuário | Config | Fornecido pelo usuário via interface |
| `analysisText` | Análise completa em Markdown com links dinâmicos | AI Generated | IA analisa repositórios, pessoas, commits e retorna texto formatado |
| `createdAt` | Data/hora de criação da análise | Config | Timestamp de criação |

**Links Dinâmicos** (usados em `analysisText`):
- `[repo:{id}:{name}]` → Link para página do repositório
- `[person:{id}:{name}]` → Link para perfil da pessoa
- `[file:{repo}:{path}]` → Link para arquivo no repositório
- `[commit:{sha}]` → Link para commit
- `[tag:{name}]` → Tag/label colorida

**Exemplo de `analysisText`**:
```markdown
# Análise de Impacto: Exportação de relatórios financeiros consolidados

## Repositórios Impactados

- **[repo:2:finance-core]** (confiança: 88%)
  Contém estruturas de dados financeiros necessárias para consolidação.
  Módulos críticos: [file:finance-core:src/ledger/transactions.ts], [file:finance-core:src/models/account.ts]

- **[repo:1:reports-service]** (confiança: 95%)
  Responsável pela geração e exportação de relatórios.
  Módulos críticos: [file:reports-service:src/exporters/pdf.ts], [file:reports-service:src/generators/financial.ts]

- **[repo:3:ui-dashboard]** (confiança: 82%)
  Interface para solicitação e visualização de relatórios.
  Módulos críticos: [file:ui-dashboard:src/pages/Reports.tsx]

## Pessoas Recomendadas

1. **[person:1:Ana Silva]** (relevância: 95%)
   Principal especialista em [repo:1:reports-service] com 271 commits. Mexeu 14 vezes no módulo de exportação.

2. **[person:2:Marcos Oliveira]** (relevância: 92%)
   Único especialista em [repo:2:finance-core], responsável por 75% das alterações. Conhecimento crítico sobre estruturas financeiras.

3. **[person:3:Clara Mendes]** (relevância: 85%)
   Principal autora em [repo:3:ui-dashboard]. Especialista em componentes de visualização.

## Riscos Identificados

- [tag:risco-alto] **Conhecimento obsoleto**: [repo:2:finance-core] sem mudanças há 10 meses desde [commit:a1b2c3d]
- [tag:risco-alto] **Concentração crítica**: [person:2:Marcos Oliveira] único especialista em módulo ledger
- [tag:risco-medio] **Dependência forte**: [repo:1:reports-service] e [repo:4:analytics-service] frequentemente mudam juntos
- [tag:risco-baixo] **Hotspot**: [file:reports-service:src/exporters/pdf.ts] com 124 alterações

## Ordem Sugerida de Implementação

1. **Revisar e atualizar modelos financeiros**
   Repositório: [repo:2:finance-core]
   Justificativa: Dependência ascendente - outros serviços dependem destas estruturas.

2. **Implementar agregação de dados consolidados**
   Repositório: [repo:4:analytics-service]
   Justificativa: Preparar dados que serão consumidos pelo serviço de relatórios.

3. **Desenvolver exportação consolidada**
   Repositório: [repo:1:reports-service]
   Justificativa: Implementar lógica principal usando dados consolidados.

4. **Criar interface de visualização**
   Repositório: [repo:3:ui-dashboard]
   Justificativa: Última camada - interface depende de serviços backend prontos.

## Recomendações Adicionais

- Criar documentação técnica do módulo [file:finance-core:src/ledger/] antes de iniciar
- Realizar pair programming entre [person:1:Ana Silva] e [person:2:Marcos Oliveira]
- Code review cruzado entre [person:4:Fernando Souza] e [person:1:Ana Silva]
- Implementar testes de integração entre [repo:1:reports-service] e [repo:4:analytics-service]
```

## Tipos Enum

### ActivityLevel (Nível de Atividade)

Classificação da atividade de um repositório baseada na janela móvel.

| Valor | Descrição | Critério (últimos 30 dias) |
|-------|-----------|----------|
| `HIGH` | Alta atividade | > 30 commits |
| `MEDIUM` | Atividade moderada | 10-30 commits |
| `LOW` | Baixa atividade | 1-10 commits |
| `STALE` | Sem atividade | 0 commits |

### AlertSeverity (Severidade de Alerta)

Classificação de alertas por severidade (usado em Alert.severity).

| Valor | Descrição | Cor Sugerida | Ação Esperada |
|-------|-----------|--------------|---------------|
| `info` | Informativo | Azul | Apenas informar |
| `warning` | Atenção | Amarelo | Monitorar |
| `critical` | Crítico | Vermelho | Ação imediata |

## Fontes de Dados

### Git Integration
Dados obtidos diretamente de plataformas Git via API REST e armazenados no DB.

**APIs principais**:
- GitHub API: `https://api.github.com/`
- GitLab API: `https://gitlab.com/api/v4/`
- Bitbucket API: `https://api.bitbucket.org/2.0/`

**Endpoints chave**:
- Commits: `GET /repos/{owner}/{repo}/commits`
- Detalhes do commit: `GET /repos/{owner}/{repo}/commits/{sha}`
- Repositório: `GET /repos/{owner}/{repo}`
- Usuário: `GET /users/{username}`

### Calculado
Dados derivados de análises e processamento de commits armazenados.

**Técnicas**:
- Agregações estatísticas sobre janela móvel
- Análise de padrões temporais
- Detecção de tecnologias por extensões de arquivo
- Scores de expertise e relevância

### AI Generated
Dados gerados por modelos de IA generativa (GPT-4, Claude, etc.).

**Modelos sugeridos**:
- OpenAI GPT-4 Turbo
- Anthropic Claude 3 Opus/Sonnet
- Google Gemini Pro

**Estratégia de Cache**:
- Armazenar em DB com timestamp de geração
- Invalidar cache quando repositório/pessoa mudar
- Regenerar sob demanda ou periodicamente

### Config (Configuração)
Dados fornecidos pelo usuário ou gerados internamente.

**Exemplos**:
- IDs únicos (UUIDs)
- Descrição de features
- Preferências de janela móvel (N commits)
- Configurações de threshold para alertas

## Estratégia de Janela Móvel

### Conceito
Para cálculos e consultas de métricas, utilizamos sempre os últimos N commits mais recentes, mantendo o histórico completo no banco de dados.

### Implementação

**Parâmetros configuráveis**:
- `WINDOW_SIZE`: Número de commits usados para cálculos (padrão: 300)
- `SYNC_BATCH_SIZE`: Commits buscados por vez (padrão: 100)
- `SYNC_INTERVAL`: Frequência de sincronização (padrão: diária)

**Fluxo de sincronização**:
1. Buscar commits mais recentes do repositório via Git API
2. Comparar com último commit armazenado no DB
3. Se houver novos commits:
   - Adicionar novos commits ao DB (histórico completo mantido)
   - Recalcular métricas usando os últimos `WINDOW_SIZE` commits
   - Verificar se `lastAlertsPRId` mudou
   - Se mudou, triggerar regeneração de alertas por IA

**Cálculos com janela móvel**:
- Sempre consultar os últimos N commits ordenados por `commitDate DESC`
- Métricas (hotspots, topContributors, activity) calculadas sobre esta janela
- Histórico completo disponível para análises profundas quando necessário

**Vantagens**:
- Performance: cálculos sobre conjunto fixo de commits
- Relevância: métricas refletem atividade recente
- Histórico: dados antigos preservados para auditoria
- Flexibilidade: ajustar `WINDOW_SIZE` sem perder dados

**Considerações**:
- Janelas maiores (500-1000) para projetos estáveis ou legacy
- Janelas menores (100-300) para projetos de rápida evolução
- Queries devem sempre incluir `ORDER BY commitDate DESC LIMIT {WINDOW_SIZE}`

## Notas de Implementação

1. **Datas**: Formato ISO 8601 (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SSZ)
2. **Porcentagens**: Valores 0-100 (inteiros)
3. **Scores**: Valores 0-100 (inteiros) para confidence, relevance, expertise, level
4. **Limites**: Top contributors 3-5, hotspots 3-5
5. **Cache de Commits**:
   - Histórico completo armazenado no DB
   - Métricas calculadas sempre sobre últimos N commits (janela móvel)
   - Queries devem usar `ORDER BY commitDate DESC LIMIT {WINDOW_SIZE}`
6. **Cache de Alertas**:
   - Alertas armazenados em DB com `lastAlertsPRId`
   - Regenerar quando `lastAlertsPRId` mudar (comparar PR atual com armazenada)
   - `lastAlertsPRId` pode ser NULL (nunca gerado)
7. **Atualização**:
   - Sincronização de commits: diária ou sob demanda (apenas adiciona novos)
   - Regeneração de alertas: quando `lastAlertsPRId` ≠ PR atual
   - Métricas: calculadas em tempo real sobre janela móvel
8. **IDs**: Usar UUIDs para entidades principais (Repository, Person, Alert, FeatureAnalysis)
9. **Relacionamentos**: Usar IDs para relacionar entidades (não duplicar dados)
10. **Markdown e Links**:
    - `Alert.description`, `Alert.suggestedActions`, `FeatureAnalysis.analysisText` são Markdown
    - Parser deve interpretar links dinâmicos: `[repo:{id}:{name}]`, `[person:{id}:{name}]`, etc.
11. **Monitoramento**: Logar chamadas à IA para auditoria, custos e debugging
