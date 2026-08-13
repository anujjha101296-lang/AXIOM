"""Base abstract class, artifact schemas, and security guards for specialist workers."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field

from axiom.multi_agent.models import AgentRole, TaskNode, TaskGraph
from axiom.multi_agent.budgets import MultiTierBudgetController


class TruthfulnessTier(str, Enum):
    """5-Tier Truthfulness Taxonomy for verification classification."""

    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIED = "UNVERIFIED"


class UnauthorizedToolError(Exception):
    """Raised when an unauthorized or unsafe tool execution is attempted."""

    pass


class EvidenceSnippet(BaseModel):
    """Granular snippet extracted from research documents."""

    snippet_id: str = Field(..., description="Unique snippet identifier")
    doc_id: str = Field(..., description="Source document identifier")
    text: str = Field(..., description="Extract snippet content")
    confidence: float = Field(default=1.0, description="Extraction confidence score")


class EvidencePacket(BaseModel):
    """Collection of evidence snippets returned by search tools."""

    query: str = Field(..., description="Original research query")
    snippets: List[EvidenceSnippet] = Field(default_factory=list, description="Extracted evidence snippets")
    warnings: List[str] = Field(default_factory=list, description="Warnings or execution notes")


class GroundedClaim(BaseModel):
    """Scientific claim extracted by AnalystAgent linked to supporting snippet IDs."""

    claim_id: str = Field(..., description="Unique claim identifier")
    text: str = Field(..., description="Statement of the claim")
    snippet_ids: List[str] = Field(default_factory=list, description="Supporting evidence snippet IDs")
    confidence: float = Field(default=1.0, description="Grounding confidence level")


class AnalystReport(BaseModel):
    """Structured report produced by AnalystAgent."""

    claims: List[GroundedClaim] = Field(default_factory=list, description="Extracted grounded claims")
    open_questions: List[str] = Field(default_factory=list, description="Open research questions")


class ContradictionItem(BaseModel):
    """Cross-document contradiction surfaced by CriticAgent."""

    claim_id: str = Field(..., description="Target claim identifier")
    doc_id_1: str = Field(..., description="First document ID in conflict")
    doc_id_2: str = Field(..., description="Second document ID in conflict")
    description: str = Field(..., description="Detailed conflict explanation")
    snippet_ids: List[str] = Field(default_factory=list, description="Associated snippet IDs")


class CritiqueResult(BaseModel):
    """Adversarial review outcome produced by CriticAgent."""

    claims_reviewed: int = Field(default=0, description="Total claims reviewed")
    has_contradictions: bool = Field(default=False, description="Flag indicating presence of contradictions")
    passed: bool = Field(default=True, description="Whether critique passed without fatal flaws")
    contradictions: List[ContradictionItem] = Field(default_factory=list, description="Surfaced contradictions")
    unbacked_claim_ids: List[str] = Field(default_factory=list, description="Claims lacking evidence grounding")


class VerifiedClaim(BaseModel):
    """Verified claim classified into the 5-Tier Truthfulness Taxonomy."""

    claim_id: str = Field(..., description="Target claim identifier")
    text: str = Field(..., description="Statement of the verified claim")
    truthfulness_tier: TruthfulnessTier = Field(..., description="Assigned truthfulness tier")
    grounding_snippet_ids: List[str] = Field(default_factory=list, description="Grounding snippet IDs")


class VerificationReport(BaseModel):
    """Verification classification report produced by VerifierAgent."""

    claims: List[VerifiedClaim] = Field(default_factory=list, description="Verified claims list")


class SynthesisArtifact(BaseModel):
    """Final multi-agent research synthesis report."""

    executive_summary: str = Field(..., description="Executive summary")
    verified_findings: List[Dict[str, Any]] = Field(default_factory=list, description="Verified findings")
    rejected_claims: List[Dict[str, Any]] = Field(default_factory=list, description="Rejected or ungrounded claims")
    surfaced_contradictions: List[Dict[str, Any]] = Field(default_factory=list, description="Surfaced document contradictions")
    limitations: List[str] = Field(default_factory=list, description="Methodological or evidence limitations")
    provenance_doc_ids: List[str] = Field(default_factory=list, description="Source provenance document IDs")


# Strict Tool Allowlist
ALLOWED_TOOLS = {
    "SEARCH_PROJECT_KNOWLEDGE",
    "READ_DOCUMENT_EVIDENCE",
    "ASK_GROUNDED_RESEARCH_ENGINE",
}


def sanitize_input(text: str) -> str:
    """Neutralize prompt injection attempts."""
    dangerous_keywords = ["IGNORE PREVIOUS INSTRUCTIONS", "rm -rf", "SYSTEM_SHELL_EXEC"]
    sanitized = text
    for kw in dangerous_keywords:
        if kw in sanitized:
            sanitized = sanitized.replace(kw, "[REDACTED_PROMPT_INJECTION]")
    return sanitized


def execute_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool with strict allowlist enforcement and input sanitization guards."""
    if tool_name not in ALLOWED_TOOLS:
        raise UnauthorizedToolError(f"Tool '{tool_name}' is not in allowed tool registry.")
    if "command" in payload or "shell" in payload:
        raise UnauthorizedToolError("Shell execution is strictly forbidden.")
    query = sanitize_input(str(payload.get("query", "")))
    return {"status": "success", "query": query, "result": f"Executed {tool_name} successfully."}


