"""Challenge registry — tier definitions and challenge catalog."""

from __future__ import annotations

from typing import Any

from axiom.grand_challenge.models import ChallengeDefinition, ChallengeTier, EvidenceTier

# ── Tier 0: Toy reasoning ─────────────────────────────────────────────────────

TIER_0_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t0_arithmetic_series",
        tier=ChallengeTier.TIER_0_TOY,
        title="Arithmetic Series Sum",
        objective="Verify the system can solve and report a basic arithmetic series problem.",
        domain="mathematics",
        difficulty="elementary",
        required_capabilities=["mathematical_reasoning"],
        required_tools=["scep_benchmarks", "sympy_engine"],
        verification_method="Auto-graded numeric answer against SCEP case mr_001",
        success_criteria=["Score >= 1.0 on benchmark case mr_001", "Evidence tier recorded as measured"],
        failure_criteria=["Score < 1.0", "No reproducible run artifact"],
        benchmark_metrics=["case_score", "time_ms", "pass_rate"],
        human_review_process="Spot-check single numeric answer; no formal review required.",
        benchmark_refs=["mr_001"],
        evidence_tier=EvidenceTier.MEASURED,
    ),
    ChallengeDefinition(
        challenge_id="t0_gcd_computation",
        tier=ChallengeTier.TIER_0_TOY,
        title="GCD Computation",
        objective="Validate basic number-theoretic computation pipeline.",
        domain="mathematics",
        difficulty="elementary",
        required_capabilities=["mathematical_reasoning"],
        required_tools=["scep_benchmarks"],
        verification_method="Auto-graded against SCEP case mr_003 (GCD(48,18)=6)",
        success_criteria=["Score >= 1.0 on mr_003"],
        failure_criteria=["Incorrect GCD result"],
        benchmark_metrics=["case_score", "time_ms"],
        human_review_process="Automated pass/fail only.",
        benchmark_refs=["mr_003"],
        evidence_tier=EvidenceTier.MEASURED,
    ),
    ChallengeDefinition(
        challenge_id="t0_modular_arithmetic",
        tier=ChallengeTier.TIER_0_TOY,
        title="Modular Exponentiation",
        objective="Confirm modular arithmetic evaluation works end-to-end.",
        domain="mathematics",
        difficulty="elementary",
        required_capabilities=["mathematical_reasoning"],
        required_tools=["scep_benchmarks"],
        verification_method="Auto-graded against SCEP case mr_004 (2^10 mod 7 = 2)",
        success_criteria=["Score >= 1.0 on mr_004"],
        failure_criteria=["Incorrect modular result"],
        benchmark_metrics=["case_score", "time_ms"],
        human_review_process="Automated pass/fail only.",
        benchmark_refs=["mr_004"],
        evidence_tier=EvidenceTier.MEASURED,
    ),
]

# ── Tier 1: Known-answer theorem and proof tasks ──────────────────────────────

