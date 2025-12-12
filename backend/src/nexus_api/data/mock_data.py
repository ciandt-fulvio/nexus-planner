"""
Mocked data for Nexus API.

Contains static data that mirrors frontend/src/data/mockData.ts.
This data is used by API endpoints until real database is implemented.

Sample input: N/A (data is static)
Expected output: Lists of Repository, Person, and FeatureAnalysis data
"""

from nexus_api.models import Alert, AlertType
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
            TopContributor(name="Ana Silva", percentage=32),
            TopContributor(name="Carlos Santos", percentage=28),
            TopContributor(name="Beatriz Lima", percentage=18),
        ],
        hotspots=[
            Hotspot(path="src/exporters/pdf.ts", changes=124),
            Hotspot(path="src/generators/financial.ts", changes=98),
            Hotspot(path="src/api/reports.controller.ts", changes=87),
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
            TopContributor(name="Marcos Oliveira", percentage=75),
            TopContributor(name="Paula Costa", percentage=15),
            TopContributor(name="Roberto Alves", percentage=10),
        ],
        hotspots=[
            Hotspot(path="src/ledger/transactions.ts", changes=203),
            Hotspot(path="src/models/account.ts", changes=156),
            Hotspot(path="src/calculations/balance.ts", changes=134),
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
            TopContributor(name="Clara Mendes", percentage=38),
            TopContributor(name="Diego Ferreira", percentage=24),
            TopContributor(name="Elena Rodrigues", percentage=19),
        ],
        hotspots=[
            Hotspot(path="src/pages/Reports.tsx", changes=178),
            Hotspot(path="src/components/Charts/FinancialChart.tsx", changes=145),
            Hotspot(path="src/components/Filters/DateRangePicker.tsx", changes=132),
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
            TopContributor(name="Fernando Souza", percentage=52),
            TopContributor(name="Gabriela Martins", percentage=28),
            TopContributor(name="Hugo Pereira", percentage=20),
        ],
        hotspots=[
            Hotspot(path="src/processors/metrics.ts", changes=89),
            Hotspot(path="src/aggregators/daily.ts", changes=76),
            Hotspot(path="src/api/analytics.controller.ts", changes=68),
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
            TopContributor(name="Igor Nascimento", percentage=68),
            TopContributor(name="Julia Campos", percentage=22),
            TopContributor(name="Lucas Barbosa", percentage=10),
        ],
        hotspots=[
            Hotspot(path="src/strategies/jwt.ts", changes=94),
            Hotspot(path="src/middleware/auth.ts", changes=82),
            Hotspot(path="src/services/token.service.ts", changes=71),
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


if __name__ == "__main__":
    import sys

    all_validation_failures: list[str] = []
    total_tests = 0

    # Test 1: Get all repositories returns 5
    total_tests += 1
    repos = get_all_repositories()
    if len(repos) != 5:
        all_validation_failures.append(
            f"get_all_repositories: Expected 5 repos, got {len(repos)}"
        )

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
            f"get_repository_by_id('999'): Expected None, got {repo}"
        )

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
        print(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)
