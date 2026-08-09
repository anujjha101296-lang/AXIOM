"""Formal mathematics benchmarks (FMTP §23–24)."""

from __future__ import annotations

from axiom.formal_math.models import BenchmarkLevel

BENCHMARK_SUITE: dict[int, list[dict]] = {
    BenchmarkLevel.LEVEL_0: [
        {"id": "fmt_0_1", "task": "Formalize: for all n, n + 0 = n", "domain": "algebra"},
        {"id": "fmt_0_2", "task": "Formalize: commutativity of addition on ℕ", "domain": "algebra"},
    ],
    BenchmarkLevel.LEVEL_1: [
        {"id": "fmt_1_1", "task": "Prove: sum of first n naturals", "domain": "algebra"},
        {"id": "fmt_1_2", "task": "Prove: if a|b and b|c then a|c", "domain": "number_theory"},
    ],
    BenchmarkLevel.LEVEL_2: [
        {"id": "fmt_2_1", "task": "Prove: AM-GM for two positive reals", "domain": "analysis"},
        {"id": "fmt_2_2", "task": "Prove: pigeonhole principle instance", "domain": "combinatorics"},
    ],
    BenchmarkLevel.LEVEL_3: [
        {"id": "fmt_3_1", "task": "Reproduce: Lagrange's theorem statement", "domain": "group_theory"},
    ],
    BenchmarkLevel.LEVEL_4: [
        {"id": "fmt_4_1", "task": "Reproduce published lemma from Mathlib", "domain": "algebra"},
    ],
}


def list_benchmarks(level: int | None = None) -> list[dict]:
    if level is not None:
        return BENCHMARK_SUITE.get(BenchmarkLevel(level), [])
    all_benches = []
    for lvl, items in BENCHMARK_SUITE.items():
        for item in items:
            all_benches.append({**item, "level": lvl})
    return all_benches


def estimate_difficulty(statement: str) -> dict[str, float]:
    """Estimate formalization/proof difficulty (FMTP §20)."""
    lower = statement.lower()
    depth = 0.3
    if any(k in lower for k in ["millennium", "open problem", "conjecture"]):
        depth = 0.95
    elif any(k in lower for k in ["prove", "theorem", "formal"]):
        depth = 0.6
    elif any(k in lower for k in ["formalize", "define"]):
        depth = 0.4

    return {
        "statement_complexity": depth,
        "library_availability": 0.5,
        "proof_depth": depth,
        "automation_potential": 0.7 if "=" in statement else 0.3,
        "formalization_burden": depth * 0.8,
        "human_expertise_required": depth,
    }