TIER_1_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t1_fermat_little_theorem",
        tier=ChallengeTier.TIER_1_KNOWN_ANSWER,
        title="Fermat's Little Theorem Verification",
        objective="Verify 3^(p-1) ≡ 1 (mod p) for prime p=7 using known-answer grading.",
        domain="mathematics",
        difficulty="undergraduate",
        required_capabilities=["mathematical_reasoning", "proof_verification"],
        required_tools=["scep_benchmarks", "smt_gateway"],
        verification_method="Auto-graded numeric check (SCEP mr_005); SMT finite-domain check optional",
        success_criteria=["mr_005 score >= 1.0", "Evidence tier explicitly recorded"],
        failure_criteria=["Incorrect modular result", "Claim of formal proof without compiler evidence"],
        benchmark_metrics=["case_score", "verification_invoked", "time_ms"],
        human_review_process="Reviewer confirms auto-grade matches expected answer; flags any formal-proof claims.",
        benchmark_refs=["mr_005"],
        evidence_tier=EvidenceTier.MEASURED,
        notes="This validates computation, not a written proof artifact.",
    ),
    ChallengeDefinition(
        challenge_id="t1_euler_identity",
        tier=ChallengeTier.TIER_1_KNOWN_ANSWER,
        title="Euler's Identity Numerical Verification",
        objective="Numerically verify e^(iπ) + 1 ≈ 0 within tolerance.",
        domain="mathematics",
        difficulty="undergraduate",
        required_capabilities=["mathematical_reasoning"],
        required_tools=["scep_benchmarks"],
        verification_method="Numeric tolerance check (SCEP mr_008)",
        success_criteria=["mr_008 score >= 1.0", "Error within 0.01"],
        failure_criteria=["Numeric error exceeds tolerance"],
        benchmark_metrics=["case_score", "numeric_error"],
        human_review_process="Reviewer checks tolerance bound is appropriate.",
        benchmark_refs=["mr_008"],
        evidence_tier=EvidenceTier.MEASURED,
    ),
    ChallengeDefinition(
        challenge_id="t1_proof_verification_basics",
        tier=ChallengeTier.TIER_1_KNOWN_ANSWER,
        title="Proof Verification Pipeline",
        objective="Run proof-verification benchmark cases and report evidence tier honestly.",
        domain="mathematics",
        difficulty="undergraduate",
        required_capabilities=["proof_verification"],
        required_tools=["scep_benchmarks", "smt_gateway", "lean_exporter"],
        verification_method="SCEP proof_verification cases pv_001–pv_003; simulated if compilers absent",
        success_criteria=[">= 2/3 pv cases pass", "Evidence tier not mislabeled as formal proof"],
        failure_criteria=["< 2/3 pass", "Simulated results labeled as proven"],
        benchmark_metrics=["pass_rate", "evidence_tier_accuracy"],
        human_review_process="Reviewer audits evidence tier labels against actual verification path.",
        benchmark_refs=["pv_001", "pv_002", "pv_003"],
        evidence_tier=EvidenceTier.SIMULATED,
        notes="Formal compilers may not be installed; simulated path must be disclosed.",
    ),
    ChallengeDefinition(
        challenge_id="t1_theorem_reproduction_zeta",
        tier=ChallengeTier.TIER_1_KNOWN_ANSWER,
        title="Basel Problem Numerical Reproduction",
        objective="Numerically reproduce ζ(2) = π²/6 within tolerance.",
        domain="mathematics",
        difficulty="graduate",
        required_capabilities=["mathematical_reasoning", "knowledge_quality"],
        required_tools=["scep_benchmarks"],
        verification_method="Numeric check (SCEP mr_010)",
        success_criteria=["mr_010 score >= 1.0"],
        failure_criteria=["Numeric error exceeds 0.01"],
        benchmark_metrics=["case_score", "numeric_error"],
        human_review_process="Reviewer confirms numerical method is documented.",
        benchmark_refs=["mr_010"],
        evidence_tier=EvidenceTier.MEASURED,
    ),
]

# ── Tier 2: Paper reproduction ────────────────────────────────────────────────

TIER_2_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t2_workflow_demo_reproduction",
        tier=ChallengeTier.TIER_2_PAPER_REPRODUCTION,
        title="Workflow Paper Research Demo",
        objective="Execute the GNN paper research workflow demo and produce structured artifacts.",
        domain="computer_science",
        difficulty="graduate",
        required_capabilities=["research_planning", "literature_synthesis", "research_productivity"],
        required_tools=["workflow_engine", "workflow_workers"],
        verification_method="Workflow completion with artifact checklist; human review of outputs",
        success_criteria=["Workflow completes without failure", "Research note and report artifacts produced"],
        failure_criteria=["Workflow failure", "Missing required artifacts"],
        benchmark_metrics=["workflow_completion_rate", "artifact_count", "duration_s"],
        human_review_process="Reviewer inspects artifact quality and methodology traceability.",
        benchmark_refs=["workflow:gnn_paper_research"],
        evidence_tier=EvidenceTier.BASELINE,
        notes="Demo workflow; not independent paper reproduction.",
    ),
    ChallengeDefinition(
        challenge_id="t2_literature_synthesis_bench",
        tier=ChallengeTier.TIER_2_PAPER_REPRODUCTION,
        title="Literature Synthesis Benchmark",
        objective="Score literature synthesis capability on SCEP benchmark cases.",
        domain="research",
        difficulty="graduate",
        required_capabilities=["literature_synthesis"],
        required_tools=["scep_benchmarks", "retrieval_engine"],
        verification_method="SCEP literature_synthesis benchmark pass rate",
        success_criteria=["Literature synthesis score >= 0.5"],
        failure_criteria=["Score < 0.5"],
        benchmark_metrics=["dimension_score", "pass_rate"],
        human_review_process="Reviewer samples synthesis outputs for factual accuracy.",
        benchmark_refs=["ls_*"],
        evidence_tier=EvidenceTier.BASELINE,
    ),
]

