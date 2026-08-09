"""Research gap detection (SKAI §9)."""

from __future__ import annotations

from axiom.skai.models import ConflictStatus, EntityType, ResearchGap, _new_id
from axiom.skai.store import SkaiStore


def detect_gaps(store: SkaiStore, *, campaign_id: str | None = None) -> list[ResearchGap]:
    """Inspect knowledge graph and generate research opportunities."""
    gaps: list[ResearchGap] = []
    entities = store.list_entities(limit=500)
    conflicts = store.list_conflicts(status=ConflictStatus.UNRESOLVED.value)

    # Unresolved conflicts → research tasks
    for conflict in conflicts:
        gap = ResearchGap(
            gap_id=_new_id("gap"),
            title=f"Resolve conflict: {conflict.claim_statement[:80]}",
            description="Unresolved knowledge conflict requires investigation",
            gap_type="unresolved_conflict",
            related_conflict_ids=[conflict.conflict_id],
            related_entity_ids=conflict.entity_ids,
            priority_score=0.8,
            evidence=conflict.evidence,
            campaign_id=campaign_id,
        )
        store.save_gap(gap)
        gaps.append(gap)

    # Open questions and conjectures
    for entity in entities:
        if entity.entity_type not in (EntityType.OPEN_QUESTION, EntityType.CONJECTURE):
            continue
        gap = ResearchGap(
            gap_id=_new_id("gap"),
            title=entity.title,
            description=entity.statement[:500],
            gap_type="open_question" if entity.entity_type == EntityType.OPEN_QUESTION else "unverified_conjecture",
            related_entity_ids=[entity.entity_id],
            priority_score=0.6,
            campaign_id=campaign_id,
        )
        store.save_gap(gap)
        gaps.append(gap)

    # Shared unresolved dependencies
    dep_counts: dict[str, int] = {}
    for rel in store.list_relations(limit=500):
        if rel.relation_type.value == "depends_on":
            dep_counts[rel.target_entity_id] = dep_counts.get(rel.target_entity_id, 0) + 1

    for entity_id, count in dep_counts.items():
        if count < 2:
            continue
        entity = store.get_entity(entity_id)
        if not entity:
            continue
        gap = ResearchGap(
            gap_id=_new_id("gap"),
            title=f"Bottleneck: {entity.title}",
            description=f"{count} results depend on this unresolved entity",
            gap_type="shared_dependency",
            related_entity_ids=[entity_id],
            priority_score=min(0.9, 0.4 + count * 0.1),
            campaign_id=campaign_id,
        )
        store.save_gap(gap)
        gaps.append(gap)

    return gaps
