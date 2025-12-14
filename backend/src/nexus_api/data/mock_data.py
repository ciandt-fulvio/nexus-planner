"""
Mocked data for Nexus API.

Contains static data that mirrors frontend/src/data/mockData.ts.
This data is used by API endpoints until real database is implemented.

Sample input: N/A (data is static)
Expected output: Lists of Repository, Person, and FeatureAnalysis data
"""

from nexus_api.models import Alert, AlertType
from nexus_api.models.analysis import (
    FeatureAnalysis,
    ImpactedRepo,
    RecommendedPerson,
    Risk,
    RiskLevel,
    SuggestedStep,
)
from nexus_api.models.person import Person, PersonRepository, Technology
from nexus_api.models.repository import (
    ActivityLevel,
    Hotspot,
    Repository,
    TopContributor,
)

# Repository mocked data - exactly matches frontend/src/data/mockData.ts
REPOSITORIES: list[Repository] = [
    Repository(
        id="1",
        name="reports-service",
        description="Serviço de geração e exportação de relatórios",
        lastCommit="2024-01-15",
        totalCommits=847,
        contributors=8,
        activity=ActivityLevel.HIGH,
        knowledgeConcentration=45,
        topContributors=[
            TopContributor(name="Ana Silva", email="ana.silva@company.com", commits=271, percentage=32),
            TopContributor(name="Carlos Santos", email="carlos.santos@company.com", commits=237, percentage=28),
            TopContributor(name="Beatriz Lima", email="beatriz.lima@company.com", commits=153, percentage=18),
        ],
        hotspots=[
            Hotspot(path="src/exporters/pdf.ts", changes=124, lastModified="2024-01-15", contributors=4),
            Hotspot(path="src/generators/financial.ts", changes=98, lastModified="2024-01-12", contributors=3),
            Hotspot(path="src/api/reports.controller.ts", changes=87, lastModified="2024-01-10", contributors=5),
        ],
        dependencies=["finance-core", "analytics-service"],
        alerts=[
            Alert(
                type=AlertType.INFO,
                message="Alta atividade recente - 47 commits nos últimos 30 dias",
            ),
            Alert(
                type=AlertType.WARNING,
                message="Forte dependência com analytics-service - mudanças costumam ocorrer juntas",
            ),
        ],
    ),
    Repository(
        id="2",
        name="finance-core",
        description="Núcleo de lógica financeira e contábil",
        lastCommit="2023-03-22",
        totalCommits=1243,
        contributors=5,
        activity=ActivityLevel.STALE,
        knowledgeConcentration=75,
        topContributors=[
            TopContributor(name="Marcos Oliveira", email="marcos.oliveira@company.com", commits=932, percentage=75),
            TopContributor(name="Paula Costa", email="paula.costa@company.com", commits=186, percentage=15),
            TopContributor(name="Roberto Alves", email="roberto.alves@company.com", commits=124, percentage=10),
        ],
        hotspots=[
            Hotspot(path="src/ledger/transactions.ts", changes=203, lastModified="2023-03-22", contributors=2),
            Hotspot(path="src/models/account.ts", changes=156, lastModified="2023-03-15", contributors=2),
            Hotspot(path="src/calculations/balance.ts", changes=134, lastModified="2023-03-10", contributors=1),
        ],
        dependencies=["database-layer"],
        alerts=[
            Alert(
                type=AlertType.DANGER,
                message="Repositório sem alterações há 10 meses - risco de conhecimento obsoleto",
            ),
            Alert(
                type=AlertType.DANGER,
                message="Marcos Oliveira responsável por 75% das alterações - concentração crítica",
            ),
            Alert(
                type=AlertType.WARNING,
                message="Módulo ledger/ tem apenas 1 pessoa ativa historicamente",
            ),
        ],
    ),
    Repository(
        id="3",
        name="ui-dashboard",
        description="Interface web do dashboard principal",
        lastCommit="2024-01-18",
        totalCommits=2156,
        contributors=12,
        activity=ActivityLevel.HIGH,
        knowledgeConcentration=38,
        topContributors=[
            TopContributor(name="Clara Mendes", email="clara.mendes@company.com", commits=819, percentage=38),
            TopContributor(name="Diego Ferreira", email="diego.ferreira@company.com", commits=517, percentage=24),
            TopContributor(name="Elena Rodrigues", email="elena.rodrigues@company.com", commits=410, percentage=19),
        ],
        hotspots=[
            Hotspot(path="src/pages/Reports.tsx", changes=178, lastModified="2024-01-18", contributors=6),
            Hotspot(path="src/components/Charts/FinancialChart.tsx", changes=145, lastModified="2024-01-17", contributors=4),
            Hotspot(path="src/components/Filters/DateRangePicker.tsx", changes=132, lastModified="2024-01-15", contributors=5),
        ],
        dependencies=["reports-service", "auth-service"],
        alerts=[
            Alert(
                type=AlertType.INFO,
                message="Boa distribuição de conhecimento entre 12 contribuidores",
            ),
            Alert(
                type=AlertType.WARNING,
                message="Componente FinancialChart.tsx modificado frequentemente - possível hotspot de bugs",
            ),
        ],
    ),
    Repository(
        id="4",
        name="analytics-service",
        description="Processamento e análise de dados",
        lastCommit="2024-01-10",
        totalCommits=634,
        contributors=6,
        activity=ActivityLevel.MEDIUM,
        knowledgeConcentration=52,
        topContributors=[
            TopContributor(name="Fernando Souza", email="fernando.souza@company.com", commits=330, percentage=52),
            TopContributor(name="Gabriela Martins", email="gabriela.martins@company.com", commits=178, percentage=28),
            TopContributor(name="Hugo Pereira", email="hugo.pereira@company.com", commits=126, percentage=20),
        ],
        hotspots=[
            Hotspot(path="src/processors/metrics.ts", changes=89, lastModified="2024-01-10", contributors=3),
            Hotspot(path="src/aggregators/daily.ts", changes=76, lastModified="2024-01-08", contributors=2),
            Hotspot(path="src/api/analytics.controller.ts", changes=68, lastModified="2024-01-05", contributors=4),
        ],
        dependencies=["database-layer", "cache-service"],
        alerts=[
            Alert(
                type=AlertType.WARNING,
                message="Fernando Souza é responsável por mais de 50% das alterações",
            ),
            Alert(
                type=AlertType.INFO,
                message="Atividade moderada - 18 commits nos últimos 30 dias",
            ),
        ],
    ),
    Repository(
        id="5",
        name="auth-service",
        description="Autenticação e autorização",
        lastCommit="2023-11-30",
        totalCommits=456,
        contributors=4,
        activity=ActivityLevel.LOW,
        knowledgeConcentration=68,
        topContributors=[
            TopContributor(name="Igor Nascimento", email="igor.nascimento@company.com", commits=310, percentage=68),
            TopContributor(name="Julia Campos", email="julia.campos@company.com", commits=100, percentage=22),
            TopContributor(name="Lucas Barbosa", email="lucas.barbosa@company.com", commits=46, percentage=10),
        ],
        hotspots=[
            Hotspot(path="src/strategies/jwt.ts", changes=94, lastModified="2023-11-30", contributors=2),
            Hotspot(path="src/middleware/auth.ts", changes=82, lastModified="2023-11-28", contributors=3),
            Hotspot(path="src/services/token.service.ts", changes=71, lastModified="2023-11-25", contributors=2),
        ],
        dependencies=["database-layer"],
        alerts=[
            Alert(
                type=AlertType.WARNING,
                message="Sem commits há 2 meses - atividade baixa",
            ),
            Alert(
                type=AlertType.DANGER,
                message="Igor Nascimento detém 68% do conhecimento - risco de concentração",
            ),
        ],
    ),
]


