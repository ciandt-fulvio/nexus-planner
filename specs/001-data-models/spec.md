# Feature Specification: Data Models e Persistência

**Feature Branch**: `001-data-models`
**Created**: 2025-12-13
**Status**: Draft
**Input**: User description: "Com base em docs/data_dictionary.md, criar estrutura de dados (e seus models) para obter, armazenar, gerar, calcular, fazer/atualizar cache, etc os dados da aplicação. Após esse trabalho, deve ser possível suprir as APIs atuais que hoje consomem dados mockados por dados reais. Thresholds devem ser configuráveis via .env"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar Repositórios com Dados Reais (Priority: P1)

Um usuário acessa o dashboard de repositórios e visualiza informações reais obtidas do Git (nome, descrição, commits, contribuidores) em vez de dados mockados.

**Why this priority**: É a funcionalidade central do produto. Sem dados reais de repositórios, o sistema não entrega valor. Esta é a fundação sobre a qual todas as outras funcionalidades são construídas.

**Independent Test**: Pode ser testado acessando a tela de repositórios e verificando que os dados exibidos correspondem aos repositórios Git reais configurados no sistema.

**Acceptance Scenarios**:

1. **Given** o sistema está conectado a repositórios Git, **When** o usuário acessa a lista de repositórios, **Then** os repositórios são exibidos com nome, descrição e métricas básicas reais
2. **Given** commits foram sincronizados, **When** o usuário visualiza um repositório, **Then** vê top contributors e hotspots calculados sobre os últimos N commits configurados
3. **Given** um repositório não tem commits recentes, **When** o usuário visualiza o repositório, **Then** o nível de atividade é exibido como LOW ou STALE conforme thresholds configurados

---

### User Story 2 - Visualizar Pessoas com Métricas Calculadas (Priority: P2)

Um usuário acessa o dashboard de pessoas e visualiza desenvolvedores com suas tecnologias, repositórios e níveis de expertise calculados a partir do histórico de commits.

**Why this priority**: Depende dos dados de commits já sincronizados (P1). Permite identificar especialistas e distribuição de conhecimento na equipe.

**Independent Test**: Pode ser testado acessando o perfil de um desenvolvedor e verificando que as tecnologias e níveis de expertise refletem os commits reais feitos por essa pessoa.

**Acceptance Scenarios**:

1. **Given** commits sincronizados contêm arquivos de diferentes tecnologias, **When** o usuário visualiza uma pessoa, **Then** vê as tecnologias detectadas com níveis de domínio calculados
2. **Given** uma pessoa contribuiu em múltiplos repositórios, **When** o usuário visualiza essa pessoa, **Then** vê a lista de repositórios com número de commits e expertise em cada um
3. **Given** uma pessoa não fez commits nos últimos 30 dias, **When** o usuário visualiza essa pessoa, **Then** a atividade recente é exibida como 0

---

### User Story 3 - Receber Alertas Gerados por IA (Priority: P3)

Um usuário visualiza alertas sobre riscos de conhecimento (concentração, inatividade, hotspots) gerados automaticamente pela IA para repositórios e pessoas.

**Why this priority**: Depende de dados calculados (P1 e P2) e requer integração com serviço de IA. Adiciona valor analítico sobre os dados básicos.

**Independent Test**: Pode ser testado visualizando alertas em um repositório com alta concentração de conhecimento e verificando que o alerta descreve corretamente o risco.

**Acceptance Scenarios**:

1. **Given** um repositório tem um contribuidor com mais de 70% dos commits, **When** alertas são gerados, **Then** um alerta crítico de concentração de conhecimento é exibido
2. **Given** alertas foram gerados para um repositório, **When** novos commits são sincronizados sem mudança na última PR, **Then** os alertas em cache são mantidos
3. **Given** a última PR mudou desde a geração de alertas, **When** o sistema verifica, **Then** novos alertas são regenerados pela IA

---

### User Story 4 - Obter Análise de Impacto de Feature (Priority: P4)

Um usuário descreve uma feature e recebe uma análise de impacto gerada por IA indicando repositórios afetados, pessoas recomendadas, riscos e ordem de implementação.

**Why this priority**: Funcionalidade avançada que depende de todas as anteriores. Requer dados completos de repositórios, pessoas e integração com IA.

**Independent Test**: Pode ser testado submetendo uma descrição de feature e verificando que a análise retornada menciona repositórios e pessoas relevantes ao contexto descrito.

**Acceptance Scenarios**:

1. **Given** o sistema tem dados de repositórios e pessoas, **When** o usuário descreve uma feature, **Then** recebe análise em texto Markdown com links dinâmicos
2. **Given** uma análise foi gerada, **When** o usuário visualiza, **Then** links como [repo:id:name] e [person:id:name] são renderizados como navegáveis
3. **Given** o usuário solicita nova análise, **When** a mesma é gerada, **Then** é armazenada com timestamp para histórico

---

### Edge Cases

