"""
AXIOM Workflow Engine — PlannerWorker
======================================
Decomposes an objective into a structured task DAG.
v1 uses deterministic rule-based planning.
v2 will use LLM-backed planning (Sprint 5: Reasoning Engine).
"""
from __future__ import annotations

import logging
import uuid

from .base import BaseWorker
from ..models import Task, WorkflowContext, WorkerResult, ArtifactType, Artifact
from ..memory import WorkflowMemory

logger = logging.getLogger(__name__)

# Default task templates per domain
_DOMAIN_TEMPLATES: dict[str, list[dict]] = {
    "research": [
        {"title": "Search literature",  "worker_type": "researcher", "description": "Find and retrieve relevant sources"},
        {"title": "Extract knowledge",  "worker_type": "researcher", "description": "Extract key claims and findings"},
        {"title": "Review extractions", "worker_type": "reviewer",   "description": "Validate extracted knowledge quality"},
        {"title": "Merge findings",     "worker_type": "merger",     "description": "Combine all extracted knowledge"},
        {"title": "Generate report",    "worker_type": "reporter",   "description": "Synthesize findings into a final report"},
    ],
    "math": [
        {"title": "Identify problem structure", "worker_type": "researcher", "description": "Analyze the mathematical problem"},
        {"title": "Survey related work",        "worker_type": "researcher", "description": "Find related theorems and proofs"},
        {"title": "Review relevance",           "worker_type": "reviewer",   "description": "Filter relevant results"},
        {"title": "Synthesize approach",        "worker_type": "merger",     "description": "Combine insights into a strategy"},
        {"title": "Generate proof plan",        "worker_type": "reporter",   "description": "Produce a structured proof plan"},
    ],
    "general": [
        {"title": "Gather information",  "worker_type": "researcher", "description": "Collect relevant information"},
        {"title": "Analyze findings",    "worker_type": "reviewer",   "description": "Analyze and validate information"},
        {"title": "Synthesize results",  "worker_type": "merger",     "description": "Combine analysis results"},
        {"title": "Generate report",     "worker_type": "reporter",   "description": "Produce final deliverable"},
    ],
}


class PlannerWorker(BaseWorker):
    """
    Decomposes an objective into a structured task list with dependencies.

    v1: Rule-based templates per domain.
    v2: Will use LLM reasoning to dynamically generate task DAGs.

    Output:
        outputs["tasks"] = list[dict] — task definitions with depends_on[] chains
    """

    worker_type = "planner"
    mission = "Decompose an objective into an ordered, dependency-linked task graph"
    capabilities = ["task_decomposition", "dependency_planning", "workflow_design"]

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        objective = task.inputs.get("objective", context.objective)
        domain = task.inputs.get("domain", context.domain)

        logger.info(f"PlannerWorker: planning for objective={objective!r}, domain={domain!r}")

        # Look up template for domain (fallback to general)
        templates = _DOMAIN_TEMPLATES.get(domain, _DOMAIN_TEMPLATES["general"])

        # Build task list with sequential depends_on chain
        task_defs = []
        prev_id: str | None = None

        for template in templates:
            task_id = str(uuid.uuid4())
            task_def = {
                "id": task_id,
                "title": template["title"],
                "description": f"{template['description']} — {objective}",
                "worker_type": template["worker_type"],
                "inputs": {
                    "objective": objective,
                    "domain": domain,
                },
                "depends_on": [prev_id] if prev_id else [],
                "max_retries": 2,
                "timeout_s": 300.0,
                "require_approval": False,
            }
            task_defs.append(task_def)
            prev_id = task_id

        # Store plan in working memory
        await memory.set("plan_task_count", len(task_defs), source_task_id=task.id)
        await memory.set("plan_domain", domain, source_task_id=task.id)

        plan_artifact = Artifact(
            task_id=task.id,
            workflow_id=task.workflow_id,
            artifact_type=ArtifactType.PLAN,
            title=f"Workflow Plan: {objective[:60]}",
            content={"tasks": task_defs, "domain": domain},
            text_content=self._format_plan(task_defs),
        )

        logger.info(f"PlannerWorker: generated {len(task_defs)} tasks for domain={domain!r}")
        return WorkerResult(
            success=True,
            outputs={"tasks": task_defs, "task_count": len(task_defs)},
            artifacts=[plan_artifact],
        )

    def _format_plan(self, task_defs: list[dict]) -> str:
        lines = ["# Workflow Plan\n"]
        for i, td in enumerate(task_defs, 1):
            deps = td.get("depends_on", [])
            dep_str = f" (after: {deps})" if deps else ""
            lines.append(f"{i}. [{td['worker_type']}] {td['title']}{dep_str}")
            lines.append(f"   {td['description']}")
        return "\n".join(lines)
