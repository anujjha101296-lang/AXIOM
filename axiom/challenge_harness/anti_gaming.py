"""
axiom.challenge_harness.anti_gaming
==================================
Anti-Gaming Engine.
Protects benchmark integrity against prompt leakage, answer memorization, and fake citations.
"""
from __future__ import annotations

from typing import Tuple


class AntiGamingEngine:
    """Detects benchmark leakage and answer memorization attempts."""

    def inspect_output(self, agent_output: str, hidden_solution: str = "") -> Tuple[bool, str]:
        """
        Inspect agent output for benchmark prompt leakage or hardcoded answers.
        Returns (is_gaming_detected, reason).
        """
        text = agent_output.lower()

        # Hardcoded solution detection
        if "hardcoded_answer_flag" in text or "bypass_evaluation" in text:
            return True, "Anti-Gaming Triggered: Hardcoded answer or evaluation bypass detected."

        # Fake citation pattern
        if "doi:10.0000/fake" in text or "fake_journal_v1" in text:
            return True, "Anti-Gaming Triggered: Fabricated citation detected."

        return False, "Clean output"
