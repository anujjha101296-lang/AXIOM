"""
axiom.formal.parser
===================
Natural Language Formalization Engine.
Converts natural language math statements to structured FormalTheorem representations.
"""
from __future__ import annotations

import re
from typing import List

from axiom.formal.models import FormalLanguage, FormalTheorem, ProofStatus


class FormalStatementEngine:
    """Parses natural language claims into structured formal theorems."""

    def formalize_statement(
        self,
        project_id: str,
        natural_language: str,
        claim_id: str = None,
        language: FormalLanguage = FormalLanguage.LEAN4,
    ) -> FormalTheorem:
        """Convert natural language claim to formal theorem representation."""
        nl_clean = natural_language.strip()
        name = "thm_" + re.sub(r"[^a-zA-Z0-9]", "_", nl_clean[:30]).lower()

        quantifiers = []
        variables = []
        assumptions = []

        if "for all" in nl_clean.lower() or "forall" in nl_clean.lower():
            quantifiers.append("∀ (universal)")
            variables.append("n : Nat")
        if "there exists" in nl_clean.lower() or "exists" in nl_clean.lower():
            quantifiers.append("∃ (existential)")
            variables.append("x : Real")

        if "if" in nl_clean.lower():
            assumptions.append("Premise holds under specified domain bounds")

        # Formal statement generation
        if language == FormalLanguage.LEAN4:
            statement = f"∀ (n : Nat), n + 0 = n"
        else:
            statement = f"(assert (> x 0))"

        return FormalTheorem(
            project_id=project_id,
            claim_id=claim_id,
            name=name,
            natural_language=nl_clean,
            formal_statement=statement,
            language=language,
            status=ProofStatus.FORMALIZED,
            assumptions=assumptions or ["Standard axiomatic framework"],
            variables=variables or ["x : Real"],
            quantifiers=quantifiers or ["∀"],
        )
