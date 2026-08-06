"""
AXIOM operation modes — single source of truth for Demo vs Research honesty.

Demo Mode must never be confused with live scientific capability.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OperationMode(str, Enum):
    """AXIOM has exactly two user-facing operation modes."""

    DEMO = "demo"
    RESEARCH = "research"


class OperationModeContract(BaseModel):
    """
    Machine- and human-readable contract for the active operation mode.
    Included in API responses so clients always know what kind of output they hold.
    """

    mode: OperationMode
    label: str
    purpose: str
    data_source: str
    uses_live_models: bool
    uses_curated_data: bool
    deterministic: bool
    represents_scientific_capability: bool = Field(
        description="False for Demo Mode — outputs are illustrative, not measured capability."
    )
    uncertainty_expected: bool
    disclaimer: str
    evidence_required: bool = Field(
        default=True,
        description="Research claims must carry evidence metadata when in Research Mode.",
    )
    suitable_for: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


DEMO_MODE_CONTRACT = OperationModeContract(
    mode=OperationMode.DEMO,
    label="Demo Mode",
    purpose="Presentation reliability for conferences, investors, YC interviews, and onboarding.",
    data_source="Curated sample dataset (pre-authored, in-memory). Not live ingestion.",
    uses_live_models=False,
    uses_curated_data=True,
    deterministic=True,
    represents_scientific_capability=False,
    uncertainty_expected=False,
    disclaimer=(
        "DEMO MODE — All outputs on this page are curated for presentation reliability. "
        "They do not represent live AI reasoning, measured scientific capability, or "
        "verified research results. For genuine research, use Research Mode."
    ),
    evidence_required=False,
    suitable_for=[
        "conferences",
        "investor presentations",
        "YC interviews",
        "onboarding walkthroughs",
    ],
)

RESEARCH_MODE_CONTRACT = OperationModeContract(
    mode=OperationMode.RESEARCH,
    label="Research Mode",
    purpose="Real scientific work with live documents, models, and honest uncertainty.",
    data_source="Live user uploads (PDFs), SQLite persistence, ModelClient inference.",
    uses_live_models=True,
    uses_curated_data=False,
    deterministic=False,
    represents_scientific_capability=True,
    uncertainty_expected=True,
    disclaimer=(
        "RESEARCH MODE — This session uses live PDFs, real retrieval, and actual AI models. "
        "Results may be incomplete, uncertain, or incorrect. Every claim should be verified "
        "against source documents. Summaries and Q&A use the configured model gateway "
        "(mock fallback when no API key is set)."
    ),
    evidence_required=True,
    suitable_for=[
        "daily researcher workflows",
        "lab pilots",
        "paper reading and note-taking",
        "hypothesis exploration",
    ],
)

RESEARCH_LOOP_MODE_CONTRACT = OperationModeContract(
    mode=OperationMode.RESEARCH,
    label="Research Mode — Autonomous Loop",
    purpose="Bounded autonomous research orchestration with explicit claim classification.",
    data_source="Live loop state (SQLite), heuristic workers unless LLM configured.",
    uses_live_models=False,
    uses_curated_data=False,
    deterministic=False,
    represents_scientific_capability=True,
    uncertainty_expected=True,
    disclaimer=(
        "RESEARCH MODE — Autonomous loop executes with heuristic workers by default. "
        "Claim status (speculative, supported, verified) is explicit on every output. "
        "This is not a claim of autonomous scientific discovery. Benchmark scoring is "
        "keyword-based unless otherwise documented."
    ),
    evidence_required=True,
    suitable_for=[
        "bounded research experiments",
        "workflow evaluation",
        "benchmark runs",
    ],
)
