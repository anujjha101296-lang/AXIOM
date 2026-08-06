"""Role specifications for autonomous research loop workers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RoleSpec:
    role_id: str
    name: str
    responsibilities: List[str]
    inputs: List[str]
    outputs: List[str]
    tools: List[str]
    success_criteria: List[str]
    failure_criteria: List[str]
    worker_type: str


RESEARCH_LOOP_ROLES: dict[str, RoleSpec] = {
    "research_planner": RoleSpec(
        role_id="research_planner",
        name="Research Planner",
        responsibilities=[
            "Decompose the research question into ordered subproblems",
            "Identify known facts and explicit assumptions",
            "Check failure memory before proposing approaches",
        ],
        inputs=["research_question", "prior_state", "failure_memory"],
        outputs=["subproblems", "known_facts", "assumptions", "open_questions"],
        tools=["failure_memory_store", "workflow_memory"],
        success_criteria=["At least 2 subproblems produced", "Assumptions explicitly listed"],
        failure_criteria=["Empty decomposition", "Repeats blocked approach"],
        worker_type="research_planner",
    ),
    "literature_researcher": RoleSpec(
        role_id="literature_researcher",
        name="Literature Researcher",
        responsibilities=[
            "Retrieve evidence from project documents and knowledge base",
            "Extract citable facts with source attribution",
            "Never invent citations",
        ],
        inputs=["subproblems", "project_id", "research_question"],
        outputs=["evidence_items", "sources"],
        tools=["research_store.search", "research_store.list_documents"],
        success_criteria=["Evidence has source field", "At least 1 evidence item per subproblem"],
        failure_criteria=["Fabricated source", "Empty retrieval with available documents"],
        worker_type="literature_researcher",
    ),
    "hypothesis_generator": RoleSpec(
        role_id="hypothesis_generator",
        name="Hypothesis Generator",
        responsibilities=[
            "Propose candidate hypotheses grounded in evidence",
            "Avoid duplicates and blocked approaches",
            "Rank candidates by evidential support",
        ],
        inputs=["evidence", "subproblems", "failure_memory"],
        outputs=["hypotheses", "rankings"],
        tools=["hypothesis_engine", "failure_memory_store"],
        success_criteria=["Hypotheses cite evidence", "No duplicate fingerprints"],
        failure_criteria=["Repeats failed approach", "Unsupported speculation without label"],
        worker_type="hypothesis_generator",
    ),
    "skeptic_critic": RoleSpec(
        role_id="skeptic_critic",
        name="Skeptic / Critic",
        responsibilities=[
            "Challenge unsupported claims and weak reasoning",
            "Flag false citations and overconfident statements",
            "Produce actionable criticism for each top hypothesis",
        ],
        inputs=["hypotheses", "evidence", "claims"],
        outputs=["criticisms", "rejected_hypothesis_ids"],
        tools=["claim_classifier"],
        success_criteria=["Each hypothesis receives criticism", "Unsupported claims flagged"],
        failure_criteria=["Approves without evidence review"],
        worker_type="skeptic_critic",
    ),
    "evidence_verifier": RoleSpec(
        role_id="evidence_verifier",
        name="Evidence Verifier",
        responsibilities=[
            "Classify claims using epistemic status taxonomy",
            "Run bounded SMT checks where applicable",
            "Never upgrade UNVERIFIED to FORMALLY_VERIFIED without evidence",
        ],
        inputs=["claims", "hypotheses", "experiments"],
        outputs=["verified_claims", "disproved_claims", "verification_results"],
        tools=["smt_gateway", "truthfulness.EpistemicAssignment"],
        success_criteria=["All claims have ClaimStatus", "SMT results labeled correctly"],
        failure_criteria=["False formal proof claim", "Missing evidence mode"],
        worker_type="evidence_verifier",
    ),
    "experiment_designer": RoleSpec(
        role_id="experiment_designer",
        name="Experiment Designer",
        responsibilities=[
            "Design bounded derivations or computational checks",
            "Execute sympy-based verification for algebraic claims",
            "Record failed derivations for failure memory",
        ],
        inputs=["top_hypothesis", "subproblems"],
        outputs=["experiments", "derivation_results"],
        tools=["sympy_engine", "failure_memory_store"],
        success_criteria=["Experiment has method and result", "Failures recorded"],
        failure_criteria=["Infinite loop pattern", "Blocked approach reused"],
        worker_type="experiment_designer",
    ),
    "synthesis_worker": RoleSpec(
        role_id="synthesis_worker",
        name="Synthesis Worker",
        responsibilities=[
            "Integrate evidence, verified claims, and experiment results",
            "Identify knowledge gaps and remaining uncertainties",
            "Update confidence estimate",
        ],
        inputs=["evidence", "claims", "experiments", "criticisms"],
        outputs=["synthesis", "gaps", "uncertainties", "confidence"],
        tools=["workflow_memory"],
        success_criteria=["Gaps explicitly listed", "Confidence in [0,1]"],
        failure_criteria=["Contradictory synthesis without flagging"],
        worker_type="synthesis_worker",
    ),
    "research_reporter": RoleSpec(
        role_id="research_reporter",
        name="Research Reporter",
        responsibilities=[
            "Produce final evidence-backed research report",
            "Include claim status for every important statement",
            "Document failed approaches and what was learned",
        ],
        inputs=["full_research_state"],
        outputs=["final_report", "artifact"],
        tools=["artifact_store"],
        success_criteria=["Report cites evidence", "Claim statuses visible", "Provenance preserved"],
        failure_criteria=["Claims discovery without evidence", "Missing failure section"],
        worker_type="research_reporter",
    ),
}


def list_roles() -> list[RoleSpec]:
    return list(RESEARCH_LOOP_ROLES.values())
