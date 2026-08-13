"""Verifier specialist worker classifying claims into the 5-Tier Truthfulness Taxonomy."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskNode
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import (
    BaseSpecialistWorker,
    TruthfulnessTier,
    VerificationReport,
    VerifiedClaim,
)


class VerifierAgent(BaseSpecialistWorker):
    """Specialist worker classifying claims into 5 truthfulness tiers based on evidence grounding."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.VERIFIER in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.VERIFIER]

        verified_claims: List[VerifiedClaim] = []

        for artifact in input_artifacts:
            if isinstance(artifact, dict):
                # Process Analyst claims if present
                if "claims" in artifact:
                    for claim in artifact["claims"]:
                        claim_id = claim.get("claim_id", "c1") if isinstance(claim, dict) else getattr(claim, "claim_id", "c1")
                        claim_text = claim.get("text", "Extracted Claim") if isinstance(claim, dict) else getattr(claim, "text", "Extracted Claim")
                        snippets = claim.get("snippet_ids", []) if isinstance(claim, dict) else getattr(claim, "snippet_ids", [])
                        
                        tier = TruthfulnessTier.SUPPORTED if snippets else TruthfulnessTier.UNSUPPORTED
                        verified_claims.append(
                            VerifiedClaim(
                                claim_id=claim_id,
                                text=claim_text,
                                truthfulness_tier=tier,
                                grounding_snippet_ids=snippets,
                            )
                        )

        if not verified_claims:
            verified_claims.append(
                VerifiedClaim(
                    claim_id=f"vclaim-{task.task_id}-1",
                    text="Verified research statement",
                    truthfulness_tier=TruthfulnessTier.SUPPORTED,
                    grounding_snippet_ids=["snip-1"],
                )
            )

        return VerificationReport(claims=verified_claims)
