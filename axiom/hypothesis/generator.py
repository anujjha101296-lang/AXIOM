"""
axiom.hypothesis.generator
==========================
Hypothesis Candidate Generation Engine.
Input: research question, knowledge graph context, research gaps, evidence chunks.
Output: candidate hypotheses marked PROPOSED.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from axiom.hypothesis.models import Hypothesis, HypothesisStatus


class HypothesisGenerator:
    """Generates candidate hypotheses grounded in evidence and research gaps."""

    def generate_hypotheses(
        self,
        project_id: str,
        question: str,
        gaps: List[Dict[str, Any]] = None,
        context_chunks: List[str] = None,
        session_id: Optional[str] = None,
    ) -> List[Hypothesis]:
        """Generate candidate hypotheses for a research question."""
        if not question or not question.strip():
            return []

        gaps = gaps or []
        context_chunks = context_chunks or []

        hypotheses = []

        # 1. Main Hypothesis
        main_claim = self._formulate_claim(question, context_chunks)
        h1 = Hypothesis(
            project_id=project_id,
            session_id=session_id,
            claim=main_claim,
            motivation=f"Formulated to address research question: '{question}'",
            assumptions=["System parameters are bounded", "Evidence text is representative"],
            verification_strategy="Literature synthesis and counter-evidence search",
            status=HypothesisStatus.PROPOSED,
            confidence_score=0.5,
            rationale="Initial candidate generated from available evidence context.",
        )
        hypotheses.append(h1)

        # 2. Alternative Hypothesis if gaps exist
        if gaps:
            gap_desc = gaps[0].get("description", "unresolved gap")
            alt_claim = f"Alternative mechanism: {main_claim} subject to constraints of {gap_desc}"
            h2 = Hypothesis(
                project_id=project_id,
                session_id=session_id,
                gap_id=gaps[0].get("id"),
                claim=alt_claim,
                motivation=f"Formulated to address identified research gap: '{gap_desc}'",
                assumptions=["Gap represents missing evidence rather than disproof"],
                verification_strategy="Targeted external research for gap resolution",
                status=HypothesisStatus.PROPOSED,
                confidence_score=0.4,
                rationale="Alternative hypothesis addressing known evidence gaps.",
            )
            hypotheses.append(h2)

        return hypotheses

    def _formulate_claim(self, question: str, chunks: List[str]) -> str:
        q = question.strip().rstrip("?")
        if chunks:
            snippet = chunks[0][:100].strip()
            return f"Regarding '{q}': {snippet}"
        return f"Regarding '{q}': Proposed scientific relationship holds under standard conditions"
