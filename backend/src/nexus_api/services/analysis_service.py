"""
Analysis service for creating feature impact analyses.

Provides async functions for creating and saving feature analyses.
Analyses are based on repository and person data from the database.

Docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Sample input: Feature description string
Expected output: FeatureAnalysis Pydantic model
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_api.db.tables import CommitTable, FeatureAnalysisTable, PersonTable, RepositoryTable
from nexus_api.models.analysis import (
    FeatureAnalysis,
    ImpactedRepo,
    RecommendedPerson,
    Risk,
    RiskLevel,
    SuggestedStep,
)


async def _get_active_repositories(
    db: AsyncSession,
) -> list[dict]:
    """
    Get repositories with recent activity.

    Args:
        db: Async database session

    Returns:
        List of dicts with repo info and commit counts
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    stmt = (
        select(
            RepositoryTable.id,
            RepositoryTable.name,
            func.count(CommitTable.id).label("commit_count"),
        )
        .join(CommitTable, CommitTable.repository_id == RepositoryTable.id)
        .where(CommitTable.commit_date >= thirty_days_ago)
        .group_by(RepositoryTable.id, RepositoryTable.name)
        .order_by(func.count(CommitTable.id).desc())
        .limit(10)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"id": row.id, "name": row.name, "commit_count": row.commit_count}
        for row in rows
    ]


async def _get_active_contributors(
    db: AsyncSession,
) -> list[dict]:
    """
    Get contributors with recent activity.

    Args:
        db: Async database session

    Returns:
        List of dicts with contributor info and commit counts
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    stmt = (
        select(
            PersonTable.id,
            PersonTable.name,
            PersonTable.email,
            func.count(CommitTable.id).label("commit_count"),
        )
        .join(CommitTable, CommitTable.author_email == PersonTable.email)
        .where(CommitTable.commit_date >= thirty_days_ago)
        .group_by(PersonTable.id, PersonTable.name, PersonTable.email)
        .order_by(func.count(CommitTable.id).desc())
        .limit(10)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"id": row.id, "name": row.name, "email": row.email, "commit_count": row.commit_count}
        for row in rows
    ]


async def create_analysis(
    db: AsyncSession,
    feature_description: str,
) -> FeatureAnalysis:
    """
    Create a feature impact analysis based on repository and person data.

    Args:
        db: Async database session
        feature_description: Description of the feature to analyze

    Returns:
        FeatureAnalysis Pydantic model with impact assessment
    """
    # Get active repositories
    active_repos = await _get_active_repositories(db)

    # Get active contributors
    active_contributors = await _get_active_contributors(db)

    # Build impacted repos list
    impacted_repos = []
    for i, repo in enumerate(active_repos[:5]):  # Top 5 repos
        confidence = max(95 - (i * 15), 40)  # Decreasing confidence
        impacted_repos.append(
            ImpactedRepo(
                name=repo["name"],
                confidence=confidence,
                reasoning=f"Repositório ativo com {repo['commit_count']} commits recentes",
                modules=["src/"],
            )
        )

    # Build recommended people list
    recommended_people = []
    for i, person in enumerate(active_contributors[:5]):  # Top 5 contributors
        relevance = max(95 - (i * 15), 40)
        recommended_people.append(
            RecommendedPerson(
                name=person["name"],
                relevance=relevance,
                reasoning=f"Contribuidor ativo com {person['commit_count']} commits recentes",
            )
        )

    # Generate risks based on data
    risks = []
    if len(active_repos) == 0:
        risks.append(
            Risk(
                type=RiskLevel.HIGH,
                message="Nenhum repositório com atividade recente identificado",
            )
        )
    elif len(active_repos) < 3:
        risks.append(
            Risk(
                type=RiskLevel.MEDIUM,
                message="Poucos repositórios ativos identificados",
            )
        )

    if len(active_contributors) == 0:
        risks.append(
            Risk(
                type=RiskLevel.HIGH,
                message="Nenhum contribuidor ativo identificado",
            )
        )
    elif len(active_contributors) < 3:
        risks.append(
            Risk(
                type=RiskLevel.MEDIUM,
                message="Equipe reduzida para implementação",
            )
        )

    # Generate suggested steps
    suggested_steps = []
    for i, repo in enumerate(impacted_repos[:3]):
        suggested_steps.append(
            SuggestedStep(
                step=i + 1,
                action=f"Revisar e atualizar {repo.name}",
                repository=repo.name,
                reasoning=repo.reasoning,
            )
        )

    # Additional recommendations
    recommendations = [
        "Sincronize todos os repositórios antes de iniciar a implementação",
        "Consulte os especialistas identificados para validar a análise",
    ]

    return FeatureAnalysis(
        feature=feature_description,
        impactedRepos=impacted_repos,
        recommendedPeople=recommended_people,
        risks=risks,
        suggestedOrder=suggested_steps,
        additionalRecommendations=recommendations,
    )


async def save_analysis(
    db: AsyncSession,
    analysis: FeatureAnalysis,
) -> FeatureAnalysisTable:
    """
    Save a feature analysis to the database.

    Args:
        db: Async database session
        analysis: FeatureAnalysis Pydantic model to save

    Returns:
        Saved FeatureAnalysisTable instance
    """
    # Convert analysis to markdown-like text
    analysis_text = _format_analysis_as_markdown(analysis)

    table_entry = FeatureAnalysisTable(
        id=str(uuid.uuid4()),
        feature_description=analysis.feature,
        analysis_text=analysis_text,
    )

    db.add(table_entry)
    await db.commit()
    await db.refresh(table_entry)

    return table_entry


def _format_analysis_as_markdown(analysis: FeatureAnalysis) -> str:
    """
    Format a FeatureAnalysis as Markdown text.

    Args:
        analysis: FeatureAnalysis model

    Returns:
        Markdown-formatted analysis text
    """
    lines = [
        f"# Análise de Impacto: {analysis.feature}",
        "",
        "## Repositórios Impactados",
        "",
    ]

    for repo in analysis.impactedRepos:
        lines.append(f"- **{repo.name}** (Confiança: {repo.confidence}%)")
        lines.append(f"  - {repo.reasoning}")
        lines.append(f"  - Módulos: {', '.join(repo.modules)}")
        lines.append("")

    lines.append("## Pessoas Recomendadas")
    lines.append("")

    for person in analysis.recommendedPeople:
        lines.append(f"- **{person.name}** (Relevância: {person.relevance}%)")
        lines.append(f"  - {person.reasoning}")
        lines.append("")

    lines.append("## Riscos Identificados")
    lines.append("")

    for risk in analysis.risks:
        lines.append(f"- [{risk.type.value.upper()}] {risk.message}")

    lines.append("")
    lines.append("## Ordem Sugerida de Implementação")
    lines.append("")

    for step in analysis.suggestedOrder:
        lines.append(f"{step.step}. **{step.action}** ({step.repository})")
        lines.append(f"   - {step.reasoning}")
        lines.append("")

    lines.append("## Recomendações Adicionais")
    lines.append("")

    for rec in analysis.additionalRecommendations:
        lines.append(f"- {rec}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("✅ analysis_service module loaded successfully")
