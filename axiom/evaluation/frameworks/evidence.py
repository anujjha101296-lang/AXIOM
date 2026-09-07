"""
S0-E4 EPIC-002 evidence integration gate.

Every capability score exposes evidence_state, benchmark_count, and stated limitations.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from axiom.evaluation.benchmarks.suite import (
    run_conjecture_benchmarks,
    run_counterexample_benchmarks,
    run_knowledge_quality_benchmarks,
    run_literature_synthesis_benchmarks,
    run_math_reasoning_benchmarks,
    run_proof_verification_benchmarks,
    run_research_planning_benchmarks,
    run_research_productivity_benchmarks,
)
from axiom.evaluation.frameworks.capability import (
    BenchmarkResult,
    CapabilityDimension,
    CapabilitySnapshot,
    DimensionScore,
    EvidenceState,
    make_dimension_score,
)

# Per-dimension limitations surfaced on every score (S0-E4 requirement).
DIMENSION_LIMITATIONS: dict[CapabilityDimension, list[str]] = {
    CapabilityDimension.MATHEMATICAL_REASONING: [
        "Benchmarks use symbolic/heuristic checks, not competition-level problem solving.",
    ],
    CapabilityDimension.PROOF_VERIFICATION: [
        "Proof verification uses structural simulation when Lean/Coq/Isabelle compilers are absent.",
        "Simulated passes do not constitute formal proof.",
    ],
    CapabilityDimension.CONJECTURE_GENERATION: [
        "Conjecture quality depends on knowledge graph population; empty DB yields degraded signal.",
    ],
    CapabilityDimension.KNOWLEDGE_QUALITY: [
        "Knowledge quality benchmarks require a populated epistemic store.",
    ],
    CapabilityDimension.COUNTEREXAMPLE_SEARCH: [
        "Search is bounded heuristic enumeration, not exhaustive counterexample discovery.",
    ],
    CapabilityDimension.RESEARCH_PLANNING: [
        "Planning benchmarks use template heuristics, not LLM-backed strategy generation.",
    ],
    CapabilityDimension.LITERATURE_SYNTHESIS: [
        "Synthesis benchmarks depend on ingested literature in the knowledge graph.",
    ],
    CapabilityDimension.RESEARCH_PRODUCTIVITY: [
        "Productivity metrics are proxy counts from the knowledge graph, not user studies.",
    ],
}

# Evidence classification per dimension after a benchmark run.
DIMENSION_EVIDENCE_PROFILE: dict[CapabilityDimension, tuple[EvidenceState, bool]] = {
    CapabilityDimension.MATHEMATICAL_REASONING: (EvidenceState.MEASURED, False),
    CapabilityDimension.PROOF_VERIFICATION: (EvidenceState.SIMULATED, True),
    CapabilityDimension.CONJECTURE_GENERATION: (EvidenceState.MEASURED, False),
    CapabilityDimension.KNOWLEDGE_QUALITY: (EvidenceState.MEASURED, False),
    CapabilityDimension.COUNTEREXAMPLE_SEARCH: (EvidenceState.MEASURED, False),
    CapabilityDimension.RESEARCH_PLANNING: (EvidenceState.MEASURED, False),
    CapabilityDimension.LITERATURE_SYNTHESIS: (EvidenceState.MEASURED, False),
    CapabilityDimension.RESEARCH_PRODUCTIVITY: (EvidenceState.MEASURED, False),
}

# Conservative baseline scores when no benchmark run exists (honest, gated).
BASELINE_SCORES: dict[CapabilityDimension, float] = {
    CapabilityDimension.MATHEMATICAL_REASONING: 0.40,
    CapabilityDimension.PROOF_VERIFICATION: 0.35,
    CapabilityDimension.CONJECTURE_GENERATION: 0.30,
    CapabilityDimension.KNOWLEDGE_QUALITY: 0.45,
    CapabilityDimension.COUNTEREXAMPLE_SEARCH: 0.35,
    CapabilityDimension.RESEARCH_PLANNING: 0.30,
    CapabilityDimension.LITERATURE_SYNTHESIS: 0.40,
    CapabilityDimension.RESEARCH_PRODUCTIVITY: 0.30,
}

REQUIRED_SCORE_FIELDS = (
    "score",
    "level",
    "level_name",
    "confidence",
    "benchmark_count",
    "estimated",
    "evidence_state",
    "limitations",
)


def gate_dimension_dict(score: DimensionScore) -> dict[str, Any]:
    """Serialize a DimensionScore with all S0-E4 evidence fields."""
    return {
        "score": score.raw_score,
        "level": score.level,
        "level_name": score.level_name,
        "confidence": score.confidence,
        "benchmark_count": score.benchmark_count,
        "estimated": score.estimated,
        "evidence_state": score.evidence_state.value,
        "limitations": list(score.limitations),
        "weighted": score.weighted_score,
    }


def make_gated_dimension_score(
    dimension: CapabilityDimension,
    raw_score: float,
    benchmark_count: int,
    *,
    evidence_state: EvidenceState,
    estimated: bool | None = None,
    confidence: float | None = None,
    extra_limitations: list[str] | None = None,
) -> DimensionScore:
    """Build a dimension score with evidence gate fields populated."""
    if estimated is None:
        estimated = evidence_state in (
            EvidenceState.ESTIMATED,
            EvidenceState.BASELINE,
            EvidenceState.SIMULATED,
        )
    if confidence is None:
        if benchmark_count == 0:
            confidence = 0.0
        elif evidence_state == EvidenceState.SIMULATED:
            confidence = 0.5
        else:
            confidence = min(0.95, 0.5 + benchmark_count * 0.05)

    limitations = list(DIMENSION_LIMITATIONS.get(dimension, []))
    if extra_limitations:
        limitations.extend(extra_limitations)
    if benchmark_count == 0:
        limitations.append("No benchmark cases executed for this dimension.")

    return make_dimension_score(
        dimension,
        raw_score,
        benchmark_count,
        confidence=confidence,
        estimated=estimated,
        evidence_state=evidence_state,
        limitations=limitations,
    )


def build_baseline_snapshot() -> CapabilitySnapshot:
    """Evidence-gated baseline when no benchmark run exists in the database."""
    snapshot = CapabilitySnapshot(
        run_id="baseline",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    snapshot.dimension_scores = [
        make_gated_dimension_score(
            dim,
            BASELINE_SCORES[dim],
            benchmark_count=0,
            evidence_state=EvidenceState.BASELINE,
            estimated=True,
            confidence=0.0,
            extra_limitations=[
                "Baseline placeholder — run POST /eval/run or make test-benchmark for measured scores.",
            ],
        )
        for dim in CapabilityDimension
    ]
    snapshot.compute_composite()
    return snapshot


def build_baseline_dimensions_dict() -> dict[str, Any]:
    """Return gated dimension scores for empty-database API responses."""
    snapshot = build_baseline_snapshot()
    return {s.dimension.value: gate_dimension_dict(s) for s in snapshot.dimension_scores}


def assert_gated_dimension(dim_name: str, info: dict[str, Any]) -> None:
    """Validate that a dimension payload includes all S0-E4 fields."""
    for field in REQUIRED_SCORE_FIELDS:
        assert field in info, f"{dim_name} missing required field: {field}"
    assert isinstance(info["limitations"], list)
    assert len(info["limitations"]) >= 1
    assert info["evidence_state"] in {s.value for s in EvidenceState}


@dataclass
class BenchmarkRunBundle:
    snapshot: CapabilitySnapshot
    all_results: list[BenchmarkResult]
    scores_map: dict[str, float]


def run_all_capability_benchmarks(db_path: str) -> BenchmarkRunBundle:
    """Run all eight benchmark suites and return an evidence-gated snapshot."""
    mr_results, mr_score = run_math_reasoning_benchmarks()
    pv_results, pv_score = run_proof_verification_benchmarks()
    cg_results, cg_score = run_conjecture_benchmarks(db_path)
    kq_results, kq_score = run_knowledge_quality_benchmarks(db_path)
    ce_results, ce_score = run_counterexample_benchmarks(db_path)
    rp_results, rp_score = run_research_planning_benchmarks()
    ls_results, ls_score = run_literature_synthesis_benchmarks(db_path)
    rd_results, rd_score = run_research_productivity_benchmarks(db_path)

    run_id = str(uuid.uuid4())[:8]
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    suite_data: list[tuple[CapabilityDimension, list[BenchmarkResult], float]] = [
        (CapabilityDimension.MATHEMATICAL_REASONING, mr_results, mr_score),
        (CapabilityDimension.PROOF_VERIFICATION, pv_results, pv_score),
        (CapabilityDimension.CONJECTURE_GENERATION, cg_results, cg_score),
        (CapabilityDimension.KNOWLEDGE_QUALITY, kq_results, kq_score),
        (CapabilityDimension.COUNTEREXAMPLE_SEARCH, ce_results, ce_score),
        (CapabilityDimension.RESEARCH_PLANNING, rp_results, rp_score),
        (CapabilityDimension.LITERATURE_SYNTHESIS, ls_results, ls_score),
        (CapabilityDimension.RESEARCH_PRODUCTIVITY, rd_results, rd_score),
    ]

    dimension_scores: list[DimensionScore] = []
    for dimension, results, raw_score in suite_data:
        evidence_state, estimated = DIMENSION_EVIDENCE_PROFILE[dimension]
        extra: list[str] = []
        if len(results) == 0:
            evidence_state = EvidenceState.UNAVAILABLE
            estimated = True
            extra.append("Benchmark suite returned no results.")
        dimension_scores.append(
            make_gated_dimension_score(
                dimension,
                raw_score,
                len(results),
                evidence_state=evidence_state,
                estimated=estimated,
                extra_limitations=extra,
            )
        )

    snapshot = CapabilitySnapshot(run_id=run_id, timestamp=timestamp, dimension_scores=dimension_scores)
    snapshot.compute_composite()

    all_results = (
        mr_results + pv_results + cg_results + kq_results
        + ce_results + rp_results + ls_results + rd_results
    )
    scores_map = {s.dimension.value: s.raw_score for s in snapshot.dimension_scores}
    return BenchmarkRunBundle(snapshot=snapshot, all_results=all_results, scores_map=scores_map)
