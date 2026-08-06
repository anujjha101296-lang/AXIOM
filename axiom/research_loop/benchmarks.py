"""Historical benchmark problems with hidden solutions for validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class HistoricalBenchmark:
    id: str
    title: str
    problem_statement: str
    domain: str
    difficulty: str
    hidden_solution: str
    solution_keywords: List[str]
    evaluation_notes: str
    # Hidden from the loop during execution — only used for scoring


def _score_keyword_match(report: str, keywords: List[str]) -> float:
    if not keywords:
        return 0.0
    text = report.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return round(hits / len(keywords), 4)


def _score_sum_formula(report: str, state_claims: List[str]) -> float:
    combined = (report + " " + " ".join(state_claims)).lower()
    has_formula = bool(re.search(r"n\s*\(\s*n\s*\+\s*1\s*\)\s*/\s*2", combined))
    has_gauss = "n(n+1)/2" in combined.replace(" ", "") or "n(n+1)/2" in combined
    has_closed = "closed form" in combined or "formula" in combined
    score = 0.0
    if has_formula or has_gauss:
        score += 0.6
    if has_closed:
        score += 0.2
    if "5050" in combined or "sum" in combined:
        score += 0.2
    return min(1.0, score)


def _score_pythagorean(report: str, state_claims: List[str]) -> float:
    combined = (report + " " + " ".join(state_claims)).lower()
    score = 0.0
    if "3" in combined and "4" in combined and "5" in combined:
        score += 0.4
    if "25" in combined or "9" in combined or "16" in combined:
        score += 0.2
    if "pythagor" in combined:
        score += 0.2
    if "a^2" in combined or "a²" in combined or "square" in combined:
        score += 0.2
    return min(1.0, score)


def _score_prime_infinitude(report: str, state_claims: List[str]) -> float:
    combined = (report + " " + " ".join(state_claims)).lower()
    score = 0.0
    if "infinite" in combined or "infinitely many" in combined or "unbounded" in combined:
        score += 0.4
    if "euclid" in combined or "contradiction" in combined:
        score += 0.3
    if "prime" in combined:
        score += 0.2
    if "product" in combined or "multiply" in combined:
        score += 0.1
    return min(1.0, score)


def _score_euler_polyhedra(report: str, state_claims: List[str]) -> float:
    combined = (report + " " + " ".join(state_claims)).lower()
    score = 0.0
    if "v - e + f" in combined or "v-e+f" in combined.replace(" ", ""):
        score += 0.4
    if "2" in combined and ("vertex" in combined or "edge" in combined or "face" in combined):
        score += 0.3
    if "euler" in combined:
        score += 0.2
    if "cube" in combined or "8" in combined and "12" in combined and "6" in combined:
        score += 0.1
    return min(1.0, score)


HISTORICAL_BENCHMARKS: Dict[str, HistoricalBenchmark] = {
    "bench_sum_formula": HistoricalBenchmark(
        id="bench_sum_formula",
        title="Sum of First n Integers",
        problem_statement=(
            "Find a closed-form formula for the sum 1 + 2 + 3 + ... + n. "
            "Derive the result and verify it for n=100."
        ),
        domain="algebra",
        difficulty="undergraduate",
        hidden_solution="n(n+1)/2; for n=100 the sum is 5050",
        solution_keywords=["n(n+1)/2", "5050", "closed form", "gauss", "arithmetic series"],
        evaluation_notes="Classic Gauss sum; solution should state n(n+1)/2.",
    ),
    "bench_pythagorean_345": HistoricalBenchmark(
        id="bench_pythagorean_345",
        title="Pythagorean Triple (3,4,5)",
        problem_statement=(
            "Explain why 3² + 4² = 5² holds and describe the general pattern "
            "for Pythagorean triples of positive integers."
        ),
        domain="number_theory",
        difficulty="undergraduate",
        hidden_solution="9+16=25; triples satisfy a²+b²=c² with (3,4,5) as smallest primitive example",
        solution_keywords=["9", "16", "25", "pythagorean", "a^2", "triple"],
        evaluation_notes="Should verify 3-4-5 and mention Pythagorean relation.",
    ),
    "bench_prime_infinitude": HistoricalBenchmark(
        id="bench_prime_infinitude",
        title="Infinitude of Primes",
        problem_statement=(
            "Prove or provide strong evidence that there are infinitely many prime numbers. "
            "What classical argument applies?"
        ),
        domain="number_theory",
        difficulty="undergraduate",
        hidden_solution="Euclid's proof: assume finitely many primes, multiply all and add 1",
        solution_keywords=["euclid", "infinite", "infinitely many", "contradiction", "prime"],
        evaluation_notes="Euclid's classical proof is the expected route.",
    ),
    "bench_euler_polyhedra": HistoricalBenchmark(
        id="bench_euler_polyhedra",
        title="Euler's Polyhedron Formula",
        problem_statement=(
            "For a convex polyhedron, relate the number of vertices V, edges E, and faces F. "
            "Verify the relationship for a cube."
        ),
        domain="geometry",
        difficulty="undergraduate",
        hidden_solution="V - E + F = 2; cube has V=8, E=12, F=6 giving 8-12+6=2",
        solution_keywords=["v - e + f", "euler", "2", "cube", "8", "12", "6"],
        evaluation_notes="Euler characteristic V-E+F=2 for convex polyhedra.",
    ),
}

SCORERS: Dict[str, Callable[[str, List[str]], float]] = {
    "bench_sum_formula": _score_sum_formula,
    "bench_pythagorean_345": _score_pythagorean,
    "bench_prime_infinitude": _score_prime_infinitude,
    "bench_euler_polyhedra": _score_euler_polyhedra,
}


def get_benchmark(benchmark_id: str) -> Optional[HistoricalBenchmark]:
    return HISTORICAL_BENCHMARKS.get(benchmark_id)


def list_benchmarks() -> List[HistoricalBenchmark]:
    return list(HISTORICAL_BENCHMARKS.values())


def score_benchmark(
    benchmark_id: str,
    final_report: str,
    claims: List[str],
) -> float:
    bench = get_benchmark(benchmark_id)
    if not bench:
        return 0.0
    scorer = SCORERS.get(benchmark_id)
    if scorer:
        return scorer(final_report, claims)
    return _score_keyword_match(final_report, bench.solution_keywords)
