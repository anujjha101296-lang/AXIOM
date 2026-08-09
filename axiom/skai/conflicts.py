"""Knowledge conflict detection (SKAI §7)."""

from __future__ import annotations

from axiom.skai.models import ConflictStatus, KnowledgeConflict, KnowledgeEntity, RelationType, _new_id
from axiom.skai.store import SkaiStore


def detect_conflicts(store: SkaiStore) -> list[KnowledgeConflict]:
    """Detect contradictions and opposing positions in the knowledge graph."""
    entities = store.list_entities(limit=500)
    conflicts: list[KnowledgeConflict] = []
    seen: set[str] = set()

    # Find explicit CONTRADICTS/REFUTES relations
    for rel in store.list_relations(limit=500):
        if rel.relation_type not in (RelationType.CONTRADICTS, RelationType.REFUTES, RelationType.CHALLENGES):
            continue
        src = store.get_entity(rel.source_entity_id)
        tgt = store.get_entity(rel.target_entity_id)
        if not src or not tgt:
            continue
        key = tuple(sorted([src.entity_id, tgt.entity_id]))
        if key in seen:
            continue
        seen.add(key)

        conflict = KnowledgeConflict(
            conflict_id=_new_id("conf"),
            claim_statement=src.statement[:500],
            positions=[
                {"entity_id": src.entity_id, "position": "supports", "source_id": src.source_id},
                {"entity_id": tgt.entity_id, "position": "contradicts", "source_id": tgt.source_id},
            ],
            evidence=[rel.evidence] if rel.evidence else [],
            status=ConflictStatus.UNRESOLVED,
            entity_ids=[src.entity_id, tgt.entity_id],
        )
        store.save_conflict(conflict)
        conflicts.append(conflict)

    # Detect semantic opposition via statement keywords
    refute_words = ("false", "counterexample", "disproves", "refutes", "not true", "fails")
    for entity in entities:
        stmt_lower = entity.statement.lower()
        if not any(w in stmt_lower for w in refute_words):
            continue
        # Find related entities from same source that might be challenged
        related = [e for e in entities if e.source_id != entity.source_id and e.entity_type == entity.entity_type]
        for other in related[:3]:
            if _statements_overlap(entity.statement, other.statement):
                key = tuple(sorted([entity.entity_id, other.entity_id]))
                if key in seen:
                    continue
                seen.add(key)
                conflict = KnowledgeConflict(
                    conflict_id=_new_id("conf"),
                    claim_statement=other.statement[:500],
                    positions=[
                        {"entity_id": other.entity_id, "position": "claimed_true", "source_id": other.source_id},
                        {"entity_id": entity.entity_id, "position": "challenged", "source_id": entity.source_id},
                    ],
                    assumptions=["Keyword-based conflict detection — requires verification"],
                    status=ConflictStatus.REQUIRES_INVESTIGATION,
                    entity_ids=[entity.entity_id, other.entity_id],
                )
                store.save_conflict(conflict)
                conflicts.append(conflict)

    return conflicts


def _statements_overlap(a: str, b: str) -> bool:
    """Crude overlap check — shared significant words."""
    words_a = {w for w in a.lower().split() if len(w) > 4}
    words_b = {w for w in b.lower().split() if len(w) > 4}
    return len(words_a & words_b) >= 2
