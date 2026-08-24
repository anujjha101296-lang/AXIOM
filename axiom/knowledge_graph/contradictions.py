"""
axiom.knowledge_graph.contradictions
====================================
Contradiction Detection & Disagreement Representation Engine.
Explicitly links conflicting claims via GraphContradiction without deleting contradictory evidence.
"""
from __future__ import annotations

import re
from typing import List, Optional

from axiom.knowledge_graph.models import GraphClaim, GraphContradiction, EpistemicStatus


class ContradictionDetector:
    """Detects explicit contradictions between claims."""

    def detect_contradiction(
        self,
        claim_a: GraphClaim,
        claim_b: GraphClaim,
    ) -> Optional[GraphContradiction]:
        """
        Check if two claims in the same project contradict each other.
        Returns GraphContradiction if conflict is detected, else None.
        """
        if claim_a.id == claim_b.id or claim_a.project_id != claim_b.project_id:
            return None

        text_a = claim_a.claim_text.lower()
        text_b = claim_b.claim_text.lower()

        # Check for direct negation or opposite quantitative/evaluative statements
        is_contradiction = False
        reasoning = ""

        # Case 1: Direct negation phrases e.g. "x improves y" vs "x does not improve y"
        if ("not" in text_b or "fails" in text_b or "no" in text_b) and any(w in text_a for w in ["improves", "proves", "holds", "increases"]):
            # Check overlap of subject words
            words_a = set(re.findall(r'\w+', text_a)) - {"not", "no", "is", "a", "the", "and", "or"}
            words_b = set(re.findall(r'\w+', text_b)) - {"not", "no", "is", "a", "the", "and", "or"}
            intersection = words_a.intersection(words_b)
            if len(intersection) >= 2:
                is_contradiction = True
                reasoning = f"Claim A asserts positive assertion while Claim B asserts negative negation over shared concepts ({', '.join(list(intersection)[:3])})."

        if is_contradiction:
            # Update epistemic statuses
            claim_a.epistemic_status = EpistemicStatus.CONTRADICTED
            claim_b.epistemic_status = EpistemicStatus.CONTRADICTED
            return GraphContradiction(
                project_id=claim_a.project_id,
                claim_a_id=claim_a.id,
                claim_b_id=claim_b.id,
                contradiction_type="DIRECT_NEGATION",
                reasoning=reasoning,
                resolved=False,
            )

        return None