# ── Tier 3: Small open research questions ─────────────────────────────────────

TIER_3_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t3_open_problem_decomposition",
        tier=ChallengeTier.TIER_3_SMALL_OPEN,
        title="Open Problem Decomposition",
        objective="Decompose a bounded open problem into testable sub-questions with competing hypotheses.",
        domain="mathematics",
        difficulty="research",
        required_capabilities=["research_planning", "conjecture_generation", "reasoning"],
        required_tools=["hypothesis_engine", "scep_benchmarks", "working_memory"],
        verification_method="SCEP research_planning benchmarks; hypothesis count >= 2 with documented weaknesses",
        success_criteria=[">= 2 competing hypotheses", "Research plan with success criteria", "rp benchmark score >= 0.4"],
        failure_criteria=["Single hypothesis only", "No documented weaknesses", "rp score < 0.4"],
        benchmark_metrics=["hypothesis_count", "plan_completeness", "rp_score"],
        human_review_process="Domain reviewer evaluates decomposition quality and falsifiability.",
        benchmark_refs=["rp_001", "rp_002", "rp_003"],
        evidence_tier=EvidenceTier.HEURISTIC,
    ),
    ChallengeDefinition(
        challenge_id="t3_conjecture_novelty",
        tier=ChallengeTier.TIER_3_SMALL_OPEN,
        title="Conjecture Generation Quality",
        objective="Generate novel conjectures and score against SCEP conjecture benchmarks.",
        domain="mathematics",
        difficulty="research",
        required_capabilities=["conjecture_generation"],
        required_tools=["mip_conjecture", "hypothesis_engine", "scep_benchmarks"],
        verification_method="SCEP conjecture_generation benchmark score",
        success_criteria=["cg benchmark score >= 0.3"],
        failure_criteria=["cg score < 0.3", "Duplicate of known conjectures without attribution"],
        benchmark_metrics=["cg_score", "novelty_estimate"],
        human_review_process="Reviewer checks conjectures are non-trivial and properly scoped.",
        benchmark_refs=["cg_001", "cg_002", "cg_003"],
        evidence_tier=EvidenceTier.HEURISTIC,
    ),
]

# ── Tier 4: Domain grand challenges ───────────────────────────────────────────

TIER_4_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t4_multi_domain_capability",
        tier=ChallengeTier.TIER_4_DOMAIN_GRAND,
        title="Multi-Domain Capability Campaign",
        objective="Sustain measured capability across >= 6 SCEP dimensions for 30-day campaign window.",
        domain="cross_domain",
        difficulty="research",
        required_capabilities=[
            "mathematical_reasoning", "proof_verification", "conjecture_generation",
            "knowledge_quality", "research_planning", "literature_synthesis",
        ],
        required_tools=["scep_benchmarks", "eval_api", "workflow_engine", "checkpoint_store"],
        verification_method="Composite SCEP score >= 0.6 with >= 6 measured dimensions; regression detection",
        success_criteria=["Composite >= 0.6", "No dimension regression > 0.1", "30-day checkpoint trail"],
        failure_criteria=["Composite < 0.6", "Unexplained regression", "Missing checkpoints"],
        benchmark_metrics=["composite_score", "dimension_coverage", "regression_delta"],
        human_review_process="Monthly capability review with engineering and research leads.",
        benchmark_refs=["scep:full_suite"],
        evidence_tier=EvidenceTier.MEASURED,
        notes="Campaign management exercise; not a scientific discovery claim.",
    ),
    ChallengeDefinition(
        challenge_id="t4_long_running_autonomous",
        tier=ChallengeTier.TIER_4_DOMAIN_GRAND,
        title="Long-Running Autonomous Research Session",
        objective="Execute a 72-hour campaign with checkpoint recovery and journal continuity.",
        domain="research",
        difficulty="research",
        required_capabilities=["research_planning", "research_productivity", "recovery_from_failure"],
        required_tools=["workflow_engine", "checkpoint_store", "working_memory"],
        verification_method="Campaign completes with >= 3 checkpoints and continuous journal",
        success_criteria=[">= 3 checkpoints saved", "Journal entries for each experiment", "Recovery from simulated failure"],
        failure_criteria=["Data loss between checkpoints", "Journal gaps > 24h unexplained"],
        benchmark_metrics=["checkpoint_count", "journal_completeness", "recovery_success"],
        human_review_process="Weekly human review of campaign journal and evidence trail.",
        benchmark_refs=["workflow:checkpoints"],
        evidence_tier=EvidenceTier.BASELINE,
    ),
]