def get_all_repositories() -> list[Repository]:
    """Return all mocked repositories."""
    return REPOSITORIES


def get_repository_by_id(repo_id: str) -> Repository | None:
    """Return a repository by ID, or None if not found."""
    for repo in REPOSITORIES:
        if repo.id == repo_id:
            return repo
    return None


# People mocked data - exactly matches frontend/src/data/mockData.ts
PEOPLE: list[Person] = [
    Person(
        id="1",
        name="Ana Silva",
        email="ana.silva@company.com",
        avatar="AS",
        repositories=[
            PersonRepository(
                name="reports-service", commits=271, lastActivity="2024-01-15", expertise=95
            ),
            PersonRepository(
                name="ui-dashboard", commits=89, lastActivity="2024-01-12", expertise=65
            ),
            PersonRepository(
                name="analytics-service", commits=34, lastActivity="2023-12-20", expertise=40
            ),
        ],
        technologies=[
            Technology(name="TypeScript", level=95),
            Technology(name="Node.js", level=90),
            Technology(name="React", level=75),
            Technology(name="PostgreSQL", level=70),
        ],
        domains=["Relatórios", "Exportação de Dados", "APIs REST"],
        recentActivity=47,
        alerts=[
            Alert(
                type=AlertType.INFO,
                message="Principal especialista em reports-service com 271 commits",
            ),
            Alert(
                type=AlertType.WARNING,
                message="Conhecimento concentrado em poucos repositórios - considerar diversificação",
            ),
        ],
    ),
    Person(
        id="2",
        name="Marcos Oliveira",
        email="marcos.oliveira@company.com",
        avatar="MO",
        repositories=[
            PersonRepository(
                name="finance-core", commits=932, lastActivity="2023-03-22", expertise=98
            ),
            PersonRepository(
                name="database-layer", commits=156, lastActivity="2023-04-10", expertise=75
            ),
            PersonRepository(
                name="reports-service", commits=45, lastActivity="2023-02-15", expertise=35
            ),
        ],
        technologies=[
            Technology(name="Java", level=98),
            Technology(name="Spring Boot", level=95),
            Technology(name="SQL", level=92),
            Technology(name="Contabilidade", level=88),
        ],
        domains=["Finanças", "Contabilidade", "Transações", "Ledger"],
        recentActivity=0,
        alerts=[
            Alert(
                type=AlertType.DANGER,
                message="Único especialista em finance-core - risco crítico de concentração",
            ),
            Alert(
                type=AlertType.DANGER,
                message="Sem atividade há 10 meses - conhecimento pode estar desatualizado",
            ),
            Alert(
                type=AlertType.WARNING, message="Responsável por 75% das alterações em finance-core"
            ),
        ],
    ),
    Person(
        id="3",
        name="Clara Mendes",
        email="clara.mendes@company.com",
        avatar="CM",
        repositories=[
            PersonRepository(
                name="ui-dashboard", commits=819, lastActivity="2024-01-18", expertise=96
            ),
            PersonRepository(
                name="design-system", commits=234, lastActivity="2024-01-16", expertise=85
            ),
            PersonRepository(
                name="reports-service", commits=67, lastActivity="2024-01-10", expertise=45
            ),
        ],
        technologies=[
            Technology(name="React", level=98),
            Technology(name="TypeScript", level=95),
            Technology(name="CSS/Tailwind", level=92),
            Technology(name="UX/UI", level=88),
        ],
        domains=["Interface", "Componentes", "Visualização de Dados", "UX"],
        recentActivity=52,
        alerts=[
            Alert(
                type=AlertType.INFO,
                message="Principal desenvolvedora frontend com alta atividade recente",
            ),
            Alert(
                type=AlertType.INFO, message="Boa distribuição entre ui-dashboard e design-system"
            ),
        ],
    ),
    Person(
        id="4",
        name="Fernando Souza",
        email="fernando.souza@company.com",
        avatar="FS",
        repositories=[
            PersonRepository(
                name="analytics-service", commits=330, lastActivity="2024-01-10", expertise=92
            ),
            PersonRepository(
                name="data-pipeline", commits=178, lastActivity="2024-01-08", expertise=80
            ),
            PersonRepository(
                name="reports-service", commits=89, lastActivity="2023-12-28", expertise=55
            ),
        ],
        technologies=[
            Technology(name="Python", level=95),
            Technology(name="Node.js", level=85),
            Technology(name="Data Analysis", level=92),
            Technology(name="SQL", level=88),
        ],
        domains=["Analytics", "Processamento de Dados", "Métricas", "ETL"],
        recentActivity=28,
        alerts=[
            Alert(
                type=AlertType.WARNING,
                message="Responsável por 52% das alterações em analytics-service",
            ),
            Alert(type=AlertType.INFO,
                  message="Especialista em processamento e análise de dados"),
        ],
    ),
    Person(
        id="5",
        name="Diego Ferreira",
        email="diego.ferreira@company.com",
        avatar="DF",
        repositories=[
            PersonRepository(
                name="ui-dashboard", commits=517, lastActivity="2024-01-17", expertise=88
            ),
            PersonRepository(
                name="mobile-app", commits=298, lastActivity="2024-01-14", expertise=82
            ),
            PersonRepository(
                name="auth-service", commits=45, lastActivity="2023-11-20", expertise=40
            ),
        ],
        technologies=[
            Technology(name="React", level=90),
            Technology(name="React Native", level=88),
            Technology(name="TypeScript", level=85),
            Technology(name="GraphQL", level=75),
        ],
        domains=["Frontend", "Mobile", "Componentes", "State Management"],
        recentActivity=41,
        alerts=[
            Alert(type=AlertType.INFO,
                  message="Forte atuação em frontend web e mobile"),
            Alert(type=AlertType.INFO,
                  message="Bom complemento de conhecimento com Clara Mendes"),
        ],
    ),
]


