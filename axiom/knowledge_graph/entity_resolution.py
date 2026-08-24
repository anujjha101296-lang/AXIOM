"""
axiom.knowledge_graph.entity_resolution
=======================================
Conservative Entity Resolution Engine.
Prevents unintended entity mergers:
NEW ENTITY -> NORMALIZE -> EXACT MATCH -> ALIAS MATCH -> HIGH-CONFIDENCE MATCH -> AMBIGUOUS? -> KEEP SEPARATE vs LINK.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from axiom.knowledge_graph.models import GraphEntity, GraphEntityAlias


def normalize_name(name: str) -> str:
    """Normalize string for conservative matching."""
    s = name.strip().lower()
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())


class ConservativeEntityResolver:
    """Conservative entity resolution engine."""

    def resolve_entity(
        self,
        candidate: GraphEntity,
        existing_entities: List[GraphEntity],
        existing_aliases: List[GraphEntityAlias],
    ) -> Tuple[GraphEntity, Optional[GraphEntityAlias], bool]:
        """
        Resolve candidate entity against existing graph entities.
        Returns (resolved_entity, alias_if_created, is_new).
        """
        cand_norm = normalize_name(candidate.name)

        # 1. Exact match on normalized name & entity type
        for e in existing_entities:
            if normalize_name(e.name) == cand_norm and e.entity_type == candidate.entity_type:
                return e, None, False

        # 2. Alias match
        for a in existing_aliases:
            if normalize_name(a.alias) == cand_norm:
                for e in existing_entities:
                    if e.id == a.entity_id:
                        return e, None, False

        # 3. High-confidence string match (e.g. acronyms or minor prefix/suffix variation)
        for e in existing_entities:
            e_norm = normalize_name(e.name)
            if self._is_high_confidence_alias(cand_norm, e_norm):
                alias = GraphEntityAlias(
                    entity_id=e.id,
                    alias=candidate.name,
                )
                return e, alias, False

        # 4. Ambiguous match -> KEEP SEPARATE (is_new = True)
        return candidate, None, True

    def _is_high_confidence_alias(self, norm_a: str, norm_b: str) -> bool:
        """Conservative rule-based equivalence check."""
        if not norm_a or not norm_b:
            return False
        # Exact acronym match e.g. "smt" vs "satisfiability modulo theories"
        if len(norm_a) <= 5 and "".join([w[0] for w in norm_b.split() if w]) == norm_a:
            return True
        if len(norm_b) <= 5 and "".join([w[0] for w in norm_a.split() if w]) == norm_b:
            return True
        return False