# ── Tier 5: Frontier open problems ────────────────────────────────────────────

TIER_5_CHALLENGES: list[ChallengeDefinition] = [
    ChallengeDefinition(
        challenge_id="t5_prize_readiness_assessment",
        tier=ChallengeTier.TIER_5_FRONTIER,
        title="Prize Readiness Assessment (Not a Solution Attempt)",
        objective="Measure organizational readiness against prize-track prerequisites without claiming progress on any prize problem.",
        domain="prize_track",
        difficulty="frontier",
        required_capabilities=[
            "mathematical_reasoning", "proof_verification", "conjecture_generation",
            "knowledge_quality", "counterexample_search",
        ],
        required_tools=["prize_readiness_scorer", "scep_benchmarks", "knowledge_graph"],
        verification_method="Prize readiness composite with explicit gaps documented; NO solution submission",
        success_criteria=["Readiness report generated", "All gaps explicitly listed", "No prize solution claims"],
        failure_criteria=["Any unsupported prize progress claim", "Readiness score presented without limitations"],
        benchmark_metrics=["readiness_score", "gap_count", "weakest_dimension"],
        human_review_process="Mandatory human authorization before any frontier-tier campaign activation.",
        benchmark_refs=["prize_readiness"],
        evidence_tier=EvidenceTier.BASELINE,
        notes="This is an organizational capability test. AXIOM does not solve prize problems in this framework.",
    ),
    ChallengeDefinition(
        challenge_id="t5_frontier_benchmark_participation",
        tier=ChallengeTier.TIER_5_FRONTIER,
        title="Frontier Benchmark Participation",
        objective="Participate in external frontier benchmarks (when available) with full provenance and honest scoring.",
        domain="cross_domain",
        difficulty="frontier",
        required_capabilities=["mathematical_reasoning", "reasoning", "verification"],
        required_tools=["eval_api", "provenance_records"],
        verification_method="External benchmark score with provenance envelope; human review required",
        success_criteria=["Provenance record complete", "Score reported with evidence tier", "Limitations documented"],
        failure_criteria=["Missing provenance", "Score inflation", "Undisclosed simulation"],
        benchmark_metrics=["external_score", "provenance_completeness"],
        human_review_process="Human must authorize benchmark participation and review all public-facing results.",
        benchmark_refs=[],
        evidence_tier=EvidenceTier.UNAVAILABLE,
        notes="No external frontier benchmark is currently integrated. Tier 5 is gated.",
    ),
]

ALL_CHALLENGES: dict[str, ChallengeDefinition] = {
    c.challenge_id: c
    for tier_list in [
        TIER_0_CHALLENGES, TIER_1_CHALLENGES, TIER_2_CHALLENGES,
        TIER_3_CHALLENGES, TIER_4_CHALLENGES, TIER_5_CHALLENGES,
    ]
    for c in tier_list
}


def get_challenge(challenge_id: str) -> ChallengeDefinition:
    if challenge_id not in ALL_CHALLENGES:
        available = ", ".join(sorted(ALL_CHALLENGES))
        raise KeyError(f"Unknown challenge '{challenge_id}'. Available: {available}")
    return ALL_CHALLENGES[challenge_id]


def list_challenges(tier: ChallengeTier | None = None) -> list[ChallengeDefinition]:
    if tier is None:
        return list(ALL_CHALLENGES.values())
    return [c for c in ALL_CHALLENGES.values() if c.tier == tier]


def program_manifest() -> dict[str, Any]:
    from axiom.grand_challenge.models import TIER_DESCRIPTIONS

    return {
        "name": "AXIOM Grand Challenge Program",
        "version": "1.0.0",
        "tiers": [
            {
                "tier": int(t),
                "name": t.name,
                "description": TIER_DESCRIPTIONS[t],
                "challenge_count": len(list_challenges(t)),
            }
            for t in ChallengeTier
        ],
        "total_challenges": len(ALL_CHALLENGES),
        "principle": "Manage long-term scientific campaigns; never claim prize solutions without evidence.",
    }