class DeterministicLLMMock:
    """Deterministic LLM mock returning Pydantic artifacts by role/prompt."""

    def __init__(self):
        self.responses: Dict[AgentRole, BaseModel] = {}

    def register_response(self, role: AgentRole, artifact: BaseModel) -> None:
        self.responses[role] = artifact

    def generate(self, role: AgentRole, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        if role in self.responses:
            return self.responses[role]

        if role == AgentRole.ORCHESTRATOR:
            g = TaskGraph()
            g.add_node(TaskNode(task_id="A", agent_role=AgentRole.RESEARCHER, description="Search docs"))
            g.add_node(TaskNode(task_id="B", agent_role=AgentRole.ANALYST, description="Analyze evidence", depends_on=["A"]))
            g.add_node(TaskNode(task_id="C", agent_role=AgentRole.CRITIC, description="Review claims", depends_on=["B"]))
            g.add_node(TaskNode(task_id="D", agent_role=AgentRole.SYNTHESIS, description="Synthesize report", depends_on=["C"]))
            return g
        elif role == AgentRole.RESEARCHER:
            return EvidencePacket(
                query=prompt,
                snippets=[EvidenceSnippet(snippet_id="snip-1", doc_id="doc-1", text="Evidence snippet text")]
            )
        elif role == AgentRole.ANALYST:
            return AnalystReport(
                claims=[GroundedClaim(claim_id="claim-1", text="Zeta zeros bound theorem", snippet_ids=["snip-1"])]
            )
        elif role == AgentRole.CRITIC:
            return CritiqueResult(claims_reviewed=1, has_contradictions=False, passed=True)
        elif role == AgentRole.VERIFIER:
            return VerificationReport(
                claims=[VerifiedClaim(claim_id="claim-1", text="Bound theorem", truthfulness_tier=TruthfulnessTier.SUPPORTED)]
            )
        elif role == AgentRole.SYNTHESIS:
            return SynthesisArtifact(
                executive_summary="Research synthesis complete.",
                verified_findings=[{"claim": "Bound theorem", "tier": "SUPPORTED"}],
                provenance_doc_ids=["doc-1"]
            )
        return schema.construct() if hasattr(schema, "construct") else schema()


class BaseSpecialistWorker(ABC):
    """Abstract base class for all specialist role workers."""

    def __init__(self, llm_mock: Optional[Any] = None):
        self.llm_mock = llm_mock

    @abstractmethod
    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        """Execute task logic and produce a Pydantic output artifact."""
        pass
