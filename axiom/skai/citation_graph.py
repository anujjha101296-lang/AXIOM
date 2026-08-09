"""Citation graph construction (SKAI §6)."""

from __future__ import annotations

from axiom.skai.models import KnowledgeEntity, KnowledgeRelation, RelationType, _new_id
from axiom.skai.store import SkaiStore


def build_citation_relations(
    store: SkaiStore,
    citing_source_id: str,
    citation_keys: list[str],
    *,
    cited_source_map: dict[str, str] | None = None,
) -> list[KnowledgeRelation]:
    """Create CITES relations from citation keys to known sources."""
    cited_map = cited_source_map or {}
    citing_entities = store.list_entities(source_id=citing_source_id)
    if not citing_entities:
        return []

    relations: list[KnowledgeRelation] = []
    anchor = citing_entities[0]

    for key in citation_keys:
        cited_source_id = cited_map.get(key)
        if not cited_source_id:
            continue
        cited_entities = store.list_entities(source_id=cited_source_id, limit=1)
        if not cited_entities:
            continue
        rel = KnowledgeRelation(
            relation_id=_new_id("rel"),
            source_entity_id=anchor.entity_id,
            target_entity_id=cited_entities[0].entity_id,
            relation_type=RelationType.CITES,
            evidence=f"\\cite{{{key}}}",
            source_id=citing_source_id,
            confidence=0.8,
            metadata={"citation_key": key},
        )
        store.save_relation(rel)
        relations.append(rel)
    return relations


def get_lineage(store: SkaiStore, entity_id: str, *, depth: int = 3) -> dict:
    """Trace citation/dependency lineage for an entity."""
    visited: set[str] = set()
    lineage: list[dict] = []

    def _walk(eid: str, d: int) -> None:
        if eid in visited or d > depth:
            return
        visited.add(eid)
        entity = store.get_entity(eid)
        if entity:
            lineage.append({"entity_id": eid, "title": entity.title, "depth": d})
        for rel in store.list_relations(entity_id=eid):
            if rel.relation_type in (RelationType.CITES, RelationType.EXTENDS, RelationType.DEPENDS_ON):
                _walk(rel.target_entity_id, d + 1)

    _walk(entity_id, 0)
    return {"entity_id": entity_id, "lineage": lineage, "depth": depth}
