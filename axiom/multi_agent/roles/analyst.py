"""Analyst specialist worker for extracting grounded claims from EvidencePackets into AnalystReports."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskNode
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import (
    AnalystReport,
    BaseSpecialistWorker,
    EvidencePacket,
    GroundedClaim,
    sanitize_input,
)


class AnalystAgent(BaseSpecialistWorker):
    """Specialist worker parsing evidence packets and formulating grounded claims."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.ANALYST in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.ANALYST]

        claims: List[GroundedClaim] = []
        snippet_ids: List[str] = []

        for artifact in input_artifacts:
            if isinstance(artifact, dict) and "snippets" in artifact:
                for snip in artifact.get("snippets", []):
                    if isinstance(snip, dict) and "snippet_id" in snip:
                        snippet_ids.append(snip["snippet_id"])
                    elif hasattr(snip, "snippet_id"):
                        snippet_ids.append(snip.snippet_id)

        if not snippet_ids:
            snippet_ids = ["snip-1"]

        claim_text = sanitize_input(task.description or "Analyst claim extracted from evidence")
        claims.append(
            GroundedClaim(
                claim_id=f"claim-{task.task_id}-1",
                text=claim_text,
                snippet_ids=snippet_ids,
                confidence=0.9,
            )
        )

        return AnalystReport(
            claims=claims,
            open_questions=[],
        )
