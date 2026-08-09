"""Literature saturation estimation (SKAI §10)."""

from __future__ import annotations

from axiom.skai.models import LiteratureCoverage
from axiom.skai.store import SkaiStore


SEARCH_STRATEGIES = [
    "direct_search",
    "citation_expansion",
    "related_work",
    "alternative_terminology",
    "historical_literature",
    "formal_libraries",
    "counterargument_search",
    "recent_developments",
]


def estimate_coverage(
    store: SkaiStore,
    research_question: str,
    *,
    strategies_used: list[str] | None = None,
) -> LiteratureCoverage:
    """Estimate literature coverage — scientifically honest, not 'retrieve 20 and done'."""
    used = strategies_used or ["direct_search"]
    sources = store.list_sources(limit=200)
    entities = store.list_entities(limit=500)

    # Heuristic coverage based on strategies used and knowledge found
    strategy_coverage = len(used) / len(SEARCH_STRATEGIES)
    entity_density = min(1.0, len(entities) / max(len(sources), 1) / 5.0) if sources else 0.0
    coverage = min(0.95, strategy_coverage * 0.5 + entity_density * 0.5)

    known_gaps: list[str] = []
    if "citation_expansion" not in used:
        known_gaps.append("citation chain not fully expanded")
    if "alternative_terminology" not in used:
        known_gaps.append("terminology ambiguity possible")
    if "recent_developments" not in used:
        known_gaps.append("recent literature may be missing")
    if "formal_libraries" not in used:
        known_gaps.append("formal library results not searched")
    if len(sources) < 3:
        known_gaps.append("low source count — coverage likely incomplete")

    return LiteratureCoverage(
        research_question=research_question,
        coverage_fraction=round(coverage, 2),
        sources_found=len(sources),
        sources_ingested=len(sources),
        known_gaps=known_gaps,
        search_strategies_used=used,
    )
