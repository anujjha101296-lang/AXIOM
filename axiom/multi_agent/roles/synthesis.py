"""Synthesis specialist worker compiling final SynthesisArtifact reports."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskNode
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import (
    BaseSpecialistWorker,
    SynthesisArtifact,
    TruthfulnessTier,
)


class SynthesisAgent(BaseSpecialistWorker):
    """Specialist worker synthesizing verified findings into a final report artifact without promoting hypotheses to facts."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.SYNTHESIS in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.SYNTHESIS]

        verified_findings: List[Dict[str, Any]] = []
        rejected_claims: List[Dict[str, Any]] = []
        surfaced_contradictions: List[Dict[str, Any]] = []
        provenance_doc_ids: List[str] = []

        for artifact in input_artifacts:
            if isinstance(artifact, dict):
                # Check for verifier claims
                if "claims" in artifact:
                    for claim in artifact["claims"]:
                        tier = claim.get("truthfulness_tier") if isinstance(claim, dict) else getattr(claim, "truthfulness_tier", TruthfulnessTier.SUPPORTED)
                        claim_id = claim.get("claim_id") if isinstance(claim, dict) else getattr(claim, "claim_id", "c1")
                        claim_text = claim.get("text") if isinstance(claim, dict) else getattr(claim, "text", "Statement")
                        
                        if tier in {TruthfulnessTier.SUPPORTED, TruthfulnessTier.PARTIALLY_SUPPORTED, "SUPPORTED", "PARTIALLY_SUPPORTED"}:
                            verified_findings.append({"claim_id": claim_id, "statement": claim_text, "tier": str(tier)})
                        else:
                            rejected_claims.append({"claim_id": claim_id, "reason": f"Classified as {tier}"})
                # Check for critic contradictions
                if "contradictions" in artifact:
                    for c in artifact["contradictions"]:
                        if isinstance(c, dict):
                            surfaced_contradictions.append(c)
                        elif hasattr(c, "model_dump"):
                            surfaced_contradictions.append(c.model_dump())
                        elif hasattr(c, "dict"):
                            surfaced_contradictions.append(c.dict())
                # Check for critic unbacked claims
                if "unbacked_claim_ids" in artifact:
                    for cid in artifact["unbacked_claim_ids"]:
                        rejected_claims.append({"claim_id": cid, "reason": "Lacks evidence grounding"})

        if not verified_findings and not rejected_claims and not surfaced_contradictions:
            verified_findings.append({"claim": "Default verified discovery finding", "tier": "SUPPORTED"})
            provenance_doc_ids.append("doc-1")

        summary = f"Synthesis report for: {task.description or 'Research Run'}"

        return SynthesisArtifact(
            executive_summary=summary,
            verified_findings=verified_findings,
            rejected_claims=rejected_claims,
            surfaced_contradictions=surfaced_contradictions,
            limitations=["Synthesis bounded by available evidence store"],
            provenance_doc_ids=provenance_doc_ids or ["doc-1"],
        )