def get_all_people() -> list[Person]:
    """Return all mocked people."""
    return PEOPLE


def get_person_by_id(person_id: str) -> Person | None:
    """Return a person by ID, or None if not found."""
    for person in PEOPLE:
        if person.id == person_id:
            return person
    return None


# Example analysis - exactly matches frontend/src/data/mockData.ts
EXAMPLE_ANALYSIS = FeatureAnalysis(
    feature="Implementar suporte a exportação de relatórios financeiros consolidados",
    impactedRepos=[
        ImpactedRepo(
            name="reports-service",
            confidence=95,
            reasoning="Forte histórico de commits contendo 'report', 'export', 'finance'. Responsável pela geração e exportação de relatórios.",
            modules=[
                "src/exporters/",
                "src/generators/financial.ts",
                "src/api/reports.controller.ts",
            ],
        ),
        ImpactedRepo(
            name="finance-core",
            confidence=88,
            reasoning="Contém estruturas de dados financeiros e lógica de consolidação usadas em relatórios.",
            modules=["src/ledger/", "src/calculations/balance.ts",
                     "src/models/account.ts"],
        ),
        ImpactedRepo(
            name="ui-dashboard",
            confidence=82,
            reasoning="Interface responsável por telas de relatórios, filtros e visualização de dados financeiros.",
            modules=["src/pages/Reports.tsx",
                     "src/components/Charts/", "src/components/Filters/"],
        ),
        ImpactedRepo(
            name="analytics-service",
            confidence=65,
            reasoning="Pode ser necessário para agregação de dados consolidados antes da exportação.",
            modules=["src/aggregators/", "src/processors/metrics.ts"],
        ),
    ],
    recommendedPeople=[
        RecommendedPerson(
            name="Ana Silva",
            relevance=95,
            reasoning="Principal especialista em reports-service com 271 commits. Mexeu 14 vezes no módulo de exportação nos últimos 6 meses.",
        ),
        RecommendedPerson(
            name="Marcos Oliveira",
            relevance=92,
            reasoning="Único especialista em finance-core, responsável por 75% das alterações. Conhecimento crítico sobre estruturas financeiras.",
        ),
        RecommendedPerson(
            name="Clara Mendes",
            relevance=85,
            reasoning="Principal autora das últimas alterações em ui-dashboard. Especialista em componentes de visualização de dados.",
        ),
        RecommendedPerson(
            name="Fernando Souza",
            relevance=70,
            reasoning="Especialista em analytics-service. Pode auxiliar na agregação de dados consolidados.",
        ),
    ],
    risks=[
        Risk(
            type=RiskLevel.HIGH,
            message="finance-core não recebe mudanças há 10 meses - risco de conhecimento obsoleto e possíveis incompatibilidades",
        ),
        Risk(
            type=RiskLevel.HIGH,
            message="Apenas Marcos Oliveira fez 75% das alterações no módulo ledger/ - concentração crítica de conhecimento",
        ),
        Risk(
            type=RiskLevel.MEDIUM,
            message="reports-service tem forte dependência histórica com analytics-service - mudanças podem impactar ambos",
        ),
        Risk(
            type=RiskLevel.MEDIUM,
            message="Módulo de exportação em reports-service é um hotspot com 124 alterações - área sensível a bugs",
        ),
        Risk(
            type=RiskLevel.LOW,
            message="ui-dashboard tem boa distribuição de conhecimento, mas componente FinancialChart.tsx é frequentemente modificado",
        ),
    ],
    suggestedOrder=[
        SuggestedStep(
            step=1,
            action="Revisão e atualização do modelo de dados financeiros",
            repository="finance-core",
            reasoning="Dependência ascendente - outros serviços dependem destas estruturas. Necessário garantir compatibilidade antes de prosseguir.",
        ),
        SuggestedStep(
            step=2,
            action="Implementar lógica de consolidação e agregação",
            repository="analytics-service",
            reasoning="Preparar dados consolidados que serão consumidos pelo serviço de relatórios.",
        ),
        SuggestedStep(
            step=3,
            action="Desenvolver nova funcionalidade de exportação consolidada",
            repository="reports-service",
            reasoning="Implementar a lógica principal de exportação usando dados consolidados.",
        ),
        SuggestedStep(
            step=4,
            action="Criar interface e componentes de visualização",
            repository="ui-dashboard",
            reasoning="Última camada - interface depende dos serviços backend estarem prontos.",
        ),
    ],
    additionalRecommendations=[
        "Criar documentação técnica do módulo ledger/ em finance-core antes de iniciar alterações",
        "Realizar pair programming entre Ana Silva e Marcos Oliveira para transferência de conhecimento sobre finance-core",
        "Considerar code review cruzado entre Fernando Souza e Ana Silva para reduzir concentração de conhecimento",
        "Implementar testes de integração entre reports-service e analytics-service devido à forte dependência",
        "Agendar sessão de alinhamento técnico com Clara Mendes antes de iniciar trabalho no frontend",
    ],
)


