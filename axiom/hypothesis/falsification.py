"""
axiom.hypothesis.falsification
==============================
Falsification Search Engine.
Deliberately searches internal evidence, external research, and knowledge graph for disproof/counterevidence.
"""
from __future__ import annotations

from typing import List, Tuple

from axiom.hypothesis.models import (
    Hypothesis,
    HypothesisEvidence,
    HypothesisStatus,
)


class FalsificationEngine:
    """Deliberately attempts to falsify proposed hypotheses using available evidence."""

    def search_counterevidence(
        self,
        hypothesis: Hypothesis,
        evidence_pool: List[Dict[str, str]],
    ) -> Tuple[Hypothesis, List[HypothesisEvidence]]:
        """
        Evaluate evidence pool for counterevidence disproving hypothesis.
        Returns (updated_hypothesis, new_evidences).
        """
        claim_lower = hypothesis.claim.lower()
        counter_evidences = []

        for item in evidence_pool:
            text = item.get("text", "").lower()
            chunk_id = item.get("chunk_id")
            source_id = item.get("source_id")

            # Check for direct disproof keywords
            if ("not" in text or "fails" in text or "disproves" in text or "refutes" in text) and any(w in text for w in claim_lower.split() if len(w) > 4):
                ev = HypothesisEvidence(
                    hypothesis_id=hypothesis.id,
                    chunk_id=chunk_id,
                    source_id=source_id,
                    supports=False,
                    snippet=item.get("text", "")[:300],
                )
                counter_evidences.append(ev)

        if counter_evidences:
            if len(counter_evidences) >= 2:
                hypothesis.status = HypothesisStatus.FALSIFIED
                hypothesis.confidence_score = 0.0
                hypothesis.rationale = f"Falsified by {len(counter_evidences)} explicit counter-evidence items."
            else:
                hypothesis.status = HypothesisStatus.CONTRADICTED
                hypothesis.confidence_score = 0.2
                hypothesis.rationale = "Contradicted by counter-evidence item."

        return hypothesis, counter_evidences
