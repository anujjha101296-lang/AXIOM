"""Knowledge versioning — never silently rewrite history (SKAI §8)."""

from __future__ import annotations

from axiom.skai.models import KnowledgeEntity, _new_id
from axiom.skai.store import SkaiStore


def version_entity(
    store: SkaiStore,
    entity_id: str,
    updated: KnowledgeEntity,
    *,
    change_reason: str,
) -> KnowledgeEntity:
    """Archive previous version before updating."""
    existing = store.get_entity(entity_id)
    if existing:
        version_num = existing.metadata.get("version", 1)
        store.save_knowledge_version(
            _new_id("kver"),
            entity_id,
            version_num,
            existing.to_dict(),
            change_reason,
        )
        updated.metadata["version"] = version_num + 1
        updated.metadata["previous_version"] = version_num
    store.save_entity(updated)
    return updated
