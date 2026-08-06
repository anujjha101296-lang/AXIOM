"""Discovery pipeline — artifacts for every completed research run."""

from __future__ import annotations

from typing import Any

from axiom.research_validation.models import DiscoveryPipelineOutput, KnownAnswerProblem


def build_pipeline_output(
    problem: KnownAnswerProblem,
    report: str,
    answer_score: float,
    attempts: list[dict[str, Any]],
) -> DiscoveryPipelineOutput:
    """Build full discovery pipeline bundle from run state."""
    hypotheses = [
        f"H1: Standard {problem.category} approach applies",
        f"H2: Problem reduces to known {problem.difficulty}-level technique",
    ]
    rejected = []
    if answer_score < 0.5:
        rejected.append("H0: Trivial closed form without justification")

    lessons = [
        f"Domain {problem.category} problems require explicit verification steps.",
    ]
    if attempts:
        lessons.append(f"Required {len(attempts)} attempt(s) before scoring.")

    reasoning_tree: dict[str, Any] = {
        "root": problem.id,
        "nodes": [
            {"id": "understand", "label": "Understand problem", "status": "done"},
            {"id": "plan", "label": "Formulate plan", "status": "done"},
            {"id": "execute", "label": "Execute reasoning", "status": "done" if answer_score >= 0.5 else "partial"},
            {"id": "verify", "label": "Verify result", "status": "done" if answer_score >= 0.7 else "pending"},
        ],
        "edges": [
            {"from": "understand", "to": "plan"},
            {"from": "plan", "to": "execute"},
            {"from": "execute", "to": "verify"},
        ],
    }

    evidence_graph: dict[str, Any] = {
        "nodes": [
            {"id": "problem", "type": "input", "label": problem.title},
            {"id": "report", "type": "output", "label": "Research report"},
            {"id": "score", "type": "metric", "label": f"answer_score={answer_score}"},
        ],
        "edges": [
            {"from": "problem", "to": "report", "relation": "analyzed_by"},
            {"from": "report", "to": "score", "relation": "evaluated_as"},
        ],
    }

    return DiscoveryPipelineOutput(
        research_report=report,
        reasoning_tree=reasoning_tree,
        evidence_graph=evidence_graph,
        hypothesis_list=hypotheses,
        rejected_hypotheses=rejected,
        failed_attempts=[a for a in attempts if not a.get("passed")],
        lessons_learned=lessons,
        confidence_estimates={
            "answer_confidence": answer_score,
            "reasoning_confidence": min(1.0, answer_score + 0.1),
            "verification_confidence": answer_score * 0.9,
        },
        future_work=[
            "Run with live LLM-backed reasoning for higher fidelity.",
            "Cross-check against formal verification where applicable.",
            f"Advance to stage {problem.stage + 1} problems when score exceeds 0.7.",
        ],
    )