- O que acontece quando não há commits em um repositório? Sistema exibe métricas zeradas e atividade STALE
- Como o sistema trata emails de autor duplicados com nomes diferentes? Consolida pela chave de email, usa o nome mais recente
- O que ocorre quando a API de IA não responde? Sistema mantém alertas em cache existentes e registra erro para retry posterior
- Como são tratados repositórios sem descrição? Campo descrição exibe vazio ou placeholder padrão

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE armazenar commits Git com todos os campos definidos no dicionário de dados (SHA, autor, arquivos, estatísticas)
- **FR-002**: Sistema DEVE calcular métricas de repositório (topContributors, hotspots, activity, knowledgeConcentration) sobre janela móvel dos últimos N commits
- **FR-003**: Sistema DEVE permitir configuração do tamanho da janela móvel via variável de ambiente WINDOW_SIZE (padrão: 300)
- **FR-004**: Sistema DEVE calcular nível de atividade (HIGH, MEDIUM, LOW, STALE) usando thresholds configuráveis via variáveis de ambiente
- **FR-005**: Sistema DEVE detectar tecnologias a partir das extensões de arquivos modificados nos commits
- **FR-006**: Sistema DEVE calcular nível de expertise de uma pessoa em um repositório baseado em commits, recência e arquivos únicos
- **FR-007**: Sistema DEVE armazenar alertas gerados por IA em cache, indexados por lastAlertsPRId ou lastAlertWasForCommitSha
- **FR-008**: Sistema DEVE regenerar alertas apenas quando o identificador de referência (PR ou commit) mudar
- **FR-009**: Sistema DEVE armazenar análises de feature com texto Markdown contendo links dinâmicos
- **FR-010**: Sistema DEVE parsear links dinâmicos no formato [tipo:id:nome] para renderização na interface
- **FR-011**: Sistema DEVE expor todos os endpoints de API atualmente existentes (repositórios, pessoas, análise) usando dados persistidos

### Thresholds Configuráveis (via .env)

- **WINDOW_SIZE**: Número de commits na janela móvel (padrão: 300)
- **ACTIVITY_HIGH_THRESHOLD**: Commits em 30 dias para atividade HIGH (padrão: 30)
- **ACTIVITY_MEDIUM_THRESHOLD**: Commits em 30 dias para atividade MEDIUM (padrão: 10)
- **ACTIVITY_LOW_THRESHOLD**: Commits em 30 dias para atividade LOW (padrão: 1)
- **CONCENTRATION_WARNING_THRESHOLD**: % de commits de único autor para alerta WARNING (padrão: 50)
- **CONCENTRATION_CRITICAL_THRESHOLD**: % de commits de único autor para alerta CRITICAL (padrão: 70)
- **TOP_CONTRIBUTORS_LIMIT**: Número de top contributors a exibir (padrão: 3)
- **TOP_HOTSPOTS_LIMIT**: Número de hotspots a exibir (padrão: 5)

### Key Entities

- **Commit**: Unidade base de armazenamento. Representa um commit Git com autor, data, mensagem, arquivos modificados e estatísticas de linhas.
- **Repository**: Agregação de métricas calculadas sobre commits. Contém informações do repositório Git e métricas derivadas (contributors, hotspots, activity).
- **Person**: Desenvolvedor identificado por email. Agrega commits de múltiplos repositórios, tecnologias detectadas e níveis de expertise.
- **Alert**: Insight gerado por IA sobre riscos ou informações relevantes. Estrutura JSON flexível com campos obrigatórios (id, title, description, severity) e opcionais (category, suggestedActions).
- **FeatureAnalysis**: Análise de impacto gerada por IA. Armazena descrição da feature e texto Markdown com análise completa.
- **TopContributor**: Subestrutura calculada. Lista os maiores contribuidores de um repositório na janela móvel.
- **Hotspot**: Subestrutura calculada. Lista os arquivos mais frequentemente modificados na janela móvel.
- **Technology**: Subestrutura calculada. Tecnologia detectada para uma pessoa com nível de domínio.
- **PersonRepository**: Subestrutura calculada. Relacionamento de uma pessoa com um repositório incluindo commits e expertise.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: APIs de repositórios e pessoas retornam dados reais em vez de mockados após implementação
- **SC-002**: Métricas calculadas (topContributors, hotspots, activity) refletem corretamente os dados dos commits armazenados
- **SC-003**: Mudança em qualquer threshold via .env altera o comportamento do cálculo sem necessidade de mudança de código
- **SC-004**: Alertas são regenerados apenas quando o identificador de referência muda, economizando chamadas à IA
- **SC-005**: Links dinâmicos em textos de alertas e análises são parseados corretamente pela interface
- **SC-006**: Sistema suporta armazenamento de pelo menos 1000 commits por repositório sem degradação perceptível de performance
- **SC-007**: Tempo de resposta das APIs de repositórios e pessoas permanece abaixo de 2 segundos com dados reais

## Assumptions

- A integração com APIs Git (GitHub, GitLab, Bitbucket) já está disponível ou será implementada em feature separada
- A integração com serviço de IA (OpenAI, Anthropic, etc.) será configurada via variáveis de ambiente
- O banco de dados utilizado suporta queries eficientes para janela móvel (ORDER BY + LIMIT)
- Os modelos Pydantic existentes serão adaptados/substituídos pelos novos modelos persistentes
- A migração de dados mockados para reais será gradual, permitindo fallback durante transição
