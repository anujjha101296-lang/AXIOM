"""
Department A — Mathematical Knowledge
Pydantic schema models for all MIP mathematical entities.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from axiom.mip.knowledge.ontology import (
    EpistemicStatus,
    MathDomain,
    MathEdgeType,
    MathObjectType,
)


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.utcnow()


# ─────────────────────────── Node Models ───────────────────────────


class MathNode(BaseModel):
    """Base model for all mathematical knowledge nodes."""

    id: str = Field(default_factory=_new_id)
    object_type: MathObjectType
    name: str
    statement: str
    domain: MathDomain = MathDomain.UNKNOWN
    epistemic_status: EpistemicStatus = EpistemicStatus.UNKNOWN
    axiom_system: str | None = None
    source_ref: str | None = None  # arXiv ID, DOI, or manual
    latex: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    class Config:
        use_enum_values = True


class TheoremNode(MathNode):
    object_type: MathObjectType = MathObjectType.THEOREM
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    proof_id: str | None = None


class LemmaNode(MathNode):
    object_type: MathObjectType = MathObjectType.LEMMA
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    parent_theorem_id: str | None = None


class DefinitionNode(MathNode):
    object_type: MathObjectType = MathObjectType.DEFINITION
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    formal_definition: str | None = None


class ConjectureNode(MathNode):
    object_type: MathObjectType = MathObjectType.CONJECTURE
    epistemic_status: EpistemicStatus = EpistemicStatus.CONJECTURED
    novelty_score: float = 0.0
    proposed_by: str = "axiom_mip"


class OpenProblemNode(MathNode):
    object_type: MathObjectType = MathObjectType.OPEN_PROBLEM
    epistemic_status: EpistemicStatus = EpistemicStatus.OPEN
    prize_amount_usd: int | None = None
    prize_org: str | None = None
    millennium_problem: bool = False


class ProofNode(MathNode):
    object_type: MathObjectType = MathObjectType.PROOF
    epistemic_status: EpistemicStatus = EpistemicStatus.VERIFIED
    proves_id: str | None = None
    formal_system: str | None = None  # lean4, coq, isabelle, informal
    proof_script: str | None = None


class CounterexampleNode(MathNode):
    object_type: MathObjectType = MathObjectType.COUNTEREXAMPLE
    epistemic_status: EpistemicStatus = EpistemicStatus.REFUTED
    refutes_id: str | None = None
    witness_values: dict[str, Any] = Field(default_factory=dict)


class EquivalentStatementNode(MathNode):
    object_type: MathObjectType = MathObjectType.EQUIVALENT_STATEMENT
    equivalent_to_id: str | None = None
    equivalence_proof_id: str | None = None


# ─────────────────────────── Edge Models ───────────────────────────


class MathEdge(BaseModel):
    """Directed edge between two mathematical nodes."""

    id: str = Field(default_factory=_new_id)
    source_id: str
    target_id: str
    edge_type: MathEdgeType
    confidence: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)

    class Config:
        use_enum_values = True


# ─────────────────────── API Payload Models ────────────────────────


class IngestRequest(BaseModel):
    object_type: MathObjectType
    name: str
    statement: str
    domain: MathDomain = MathDomain.UNKNOWN
    latex: str | None = None
    source_ref: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    node_id: str
    object_type: str
    name: str
    domain: str
    message: str


class LookupResponse(BaseModel):
    found: bool
    node: dict[str, Any] | None = None
    similar: list[dict[str, Any]] = Field(default_factory=list)


# ─────────────────── Millennium Prize Problem IDs ──────────────────

MILLENNIUM_PROBLEMS: dict[str, OpenProblemNode] = {
    "riemann_hypothesis": OpenProblemNode(
        id="riemann_hypothesis",
        name="Riemann Hypothesis",
        statement=(
            "All non-trivial zeros of the Riemann zeta function ζ(s) have real part 1/2."
        ),
        domain=MathDomain.NUMBER_THEORY,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        latex=r"\text{Re}(s) = \frac{1}{2} \text{ for all } \zeta(s) = 0, \, s \notin \{-2,-4,-6,\ldots\}",
        tags=["riemann", "zeta function", "number theory", "analytic continuation"],
    ),
    "p_vs_np": OpenProblemNode(
        id="p_vs_np",
        name="P vs NP",
        statement=(
            "Does P = NP? Can every problem whose solution can be verified in polynomial "
            "time also be solved in polynomial time?"
        ),
        domain=MathDomain.COMPUTATIONAL,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        tags=["complexity", "p vs np", "computation", "logic"],
    ),
    "navier_stokes": OpenProblemNode(
        id="navier_stokes",
        name="Navier–Stokes Existence and Smoothness",
        statement=(
            "Do smooth solutions to the Navier–Stokes equations in three dimensions "
            "always exist, and if so, are they bounded (smooth)?"
        ),
        domain=MathDomain.MATHEMATICAL_PHYSICS,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        tags=["navier-stokes", "fluid dynamics", "pde", "smoothness"],
    ),
    "birch_swinnerton_dyer": OpenProblemNode(
        id="birch_swinnerton_dyer",
        name="Birch and Swinnerton-Dyer Conjecture",
        statement=(
            "The rank of an elliptic curve over the rationals equals the order of the "
            "zero of its L-function at s=1."
        ),
        domain=MathDomain.ALGEBRAIC_GEOMETRY,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        tags=["elliptic curve", "l-function", "bsd", "algebraic geometry"],
    ),
    "yang_mills": OpenProblemNode(
        id="yang_mills",
        name="Yang–Mills Existence and Mass Gap",
        statement=(
            "Prove that quantum Yang–Mills theory exists and has a positive mass gap Δ > 0."
        ),
        domain=MathDomain.MATHEMATICAL_PHYSICS,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        tags=["yang-mills", "quantum field theory", "mass gap", "gauge theory"],
    ),
    "hodge_conjecture": OpenProblemNode(
        id="hodge_conjecture",
        name="Hodge Conjecture",
        statement=(
            "On a smooth complex projective algebraic variety, every Hodge class is a "
            "rational linear combination of classes of algebraic cycles."
        ),
        domain=MathDomain.ALGEBRAIC_GEOMETRY,
        epistemic_status=EpistemicStatus.OPEN,
        prize_amount_usd=1_000_000,
        prize_org="Clay Mathematics Institute",
        millennium_problem=True,
        tags=["hodge", "algebraic cycle", "cohomology", "algebraic geometry"],
    ),
}
