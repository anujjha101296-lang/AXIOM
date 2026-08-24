"""
axiom.knowledge_graph.research_gaps
===================================
Research Gap Identification Engine.
Detects missing evidence, weak evidence, conflicting claims, and unresolved questions.
"""
from __future__ import annotations

from typing import List, Optional

from axiom.knowledge_graph.models import (
    GapType,
    GraphClaim,
    GraphClaimEvidence,
    GraphContradiction,
    GraphEntity,
    GraphRelationship,
    GraphResearchGap,
    EpistemicStatus,
)


class ResearchGapAnalyzer:
    """Analyzes knowledge graph state to identify research gaps."""

    def analyze_gaps(
        self,
        project_id: str,
        entities: List[GraphEntity],
        claims: List[GraphClaim],
        evidences: List[GraphClaimEvidence],
        relationships: List[GraphRelationship],
        contradictions: List[GraphContradiction],
    ) -> List[GraphResearchGap]:
        """Detect research gaps across project graph objects."""
        gaps = []

        # 1. Claims with no evidence (NO_EVIDENCE)
        claim_ids_with_ev = {e.claim_id for e in evidences}
        for c in claims:
            if c.id not in claim_ids_with_ev:
                gaps.append(
                    GraphResearchGap(
                        project_id=project_id,
                        gap_type=GapType.NO_EVIDENCE,
                        description=f"Claim '{c.claim_text[:60]}' has no direct supporting evidence.",
                        severity="HIGH",
                        target_claim_id=c.id,
                    )
                )

        # 2. Conflicting evidence / Contradictions (CONFLICTING_EVIDENCE)
        for cd in contradictions:
            if not cd.resolved:
                gaps.append(
                    GraphResearchGap(
                        project_id=project_id,
                        gap_type=GapType.CONFLICTING_EVIDENCE,
                        description=f"Unresolved contradiction between claims {cd.claim_a_id[:8]} and {cd.claim_b_id[:8]}: {cd.reasoning}",
                        severity="HIGH",
                        target_claim_id=cd.claim_a_id,
                    )
                )

        # 3. Sparse entities with no relationships or claims (WEAK_EVIDENCE)
        rel_entity_ids = {r.subject_entity_id for r in relationships}.union({r.object_entity_id for r in relationships})
        for e in entities:
            if e.id not in rel_entity_ids:
                gaps.append(
                    GraphResearchGap(
                        project_id=project_id,
                        gap_type=GapType.WEAK_EVIDENCE,
                        description=f"Entity '{e.name}' has no registered relationships to other knowledge graph entities.",
                        severity="LOW",
                        target_entity_id=e.id,
                    )
                )

        return gaps
