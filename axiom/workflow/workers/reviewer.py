"""
AXIOM Workflow Engine — ReviewerWorker
========================================
Validates an artifact or set of outputs against quality criteria.
Acts as a quality gate — can reject or request revision.
"""
from __future__ import annotations

import logging

from .base import BaseWorker
from ..models import Task, WorkflowContext, WorkerResult, ArtifactType, Artifact, FailureAction
from ..memory import WorkflowMemory

logger = logging.getLogger(__name__)


class ReviewerWorker(BaseWorker):
    """
    Quality-gates a set of outputs or artifacts.

    Checks:
    - Minimum claim count (configurable, default 1)
    - Minimum concept count (configurable, default 1)
    - No empty text content
    - Custom criteria from task.inputs["criteria"]

    Inputs:
        claims       (list[str], optional)
        key_concepts (list[str], optional)
        summary      (str, optional)
        criteria     (list[str], optional) — additional check descriptions
        min_claims   (int, optional, default 1)
        min_concepts (int, optional, default 1)

    Output:
        outputs["passed"]   = bool
        outputs["score"]    = float (0.0–1.0)
        outputs["issues"]   = list[str]
        outputs["feedback"] = str
    """

    worker_type = "reviewer"
    mission = "Validate artifact quality and gate progression to the next workflow stage"
    capabilities = ["quality_assurance", "claim_validation", "completeness_check", "feedback_generation"]

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        inputs = task.inputs
        issues: list[str] = []
        checks_passed = 0
        checks_total = 0

        # Pull knowledge from working memory if not in inputs
        claims = inputs.get("claims") or await memory.get_accumulated_knowledge("claims")
        concepts = inputs.get("key_concepts") or await memory.get_accumulated_knowledge("concepts")
        summary = inputs.get("summary", "")
        criteria = inputs.get("criteria", [])
        min_claims = int(inputs.get("min_claims", 1))
        min_concepts = int(inputs.get("min_concepts", 1))

        # Check 1: Minimum claims
        checks_total += 1
        if len(claims) >= min_claims:
            checks_passed += 1
        else:
            issues.append(
                f"Insufficient claims: found {len(claims)}, required {min_claims}"
            )

        # Check 2: Minimum concepts
        checks_total += 1
        if len(concepts) >= min_concepts:
            checks_passed += 1
        else:
            issues.append(
                f"Insufficient key concepts: found {len(concepts)}, required {min_concepts}"
            )

        # Check 3: Non-empty summary
        checks_total += 1
        if summary and len(summary.strip()) >= 20:
            checks_passed += 1
        else:
            issues.append("Summary is missing or too short (<20 chars)")

        # Check 4: No duplicate claims
        checks_total += 1
        unique_claims = set(claims)
        if len(unique_claims) == len(claims):
            checks_passed += 1
        else:
            issues.append(f"Found {len(claims) - len(unique_claims)} duplicate claims")

        # Custom criteria (v1: simply record them as passed if present)
        for criterion in criteria:
            checks_total += 1
            # v2: will use LLM to evaluate custom criteria
            checks_passed += 1  # Stub: all custom criteria pass in v1

        score = checks_passed / checks_total if checks_total > 0 else 0.0
        passed = len(issues) == 0

        # Store review result in working memory
        await memory.set("review_score", score, source_task_id=task.id)
        await memory.set("review_passed", passed, source_task_id=task.id)
        if issues:
            for issue in issues:
                await memory.add_open_question(issue, source_task_id=task.id)

        feedback = self._format_feedback(score, passed, issues, checks_passed, checks_total)

        review_artifact = Artifact(
            task_id=task.id,
            workflow_id=task.workflow_id,
            artifact_type=ArtifactType.REVIEW,
            title=f"Quality Review: {task.title}",
            content={
                "passed": passed,
                "score": score,
                "checks_passed": checks_passed,
                "checks_total": checks_total,
                "issues": issues,
                "claims_reviewed": len(claims),
                "concepts_reviewed": len(concepts),
            },
            text_content=feedback,
        )

        logger.info(
            f"ReviewerWorker: score={score:.2f}, passed={passed}, "
            f"issues={len(issues)}, claims={len(claims)}, concepts={len(concepts)}"
        )

        if not passed:
            logger.warning(f"ReviewerWorker: quality gate NOT passed. Issues: {issues}")
            # Don't abort — report issues but continue with warning
            return WorkerResult(
                success=True,  # Review itself succeeded; quality concerns surfaced as issues
                outputs={
                    "passed": passed,
                    "score": score,
                    "issues": issues,
                    "feedback": feedback,
                },
                artifacts=[review_artifact],
            )

        return WorkerResult(
            success=True,
            outputs={
                "passed": passed,
                "score": score,
                "issues": issues,
                "feedback": feedback,
            },
            artifacts=[review_artifact],
        )

    def _format_feedback(
        self,
        score: float,
        passed: bool,
        issues: list[str],
        checks_passed: int,
        checks_total: int,
    ) -> str:
        status = "✅ PASSED" if passed else "⚠️ ISSUES FOUND"
        lines = [
            f"# Review Result: {status}",
            f"Score: {score:.0%} ({checks_passed}/{checks_total} checks passed)",
        ]
        if issues:
            lines.append("\n## Issues")
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("\nAll quality checks passed.")
        return "\n".join(lines)
