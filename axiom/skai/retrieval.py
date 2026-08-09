"""Reasoning-aware knowledge retrieval (SKAI §17)."""

from __future__ import annotations

from axiom.skai.models import EntityType, KnowledgeEntity
from axiom.skai.store import SkaiStore


RESEARCH_REQUIREMENTS: dict[str, list[EntityType]] = {
    "prove_theorem": [
        EntityType.DEFINITION, EntityType.THEOREM, EntityType.LEMMA,
        EntityType.COUNTEREXAMPLE, EntityType.METHOD, EntityType.OPEN_QUESTION,
    ],
    "reproduce_experiment": [
        EntityType.HYPOTHESIS, EntityType.METHOD, EntityType.EXPERIMENT,
        EntityType.DATASET, EntityType.RESULT, EntityType.LIMITATION,
    ],
    "survey_literature": [
        EntityType.THEOREM, EntityType.CONJECTURE, EntityType.OPEN_QUESTION,
        EntityType.RESULT, EntityType.LIMITATION,
    ],
}


def retrieve_for_research(
    store: SkaiStore,
    research_goal: str,
    *,
    goal_type: str = "prove_theorem",
    campaign_id: str | None = None,
    limit: int = 50,
) -> dict:
    """
    Retrieve based on research requirements, not just semantic similarity.

    Returns structured knowledge needed to pursue the research goal.
    """
    required_types = RESEARCH_REQUIREMENTS.get(goal_type, RESEARCH_REQUIREMENTS["survey_literature"])
    entities = store.list_entities(limit=limit * 2)

    if campaign_id:
        entities = [e for e in entities if e.campaign_id == campaign_id or e.campaign_id is None]

    # Score by relevance to goal keywords
    goal_words = {w.lower() for w in research_goal.split() if len(w) > 3}
    scored: list[tuple[float, KnowledgeEntity]] = []
    for entity in entities:
        if entity.entity_type not in required_types:
            continue
        stmt_words = {w.lower() for w in (entity.title + " " + entity.statement).split() if len(w) > 3}
        overlap = len(goal_words & stmt_words)
        score = overlap * 0.3 + entity.confidence * 0.4 + (0.3 if entity.entity_type in required_types[:3] else 0.1)
        scored.append((score, entity))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [e for _, e in scored[:limit]]

    conflicts = store.list_conflicts(status="unresolved", limit=10)
    gaps = store.list_gaps(campaign_id=campaign_id, limit=10)

    return {
        "research_goal": research_goal,
        "goal_type": goal_type,
        "required_entity_types": [t.value for t in required_types],
        "entities": [e.to_dict() for e in selected],
        "entity_count": len(selected),
        "unresolved_conflicts": [c.to_dict() for c in conflicts],
        "research_gaps": [g.to_dict() for g in gaps],
        "retrieval_method": "reasoning_aware_requirements",
    }
