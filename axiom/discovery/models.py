"""AXIOM Scientific Discovery Engine — domain models.

Conservative by design: hypotheses are not facts; computational evidence is not proof.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "disc") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class DiscoveryStatus(str, Enum):
    GENERATED = "GENERATED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    SUPPORTED = "SUPPORTED"
    CHALLENGED = "CHALLENGED"
    REFUTED = "REFUTED"
    UNRESOLVED = "UNRESOLVED"
    VERIFIED = "VERIFIED"
    PUBLISHED_CANDIDATE = "PUBLISHED_CANDIDATE"
    REJECTED = "REJECTED"


# Explicit allowed transitions — silent jumps are forbidden.
_ALLOWED_TRANSITIONS: dict[DiscoveryStatus, set[DiscoveryStatus]] = {
    DiscoveryStatus.GENERATED: {
        DiscoveryStatus.UNDER_INVESTIGATION,
        DiscoveryStatus.REJECTED,
        DiscoveryStatus.UNRESOLVED,
    },
    DiscoveryStatus.UNDER_INVESTIGATION: {
        DiscoveryStatus.SUPPORTED,
        DiscoveryStatus.CHALLENGED,
        DiscoveryStatus.REFUTED,
        DiscoveryStatus.UNRESOLVED,
        DiscoveryStatus.REJECTED,
    },
    DiscoveryStatus.SUPPORTED: {
        DiscoveryStatus.CHALLENGED,
        DiscoveryStatus.REFUTED,
        DiscoveryStatus.UNRESOLVED,
        DiscoveryStatus.VERIFIED,  # requires external verification evidence + gate
        DiscoveryStatus.REJECTED,
    },
    DiscoveryStatus.CHALLENGED: {
        DiscoveryStatus.SUPPORTED,
        DiscoveryStatus.REFUTED,
        DiscoveryStatus.UNRESOLVED,
        DiscoveryStatus.UNDER_INVESTIGATION,
        DiscoveryStatus.REJECTED,
    },
    DiscoveryStatus.REFUTED: {
        DiscoveryStatus.REJECTED,  # terminal-ish; no casual resurrection
    },
    DiscoveryStatus.UNRESOLVED: {
        DiscoveryStatus.UNDER_INVESTIGATION,
        DiscoveryStatus.REJECTED,
    },
    DiscoveryStatus.VERIFIED: {
        DiscoveryStatus.PUBLISHED_CANDIDATE,
        DiscoveryStatus.CHALLENGED,  # new attack may reopen
    },
    DiscoveryStatus.PUBLISHED_CANDIDATE: {
        DiscoveryStatus.CHALLENGED,
        DiscoveryStatus.REJECTED,
    },
    DiscoveryStatus.REJECTED: set(),
}


def can_transition(frm: DiscoveryStatus, to: DiscoveryStatus) -> bool:
    if frm == to:
        return True
    return to in _ALLOWED_TRANSITIONS.get(frm, set())


class NoveltyStatus(str, Enum):
    LIKELY_KNOWN = "LIKELY_KNOWN"
    POSSIBLY_KNOWN = "POSSIBLY_KNOWN"
    RELATED_WORK_FOUND = "RELATED_WORK_FOUND"
    NO_RELEVANT_PRIOR_WORK_FOUND = "NO_RELEVANT_PRIOR_WORK_FOUND"
    INSUFFICIENT_SEARCH = "INSUFFICIENT_SEARCH"


class ConfidenceChannel(str, Enum):
    MODEL = "MODEL_CONFIDENCE"
    EVIDENCE = "EVIDENCE_CONFIDENCE"
    EXPERIMENT = "EXPERIMENT_CONFIDENCE"
    REPRODUCTION = "REPRODUCTION_CONFIDENCE"
    FORMAL = "FORMAL_VERIFICATION"
    HUMAN = "HUMAN_REVIEW"


@dataclass
class ScientificConfidence:
    """Separate confidence channels — never collapse into one unexplained score."""

    model_confidence: float | None = None
    evidence_confidence: float | None = None
    experiment_confidence: float | None = None
    reproduction_confidence: float | None = None
    formal_verification: bool = False
    human_review: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_confidence": self.model_confidence,
            "evidence_confidence": self.evidence_confidence,
            "experiment_confidence": self.experiment_confidence,
            "reproduction_confidence": self.reproduction_confidence,
            "formal_verification": self.formal_verification,
            "human_review": self.human_review,
            "notes": self.notes,
            "combined_forbidden": True,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScientificConfidence:
        return cls(
            model_confidence=data.get("model_confidence"),
            evidence_confidence=data.get("evidence_confidence"),
            experiment_confidence=data.get("experiment_confidence"),
            reproduction_confidence=data.get("reproduction_confidence"),
            formal_verification=bool(data.get("formal_verification", False)),
            human_review=bool(data.get("human_review", False)),
            notes=str(data.get("notes", "")),
        )


@dataclass
class ResearchOpportunity:
    """A scored research opportunity — not a discovery."""

    opportunity_id: str
    title: str
    description: str
    gap_ids: list[str] = field(default_factory=list)
    scientific_importance: float = 0.5
    gap_evidence: float = 0.5
    novelty_likelihood: float = 0.3
    feasibility: float = 0.5
    potential_impact: float = 0.5
    verification_difficulty: float = 0.5
    computational_cost: float = 0.5
    expected_information_gain: float = 0.5
    composite_score: float = 0.0
    rationale: str = ""
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "description": self.description,
            "gap_ids": self.gap_ids,
            "scientific_importance": self.scientific_importance,
            "gap_evidence": self.gap_evidence,
            "novelty_likelihood": self.novelty_likelihood,
            "feasibility": self.feasibility,
            "potential_impact": self.potential_impact,
            "verification_difficulty": self.verification_difficulty,
            "computational_cost": self.computational_cost,
            "expected_information_gain": self.expected_information_gain,
            "composite_score": self.composite_score,
            "rationale": self.rationale,
            "created_at": self.created_at,
            "label": "RESEARCH_OPPORTUNITY",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchOpportunity:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class HypothesisRecord:
    hypothesis_id: str
    statement: str
    motivation: str = ""
    assumptions: list[str] = field(default_factory=list)
    supporting_evidence_notes: list[str] = field(default_factory=list)
    contradicting_notes: list[str] = field(default_factory=list)
    predictions: list[str] = field(default_factory=list)
    potential_counterexamples: list[str] = field(default_factory=list)
    required_experiments: list[str] = field(default_factory=list)
    proof_strategy: str = ""
    disproof_strategy: str = ""
    expected_information_gain: float = 0.5
    rejected: bool = False
    rejection_reason: str = ""
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "motivation": self.motivation,
            "assumptions": self.assumptions,
            "supporting_evidence_notes": self.supporting_evidence_notes,
            "contradicting_notes": self.contradicting_notes,
            "predictions": self.predictions,
            "potential_counterexamples": self.potential_counterexamples,
            "required_experiments": self.required_experiments,
            "proof_strategy": self.proof_strategy,
            "disproof_strategy": self.disproof_strategy,
            "expected_information_gain": self.expected_information_gain,
            "rejected": self.rejected,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HypothesisRecord:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class PredictionRecord:
    prediction_id: str
    hypothesis_id: str
    statement: str
    testable: bool = True
    experiment_hint: str = ""
    status: str = "pending"  # pending | confirmed | falsified | inconclusive
    result_notes: str = ""
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "testable": self.testable,
            "experiment_hint": self.experiment_hint,
            "status": self.status,
            "result_notes": self.result_notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PredictionRecord:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class NoveltyAssessment:
    status: NoveltyStatus = NoveltyStatus.INSUFFICIENT_SEARCH
    related_source_ids: list[str] = field(default_factory=list)
    related_titles: list[str] = field(default_factory=list)
    search_notes: str = ""
    searched_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "related_source_ids": self.related_source_ids,
            "related_titles": self.related_titles,
            "search_notes": self.search_notes,
            "searched_at": self.searched_at,
            "discovery_claim_forbidden": True,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NoveltyAssessment:
        return cls(
            status=NoveltyStatus(data.get("status", NoveltyStatus.INSUFFICIENT_SEARCH.value)),
            related_source_ids=list(data.get("related_source_ids", [])),
            related_titles=list(data.get("related_titles", [])),
            search_notes=str(data.get("search_notes", "")),
            searched_at=str(data.get("searched_at", _utc_now())),
        )


@dataclass
class AttackRecord:
    attack_id: str
    attack_type: str  # support | disprove | literature | computational | formal | skeptical
    summary: str
    outcome: str = "inconclusive"  # supporting | challenging | refuting | inconclusive
    artifact_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "attack_id": self.attack_id,
            "attack_type": self.attack_type,
            "summary": self.summary,
            "outcome": self.outcome,
            "artifact_ids": self.artifact_ids,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AttackRecord:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class StatusTransition:
    from_status: str
    to_status: str
    reason: str
    actor: str = "system"
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_status": self.from_status,
            "to_status": self.to_status,
            "reason": self.reason,
            "actor": self.actor,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatusTransition:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class Discovery:
    """First-class discovery investigation object (not a claim of scientific discovery)."""

    discovery_id: str
    research_question: str
    status: DiscoveryStatus = DiscoveryStatus.GENERATED
    campaign_id: str | None = None
    owner_id: str | None = None
    knowledge_context: str = ""
    research_gap_ids: list[str] = field(default_factory=list)
    opportunity: ResearchOpportunity | None = None
    hypotheses: list[HypothesisRecord] = field(default_factory=list)
    predictions: list[PredictionRecord] = field(default_factory=list)
    supporting_evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    experiment_ids: list[str] = field(default_factory=list)
    proof_attempt_ids: list[str] = field(default_factory=list)
    counterexample_ids: list[str] = field(default_factory=list)
    attacks: list[AttackRecord] = field(default_factory=list)
    novelty: NoveltyAssessment = field(default_factory=NoveltyAssessment)
    confidence: ScientificConfidence = field(default_factory=ScientificConfidence)
    history: list[StatusTransition] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
    memory: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_id": self.discovery_id,
            "research_question": self.research_question,
            "status": self.status.value,
            "campaign_id": self.campaign_id,
            "owner_id": self.owner_id,
            "knowledge_context": self.knowledge_context,
            "research_gap_ids": self.research_gap_ids,
            "opportunity": self.opportunity.to_dict() if self.opportunity else None,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "predictions": [p.to_dict() for p in self.predictions],
            "supporting_evidence_ids": self.supporting_evidence_ids,
            "contradicting_evidence_ids": self.contradicting_evidence_ids,
            "experiment_ids": self.experiment_ids,
            "proof_attempt_ids": self.proof_attempt_ids,
            "counterexample_ids": self.counterexample_ids,
            "attacks": [a.to_dict() for a in self.attacks],
            "novelty": self.novelty.to_dict(),
            "confidence": self.confidence.to_dict(),
            "history": [h.to_dict() for h in self.history],
            "report": self.report,
            "memory": self.memory,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_scientific_discovery_claim": False,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Discovery:
        opp = data.get("opportunity")
        return cls(
            discovery_id=data["discovery_id"],
            research_question=data["research_question"],
            status=DiscoveryStatus(data.get("status", DiscoveryStatus.GENERATED.value)),
            campaign_id=data.get("campaign_id"),
            owner_id=data.get("owner_id"),
            knowledge_context=data.get("knowledge_context", ""),
            research_gap_ids=list(data.get("research_gap_ids", [])),
            opportunity=ResearchOpportunity.from_dict(opp) if opp else None,
            hypotheses=[HypothesisRecord.from_dict(h) for h in data.get("hypotheses", [])],
            predictions=[PredictionRecord.from_dict(p) for p in data.get("predictions", [])],
            supporting_evidence_ids=list(data.get("supporting_evidence_ids", [])),
            contradicting_evidence_ids=list(data.get("contradicting_evidence_ids", [])),
            experiment_ids=list(data.get("experiment_ids", [])),
            proof_attempt_ids=list(data.get("proof_attempt_ids", [])),
            counterexample_ids=list(data.get("counterexample_ids", [])),
            attacks=[AttackRecord.from_dict(a) for a in data.get("attacks", [])],
            novelty=NoveltyAssessment.from_dict(data.get("novelty", {})),
            confidence=ScientificConfidence.from_dict(data.get("confidence", {})),
            history=[StatusTransition.from_dict(h) for h in data.get("history", [])],
            report=dict(data.get("report", {})),
            memory=list(data.get("memory", [])),
            created_at=data.get("created_at", _utc_now()),
            updated_at=data.get("updated_at", _utc_now()),
        )


__all__ = [
    "Discovery",
    "DiscoveryStatus",
    "NoveltyStatus",
    "ResearchOpportunity",
    "HypothesisRecord",
    "PredictionRecord",
    "NoveltyAssessment",
    "AttackRecord",
    "ScientificConfidence",
    "StatusTransition",
    "can_transition",
    "_new_id",
    "_utc_now",
]
