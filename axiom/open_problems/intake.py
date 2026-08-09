"""Problem intake — understand before attempting a solution."""

from __future__ import annotations

import re

from axiom.open_problems.models import ProblemUnderstanding


def understand_problem(statement: str, *, known_info: str = "") -> ProblemUnderstanding:
    text = f"{statement}\n{known_info}".strip()
    lower = text.lower()

    definitions = re.findall(
        r"(?:define|let|where)\s+([^.!\n]{5,80})",
        text,
        flags=re.I,
    )[:8]

    variables = sorted(
        set(re.findall(r"\b([nmkxyzN]|prime|integer|graph|set)\b", text))
    )[:12]

    assumptions: list[str] = []
    for marker in ("assume", "given that", "suppose", "for all", "whenever"):
        if marker in lower:
            assumptions.append(f"Statement invokes '{marker}'")
    if "even" in lower and "odd" in lower:
        assumptions.append("Parity constraints may be material")

    known_mentioned: list[str] = []
    for phrase in ("theorem", "lemma", "conjecture", "known", "proven", "disproven", "false"):
        if phrase in lower:
            known_mentioned.append(phrase)

    conclusion = ""
    for pat in (
        r"prove that\s+(.+?)(?:\.|$)",
        r"show that\s+(.+?)(?:\.|$)",
        r"is it true that\s+(.+?)(?:\?|$)",
        r"does\s+(.+?)(?:\?|$)",
    ):
        m = re.search(pat, text, flags=re.I)
        if m:
            conclusion = m.group(1).strip()[:300]
            break
    if not conclusion:
        conclusion = statement.strip()[:300]

    equivalents: list[str] = []
    if "equivalent" in lower or "iff" in lower or "if and only if" in lower:
        equivalents.append("Statement may admit equivalent reformulations")

    boundaries = []
    if any(w in lower for w in ("all", "every", "always", "never")):
        boundaries.append("Universal claim — check edge/degenerate cases")
    if any(w in lower for w in ("prime", "odd", "even")):
        boundaries.append("Small integers and composites as boundary tests")

    specials = []
    if "n=1" in lower or "n = 1" in lower or "trivial" in lower:
        specials.append("Trivial / small-n special cases indicated")
    if "odd" in lower:
        specials.append("Odd integers as a restricted regime")

    return ProblemUnderstanding(
        definitions=[d.strip() for d in definitions] or ["No explicit definitions parsed — treat as informal"],
        variables=variables or ["n"],
        assumptions=assumptions or ["No explicit assumptions extracted"],
        known_results_mentioned=known_mentioned,
        required_conclusion=conclusion,
        equivalent_formulations=equivalents,
        boundary_cases=boundaries or ["Check empty/degenerate instances"],
        special_cases=specials,
    )
