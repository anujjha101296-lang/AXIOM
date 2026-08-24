"""
axiom.hypothesis.critic
======================
Scientific Critique Engine.
Checks logical consistency, unsupported assumptions, scope errors, circular reasoning, and unfalsifiability.
"""
from __future__ import annotations

from typing import List

from axiom.hypothesis.models import CritiqueStatus, Hypothesis, HypothesisCritique


class ScientificCritic:
    """Scientific critique engine for hypotheses."""

    def critique_hypothesis(self, hypothesis: Hypothesis) -> HypothesisCritique:
        """Evaluate a hypothesis for flaws, assumptions, and falsifiability."""
        claim_text = hypothesis.claim.lower()

        unsupported_assumptions = []
        scope_errors = []
        is_falsifiable = True
        critique_status = CritiqueStatus.VALID
        critique_text = "Hypothesis is logically structured and falsifiable."

        # Check 1: Unfalsifiability check
        if any(phrase in claim_text for phrase in ["always true regardless", "cannot be disproven", "by definition"]):
            is_falsifiable = False
            critique_status = CritiqueStatus.UNFALSIFIABLE
            critique_text = "Hypothesis is unfalsifiable as it asserts tautological claims."

        # Check 2: Circular reasoning check
        elif "because" in claim_text and claim_text.split("because")[0].strip() in claim_text.split("because")[1].strip():
            critique_status = CritiqueStatus.NEEDS_REVISION
            critique_text = "Hypothesis exhibits circular reasoning."
            scope_errors.append("Circular dependency between premise and conclusion")

        # Check 3: Unsupported assumptions check
        if not hypothesis.assumptions:
            unsupported_assumptions.append("Missing explicit underlying assumptions")
            if critique_status == CritiqueStatus.VALID:
                critique_status = CritiqueStatus.NEEDS_REVISION
                critique_text = "Hypothesis requires explicit assumption specification."

        # Check 4: Overclaiming check
        if any(word in claim_text for word in ["universally", "infinitely", "every conceivable"]):
            scope_errors.append("Overclaiming beyond evidence scope")
            if critique_status == CritiqueStatus.VALID:
                critique_status = CritiqueStatus.NEEDS_REVISION
                critique_text = "Hypothesis scope is overly broad."

        return HypothesisCritique(
            hypothesis_id=hypothesis.id,
            status=critique_status,
            critique_text=critique_text,
            unsupported_assumptions=unsupported_assumptions,
            scope_errors=scope_errors,
            is_falsifiable=is_falsifiable,
        )