def get_example_analysis() -> FeatureAnalysis:
    """Return the static example analysis."""
    return EXAMPLE_ANALYSIS


if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: Get all repositories returns 5
    total_tests += 1
    repos = get_all_repositories()
    if len(repos) != 5:
        all_validation_failures.append(
            f"get_all_repositories: Expected 5 repos, got {len(repos)}")

    # Test 2: First repo is reports-service
    total_tests += 1
    first_repo = repos[0]
    if first_repo.name != "reports-service":
        all_validation_failures.append(
            f"First repo: Expected 'reports-service', got '{first_repo.name}'"
        )

    # Test 3: Get repository by ID
    total_tests += 1
    repo = get_repository_by_id("1")
    if repo is None or repo.name != "reports-service":
        all_validation_failures.append(
            f"get_repository_by_id('1'): Expected 'reports-service', got {repo}"
        )

    # Test 4: Get repository by invalid ID returns None
    total_tests += 1
    repo = get_repository_by_id("999")
    if repo is not None:
        all_validation_failures.append(
            f"get_repository_by_id('999'): Expected None, got {repo}")

    # Test 5: Repository data matches frontend mock
    total_tests += 1
    repo = get_repository_by_id("1")
    if repo:
        if repo.totalCommits != 847:
            all_validation_failures.append(
                f"reports-service totalCommits: Expected 847, got {repo.totalCommits}"
            )
        if len(repo.topContributors) != 3:
            all_validation_failures.append(
                f"reports-service topContributors: Expected 3, got {len(repo.topContributors)}"
            )
        if repo.topContributors[0].name != "Ana Silva":
            all_validation_failures.append(
                f"reports-service first contributor: Expected 'Ana Silva', got '{repo.topContributors[0].name}'"
            )

    # Final validation result
    if all_validation_failures:
        print(
            f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:"
        )
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(
            f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
