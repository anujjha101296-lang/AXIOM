"""Competing research strategies — genuinely different approaches, not LLM confidence."""

from __future__ import annotations

from axiom.open_problems.models import OpenProblem, Strategy, TrackKind, _new_id


def generate_strategies(problem: OpenProblem) -> list[Strategy]:
    """Produce distinct strategy kinds with explicit ranking features."""
    stmt = problem.informal_statement
    strategies = [
        Strategy(
            strategy_id=_new_id("st"),
            name="Analytical / structural",
            kind=TrackKind.ANALYTICAL,
            motivation="Derive necessary structure from definitions and known lemmas",
            prerequisites=["precise definitions", "known lemmas"],
            advantages=["transferable lemmas", "insight into obstacles"],
            failure_modes=["hidden assumptions", "non-constructive leaps"],
            required_tools=["reasoning", "skai"],
            expected_difficulty=0.55,
            verification_method="independent analytical review + optional formalization",
            scientific_potential=0.7,
            novelty_potential=0.35,
            feasibility=0.6,
            information_gain=0.65,
            computational_cost=0.25,
            formalizability=0.55,
        ),
        Strategy(
            strategy_id=_new_id("st"),
            name="Computational exploration",
            kind=TrackKind.COMPUTATIONAL,
            motivation="Enumerate/simulate small cases to detect patterns or failures",
            prerequisites=["executable model of the claim"],
            advantages=["fast falsification", "reproducible artifacts"],
            failure_modes=["overfitting small n", "missing asymptotic regimes"],
            required_tools=["sec", "python"],
            expected_difficulty=0.4,
            verification_method="sandboxed reproduction with seeds",
            scientific_potential=0.55,
            novelty_potential=0.25,
            feasibility=0.8,
            information_gain=0.75,
            computational_cost=0.45,
            formalizability=0.25,
        ),
        Strategy(
            strategy_id=_new_id("st"),
            name="Counterexample-first",
            kind=TrackKind.COUNTEREXAMPLE,
            motivation="Try to kill the claim before investing in a proof",
            prerequisites=["search space for adversarial cases"],
            advantages=["prevents false discovery", "cheap negative knowledge"],
            failure_modes=["incomplete search ≠ truth"],
            required_tools=["sec", "discovery"],
            expected_difficulty=0.35,
            verification_method="independent counterexample verification",
            scientific_potential=0.8,
            novelty_potential=0.2,
            feasibility=0.85,
            information_gain=0.9,
            computational_cost=0.35,
            formalizability=0.2,
        ),
        Strategy(
            strategy_id=_new_id("st"),
            name="Formal mathematics track",
            kind=TrackKind.FORMAL,
            motivation="Formalize the statement and attempt prover-backed progress",
            prerequisites=["stable informal statement"],
            advantages=["machine-checkable artifacts"],
            failure_modes=["prose mistaken for proof", "tooling gaps"],
            required_tools=["fmtp", "lean"],
            expected_difficulty=0.7,
            verification_method="trusted prover compilation only",
            scientific_potential=0.75,
            novelty_potential=0.3,
            feasibility=0.45,
            information_gain=0.55,
            computational_cost=0.5,
            formalizability=0.9,
        ),
        Strategy(
            strategy_id=_new_id("st"),
            name="Literature synthesis",
            kind=TrackKind.LITERATURE,
            motivation="Map prior art, equivalent formulations, and negative results",
            prerequisites=["search budget"],
            advantages=["avoids reinventing known work"],
            failure_modes=["incomplete retrieval ≠ novelty"],
            required_tools=["skai", "web_fetch"],
            expected_difficulty=0.45,
            verification_method="citation provenance + UNTRUSTED marking",
            scientific_potential=0.6,
            novelty_potential=0.4,
            feasibility=0.7,
            information_gain=0.7,
            computational_cost=0.3,
            formalizability=0.2,
        ),
    ]

    # Domain tweak: if known-false markers, boost counterexample
    if any(m in stmt.lower() for m in ("known false", "always false", "disproven")):
        for s in strategies:
            if s.kind == TrackKind.COUNTEREXAMPLE:
                s.scientific_potential = 0.95
                s.information_gain = 0.95
                s.feasibility = 0.95

    strategies.sort(key=lambda s: s.rank_score, reverse=True)
    return strategies


def select_top_strategies(strategies: list[Strategy], *, k: int = 5) -> list[Strategy]:
    active = [s for s in strategies if not s.abandoned]
    return sorted(active, key=lambda s: s.rank_score, reverse=True)[:k]
