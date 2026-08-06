"""
AXIOM Workflow Engine — ReporterWorker
========================================
Synthesizes all workflow artifacts into a structured final report.
The report is the primary deliverable of a completed workflow.
"""
from __future__ import annotations

import logging
from datetime import datetime

from .base import BaseWorker
from ..models import Task, WorkflowContext, WorkerResult, ArtifactType, Artifact
from ..memory import WorkflowMemory

logger = logging.getLogger(__name__)


class ReporterWorker(BaseWorker):
    """
    Generates the final structured report artifact from a completed workflow.

    Reads from working memory:
        merged_claims    → list[str]
        merged_concepts  → list[str]
        review_score     → float
        review_passed    → bool
        open_questions   → list[str]
        hypotheses       → list[str]

    Inputs (optional overrides):
        title            → str
        include_sections → list[str]

    Output:
        outputs["report_title"] = str
        outputs["report_text"]  = str
        outputs["claim_count"]  = int
        outputs["concept_count"] = int
    Artifact type: REPORT
    """

    worker_type = "reporter"
    mission = "Synthesize all workflow artifacts into a final structured report"
    capabilities = [
        "report_generation", "synthesis", "finding_summarization",
        "open_question_tracking", "executive_summary"
    ]

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        objective = context.objective
        domain = context.domain

        # Gather all knowledge from working memory
        merged_claims: list[str] = await memory.get("merged_claims", [])
        merged_concepts: list[str] = await memory.get("merged_concepts", [])
        review_score: float = await memory.get("review_score", 1.0)
        review_passed: bool = await memory.get("review_passed", True)
        open_questions: list[str] = await memory.get_open_questions()
        hypotheses: list[str] = await memory.get_hypotheses()
        failed_attempts: list = await memory.get_failed_attempts()

        # Fallback: pull from direct inputs if memory is empty
        if not merged_claims:
            merged_claims = task.inputs.get("claims", [])
        if not merged_concepts:
            merged_concepts = task.inputs.get("concepts", [])

        title = task.inputs.get(
            "title",
            f"Research Report: {objective[:60]}"
        )
        generated_at = datetime.utcnow().isoformat()

        report_text = self._build_report(
            title=title,
            objective=objective,
            domain=domain,
            claims=merged_claims,
            concepts=merged_concepts,
            review_score=review_score,
            review_passed=review_passed,
            open_questions=open_questions,
            hypotheses=hypotheses,
            failed_attempts=failed_attempts,
            generated_at=generated_at,
        )

        report_artifact = Artifact(
            task_id=task.id,
            workflow_id=task.workflow_id,
            artifact_type=ArtifactType.REPORT,
            title=title,
            content={
                "objective": objective,
                "domain": domain,
                "claims": merged_claims,
                "concepts": merged_concepts,
                "open_questions": open_questions,
                "hypotheses": hypotheses,
                "quality_score": review_score,
                "quality_passed": review_passed,
                "generated_at": generated_at,
                "metadata": {
                    "claim_count": len(merged_claims),
                    "concept_count": len(merged_concepts),
                    "open_question_count": len(open_questions),
                    "failed_attempt_count": len(failed_attempts),
                },
            },
            text_content=report_text,
        )

        logger.info(
            f"ReporterWorker: generated report '{title}' — "
            f"{len(merged_claims)} claims, {len(merged_concepts)} concepts, "
            f"{len(open_questions)} open questions"
        )

        return WorkerResult(
            success=True,
            outputs={
                "report_title": title,
                "report_text": report_text,
                "claim_count": len(merged_claims),
                "concept_count": len(merged_concepts),
                "open_question_count": len(open_questions),
            },
            artifacts=[report_artifact],
        )

    def _build_report(
        self,
        title: str,
        objective: str,
        domain: str,
        claims: list[str],
        concepts: list[str],
        review_score: float,
        review_passed: bool,
        open_questions: list[str],
        hypotheses: list[str],
        failed_attempts: list,
        generated_at: str,
    ) -> str:
        quality_status = "✅ Passed" if review_passed else f"⚠️ {review_score:.0%} ({len(open_questions)} issues)"
        lines = [
            f"# {title}",
            "",
            "## Overview",
            f"**Objective:** {objective}",
            f"**Domain:** {domain}",
            f"**Quality Score:** {quality_status}",
            f"**Generated:** {generated_at}",
            "",
        ]

        if claims:
            lines += [
                f"## Key Findings ({len(claims)} claims)",
                *[f"- {c}" for c in claims],
                "",
            ]
        else:
            lines += ["## Key Findings\n*No claims extracted.*\n"]

        if concepts:
            lines += [
                f"## Key Concepts ({len(concepts)} terms)",
                *[f"- {c}" for c in concepts],
                "",
            ]

        if hypotheses:
            lines += [
                f"## Hypotheses Generated ({len(hypotheses)})",
                *[f"- {h}" for h in hypotheses],
                "",
            ]

        if open_questions:
            lines += [
                f"## Open Questions ({len(open_questions)})",
                *[f"- {q}" for q in open_questions],
                "",
            ]

        if failed_attempts:
            lines += [
                f"## Failed Attempts ({len(failed_attempts)})",
                *[f"- {str(a)[:120]}" for a in failed_attempts],
                "",
            ]

        lines += [
            "---",
            f"*Report generated by AXIOM Workflow Engine · {generated_at}*",
        ]

        return "\n".join(lines)
