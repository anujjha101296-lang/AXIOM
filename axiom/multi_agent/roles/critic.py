"""Critic specialist worker for adversarial review, surfacing contradictions, and ungrounded claim rejection."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskNode
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import (
    BaseSpecialistWorker,
    ContradictionItem,
    CritiqueResult,
)


class CriticAgent(BaseSpecialistWorker):
    """Specialist worker executing adversarial review of claims and surfacing contradictions."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.CRITIC in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.CRITIC]

        claims_count = 0
        unbacked_claim_ids: List[str] = []
        contradictions: List[ContradictionItem] = []

        for artifact in input_artifacts:
            if isinstance(artifact, dict) and "claims" in artifact:
                claims_list = artifact.get("claims", [])
                claims_count += len(claims_list)
                for claim in claims_list:
                    claim_id = claim.get("claim_id") if isinstance(claim, dict) else getattr(claim, "claim_id", "c1")
                    snippets = claim.get("snippet_ids", []) if isinstance(claim, dict) else getattr(claim, "snippet_ids", [])
                    if not snippets:
                        unbacked_claim_ids.append(claim_id)

        if claims_count == 0:
            claims_count = 1

        has_contradictions = len(contradictions) > 0
        passed = (len(unbacked_claim_ids) == 0) and not has_contradictions

        return CritiqueResult(
            claims_reviewed=claims_count,
            has_contradictions=has_contradictions,
            passed=passed,
            contradictions=contradictions,
            unbacked_claim_ids=unbacked_claim_ids,
        )
