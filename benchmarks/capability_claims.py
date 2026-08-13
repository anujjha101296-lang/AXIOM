"""
AXIOM Phase 8 — Capability Claims Registry

Structured capability records linking each AXIOM capability to its
measurement evidence. Every claim must have a benchmark run backing it.

NO marketing claims without measurement.
Every claim must link to: capability → evidence → benchmark → version → limitations.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import CapabilityClaim, CapabilityStatus

CLAIMS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evaluation_results",
    "capability_claims.json",
)


def build_initial_claims() -> list[CapabilityClaim]:
    """
    Define AXIOM's capability claims BEFORE measurement.
    Status begins as UNMEASURED or PARTIALLY_MEASURED.
    Running benchmarks updates these to MEASURED with real values.
    """
    return [
        CapabilityClaim(
            capability_id="cap_001",
            name="Document Retrieval",
            description="Retrieve relevant document chunks given a user query using semantic similarity",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Currently benchmarked on a small 6-chunk deterministic corpus",
                "Uses TF-IDF similarity for benchmarks; production uses embedding-based retrieval",
                "No evaluation on adversarial queries or out-of-distribution topics",
                "Retrieval quality depends on chunk size and overlap configuration",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_002",
            name="Evidence-Backed Q&A",
            description="Answer questions grounded in retrieved document evidence with citations",
            status=CapabilityStatus.PARTIALLY_MEASURED,
            limitations=[
                "Answer quality depends on LLM provider and configuration",
                "Citation validity rate not yet measured in production traffic",
                "Benchmark uses mock QA; real LLM grounding not benchmarked",
                "Evaluated on 5 controlled grounding cases only",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_003",
            name="Insufficient Evidence Detection",
            description="Express uncertainty and decline to answer when evidence is absent",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Measured only in mock QA system — not real LLM",
                "Benchmark does not cover all uncertainty scenarios",
                "LLM hallucination on absent topics is not fully evaluated",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_004",
            name="Contradiction Detection",
            description="Surface conflicting evidence when multiple documents disagree",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Only 1 contradiction case in current benchmark",
                "Detection is rule-based in mock QA, not LLM-based",
                "Real contradiction detection quality depends on LLM reasoning",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_005",
            name="Controlled Research Agent — Budget Enforcement",
            description="Agent stops execution when step/tool/runtime budgets are exhausted",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Budget enforcement tested via state machine simulation only",
                "Real-world timing measurements not included in benchmark",
                "Does not test preemptive cancellation of in-flight LLM calls",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_006",
            name="Controlled Research Agent — Safe Cancellation",
            description="Agent halts immediately and persists CANCELLED state when cancellation is requested",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Cancellation tested via state machine simulation only",
                "Does not cover concurrent cancellation races in async execution",
                "Requires manual verification in live system",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_007",
            name="Controlled Research Agent — Tool Allowlist",
            description="Agent uses only allowlisted tools: SEARCH_PROJECT_KNOWLEDGE, READ_DOCUMENT_EVIDENCE, ASK_GROUNDED_RESEARCH_ENGINE",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Tool allowlist enforcement tested at state machine level only",
                "Jailbreak resistance not evaluated",
                "Prompt injection defense not benchmarked in Phase 8",
            ],
        ),
        CapabilityClaim(
            capability_id="cap_008",
            name="Regression Detection",
            description="Detect capability regressions when comparing new versions against baseline",
            status=CapabilityStatus.UNMEASURED,
            limitations=[
                "Regression detection requires at least one prior baseline run",
                "Tolerance set at 5% — may be too lenient for critical capabilities",
                "Does not capture qualitative regressions (e.g., answer style changes)",
            ],
        ),
    ]


def update_claims_from_run(claims: list[CapabilityClaim], run_data: dict) -> list[CapabilityClaim]:
    """Update capability claims based on benchmark run results."""
    suite_results = {s["suite_id"]: s for s in run_data.get("suite_results", [])}

    for claim in claims:
        if claim.capability_id == "cap_001":  # Document Retrieval
            suite = suite_results.get("retrieval_benchmark")
            if suite:
                pass_rate = suite.get("summary", {}).get("pass_rate", 0)
                claim.status = CapabilityStatus.MEASURED
                claim.evidence_run_id = run_data.get("run_id")
                claim.evidence_suite_id = "retrieval_benchmark"
                claim.measured_metric = "Mean Hit@1"
                # Find Hit@1 metric
                for r in suite.get("results", []):
                    for m in r.get("metrics", []):
                        if m["name"] == "Hit@1":
                            claim.measured_value = m["value"]
                            break
                claim.git_commit = run_data.get("git_commit", "unknown")

        elif claim.capability_id == "cap_002":  # Evidence-backed Q&A
            suite = suite_results.get("grounding_benchmark")
            if suite:
                claim.status = CapabilityStatus.PARTIALLY_MEASURED
                claim.evidence_run_id = run_data.get("run_id")
                claim.evidence_suite_id = "grounding_benchmark"
                claim.measured_metric = "Pass Rate"
                claim.measured_value = suite.get("summary", {}).get("pass_rate", 0)
                claim.git_commit = run_data.get("git_commit", "unknown")

        elif claim.capability_id in ("cap_005", "cap_006", "cap_007"):  # Agent caps
            suite = suite_results.get("agent_benchmark")
            if suite:
                claim.status = CapabilityStatus.MEASURED
                claim.evidence_run_id = run_data.get("run_id")
                claim.evidence_suite_id = "agent_benchmark"
                claim.measured_metric = "Pass Rate"
                claim.measured_value = suite.get("summary", {}).get("pass_rate", 0)
                claim.git_commit = run_data.get("git_commit", "unknown")

    return claims


def save_claims(claims: list[CapabilityClaim], path: str = CLAIMS_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in claims], f, indent=2)
    print(f"✓ Capability claims saved to {path}")


def print_claims_report(claims: list[CapabilityClaim]) -> None:
    print(f"\n{'='*60}")
    print(f"AXIOM CAPABILITY CLAIMS")
    print(f"{'='*60}")
    for claim in claims:
        status_icon = {
            CapabilityStatus.MEASURED: "✓",
            CapabilityStatus.PARTIALLY_MEASURED: "≈",
            CapabilityStatus.UNMEASURED: "?",
            CapabilityStatus.NOT_IMPLEMENTED: "✗",
        }.get(claim.status, "?")

        print(f"\n{status_icon} [{claim.capability_id}] {claim.name}")
        print(f"   Status: {claim.status.value}")
        if claim.measured_value is not None:
            print(f"   Measured: {claim.measured_metric} = {claim.measured_value:.4f}")
        if claim.evidence_run_id:
            print(f"   Evidence: run={claim.evidence_run_id[:8]}... suite={claim.evidence_suite_id}")
        print(f"   Limitations:")
        for lim in claim.limitations[:2]:  # Show first 2
            print(f"     - {lim}")
    print()
