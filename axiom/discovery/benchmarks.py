"""Deterministic discovery benchmarks including false-discovery cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from axiom.discovery.engine import DiscoveryEngine
from axiom.discovery.models import DiscoveryStatus


@dataclass
class BenchmarkCase:
    case_id: str
    name: str
    research_question: str
    seed_text: str
    expected_statuses: set[str]
    must_not_claim_discovery: bool = True
    notes: str = ""


BENCHMARKS: list[BenchmarkCase] = [
    BenchmarkCase(
        case_id="b1_known_pattern",
        name="Known scientific pattern (reproduction framing)",
        research_question="Does addition identity n+0=n hold for small integers?",
        seed_text="It is well known that for integers n, n+0=n. Open question: edge notation variants.",
        expected_statuses={"SUPPORTED", "CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION"},
        notes="Should not claim novelty for a known identity.",
    ),
    BenchmarkCase(
        case_id="b2_math_conjecture_style",
        name="Known conjecture-style question",
        research_question="Are all non-trivial zeros of zeta on the critical line?",
        seed_text="Open question / conjecture: Riemann Hypothesis. Related work extensively studied.",
        expected_statuses={"CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION", "SUPPORTED"},
        notes="Must mark insufficient search or related work; never claim solved.",
    ),
    BenchmarkCase(
        case_id="b3_known_counterexample",
        name="Statement marked known false",
        research_question="Is it true that all odd numbers greater than 1 are prime (known false)?",
        seed_text="Claim that is already disproven / known false for composites like 9.",
        expected_statuses={"REFUTED", "CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION", "SUPPORTED"},
        notes="Counterexample engine should preferentially refute when marker present.",
    ),
    BenchmarkCase(
        case_id="b4_conflicting_literature",
        name="Conflicting literature",
        research_question="Does method A always outperform method B?",
        seed_text=(
            "Paper 1 claims method A is always better. "
            "Paper 2 claims method B outperforms A on boundary cases. "
            "Unresolved conflict remains."
        ),
        expected_statuses={"CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION", "SUPPORTED"},
    ),
    BenchmarkCase(
        case_id="b5_small_gap",
        name="Small research gap",
        research_question="What is the effect of parameter k in regime k>10 for toy model M?",
        seed_text="Future work: explore parameter region k>10. Missing experiment noted.",
        expected_statuses={"SUPPORTED", "CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION"},
    ),
    BenchmarkCase(
        case_id="b6_insufficient_evidence",
        name="Correct result is insufficient evidence",
        research_question="Is phenomenon Z present in unobserved domain D?",
        seed_text="No direct measurements in domain D. Literature silent. Open question.",
        expected_statuses={"UNRESOLVED", "CHALLENGED", "UNDER_INVESTIGATION"},
    ),
    BenchmarkCase(
        case_id="b7_misleading_evidence",
        name="Misleading pattern (false discovery trap)",
        research_question="Does every sequence of length 5 of even digits always sum to a prime?",
        seed_text=(
            "Convincing-looking pattern observed in a tiny sample. "
            "Always false / known false for many counterexamples such as 2,2,2,2,2."
        ),
        expected_statuses={"REFUTED", "CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION", "SUPPORTED"},
        notes="False discovery benchmark — system should not promote to VERIFIED.",
    ),
    BenchmarkCase(
        case_id="b8_formal_candidate",
        name="Theorem needing formal verification framing",
        research_question="Can n+0=n be formally verified for integers?",
        seed_text="Standard arithmetic lemma suitable for formalization. Not a Millennium problem.",
        expected_statuses={"SUPPORTED", "CHALLENGED", "UNRESOLVED", "UNDER_INVESTIGATION"},
    ),
]


def run_benchmark_case(engine: DiscoveryEngine, case: BenchmarkCase) -> dict[str, Any]:
    d = engine.create(case.research_question, seed_text=case.seed_text, knowledge_context=case.seed_text)
    result = engine.run_cycle(d.discovery_id)
    final = engine.store.get(d.discovery_id)
    assert final is not None
    status_ok = final.status.value in case.expected_statuses
    claimed = bool(final.report.get("is_scientific_discovery_claim"))
    verified_illegal = final.status == DiscoveryStatus.VERIFIED
    novelty = final.novelty.status.value
    return {
        "case_id": case.case_id,
        "name": case.name,
        "status": final.status.value,
        "status_ok": status_ok,
        "novelty": novelty,
        "hypothesis_count": len([h for h in final.hypotheses if not h.rejected]),
        "prediction_count": len(final.predictions),
        "attacks": len(final.attacks),
        "claimed_discovery": claimed,
        "verified_without_gate": verified_illegal,
        "passed": status_ok and not claimed and not verified_illegal,
        "cycle": result,
        "notes": case.notes,
    }


def run_all_benchmarks(db_path: str) -> dict[str, Any]:
    engine = DiscoveryEngine(db_path)
    results = [run_benchmark_case(engine, case) for case in BENCHMARKS]
    passed = sum(1 for r in results if r["passed"])
    false_verified = sum(1 for r in results if r["verified_without_gate"])
    # False discovery rate proxy: fraction of misleading/false cases that reached VERIFIED
    trap_cases = [r for r in results if r["case_id"] in {"b3_known_counterexample", "b7_misleading_evidence"}]
    traps_failed = sum(1 for r in trap_cases if r["status"] == "VERIFIED" or r["claimed_discovery"])
    fdr = (traps_failed / len(trap_cases)) if trap_cases else 0.0
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "false_discovery_rate": fdr,
        "false_verified_count": false_verified,
        "results": results,
    }
