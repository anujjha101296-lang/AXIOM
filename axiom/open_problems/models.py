"""Open Problem Research Lab — domain models.

Conservative: RESOLVED and Millennium claims require explicit verification gates.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _utc_now() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "op") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ResearchStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    MAPPED = "MAPPED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    PARTIALLY_PROGRESSING = "PARTIALLY_PROGRESSING"
    PROMISING_DIRECTION = "PROMISING_DIRECTION"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"
    REFUTED = "REFUTED"
    UNVERIFIED = "UNVERIFIED"


_ALLOWED: dict[ResearchStatus, set[ResearchStatus]] = {
    ResearchStatus.UNKNOWN: {
        ResearchStatus.MAPPED,
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.MAPPED: {
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.BLOCKED,
    },
    ResearchStatus.UNDER_INVESTIGATION: {
        ResearchStatus.PARTIALLY_PROGRESSING,
        ResearchStatus.PROMISING_DIRECTION,
        ResearchStatus.BLOCKED,
        ResearchStatus.REFUTED,
        ResearchStatus.UNVERIFIED,
    },
    ResearchStatus.PARTIALLY_PROGRESSING: {
        ResearchStatus.PROMISING_DIRECTION,
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.BLOCKED,
        ResearchStatus.REFUTED,
        ResearchStatus.UNVERIFIED,
    },
    ResearchStatus.PROMISING_DIRECTION: {
        ResearchStatus.PARTIALLY_PROGRESSING,
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.BLOCKED,
        ResearchStatus.REFUTED,
        ResearchStatus.UNVERIFIED,
        ResearchStatus.RESOLVED,  # requires allow_resolved
    },
    ResearchStatus.BLOCKED: {
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.UNVERIFIED,
    },
    ResearchStatus.REFUTED: set(),
    ResearchStatus.RESOLVED: {ResearchStatus.UNVERIFIED},
    ResearchStatus.UNVERIFIED: {
        ResearchStatus.UNDER_INVESTIGATION,
        ResearchStatus.BLOCKED,
    },
}


def can_transition(frm: ResearchStatus, to: ResearchStatus) -> bool:
    return to in _ALLOWED.get(frm, set())


class ResultKind(str, Enum):
    THEOREM = "THEOREM"
    LEMMA = "LEMMA"
    CONJECTURE = "CONJECTURE"
    HEURISTIC = "HEURISTIC"
    NUMERICAL_EVIDENCE = "NUMERICAL_EVIDENCE"
    FORMAL_PROOF = "FORMAL_PROOF"
    UNVERIFIED_CLAIM = "UNVERIFIED_CLAIM"
    DISPROOF = "DISPROOF"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"


class KnowledgeBucket(str, Enum):
    PROVEN = "WHAT_IS_PROVEN"
    DISPROVEN = "WHAT_IS_DISPROVEN"
    CONJECTURED = "WHAT_IS_CONJECTURED"
    EMPIRICALLY_OBSERVED = "WHAT_IS_EMPIRICALLY_OBSERVED"
    UNKNOWN = "WHAT_IS_UNKNOWN"


class TrackKind(str, Enum):
    ANALYTICAL = "ANALYTICAL"
    COMPUTATIONAL = "COMPUTATIONAL"
    FORMAL = "FORMAL"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    LITERATURE = "LITERATURE"


class StageLevel(int, Enum):
    L1_KNOWN_OUTCOME = 1
    L2_KNOWN_THEOREM = 2
    L3_HISTORICAL = 3
    L4_REPRODUCE = 4
    L5_SMALL_OPEN = 5
    L6_OPEN_SUBPROBLEM = 6
    L7_FRONTIER = 7
    L8_MAJOR_OPEN = 8
    L9_MILLENNIUM = 9


@dataclass
class KnownResult:
    result_id: str
    statement: str
    bucket: KnowledgeBucket
    kind: ResultKind
    evidence_notes: str = ""
    source_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "statement": self.statement,
            "bucket": self.bucket.value,
            "kind": self.kind.value,
            "evidence_notes": self.evidence_notes,
            "source_refs": self.source_refs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnownResult:
        return cls(
            result_id=data["result_id"],
            statement=data["statement"],
            bucket=KnowledgeBucket(data["bucket"]),
            kind=ResultKind(data["kind"]),
            evidence_notes=data.get("evidence_notes", ""),
            source_refs=list(data.get("source_refs", [])),
        )


@dataclass
class LiteratureEntry:
    entry_id: str
    title: str
    authors: str = ""
    date: str = ""
    url: str = ""
    claims: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    provenance: str = "local_seed"
    untrusted: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "authors": self.authors,
            "date": self.date,
            "url": self.url,
            "claims": self.claims,
            "methods": self.methods,
            "limitations": self.limitations,
            "provenance": self.provenance,
            "untrusted": self.untrusted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LiteratureEntry:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class Subproblem:
    subproblem_id: str
    title: str
    statement: str
    difficulty: float = 0.5
    dependency: float = 0.5
    importance: float = 0.5
    tractability: float = 0.5
    verification_difficulty: float = 0.5
    expected_information_gain: float = 0.5
    status: str = "OPEN"
    parent_ids: list[str] = field(default_factory=list)

    @property
    def composite(self) -> float:
        return round(
            0.25 * self.importance
            + 0.2 * self.expected_information_gain
            + 0.2 * self.tractability
            + 0.15 * (1 - self.difficulty)
            + 0.1 * (1 - self.verification_difficulty)
            + 0.1 * (1 - self.dependency),
            4,
        )

    def to_dict(self) -> dict[str, Any]:
        d = {
            "subproblem_id": self.subproblem_id,
            "title": self.title,
            "statement": self.statement,
            "difficulty": self.difficulty,
            "dependency": self.dependency,
            "importance": self.importance,
            "tractability": self.tractability,
            "verification_difficulty": self.verification_difficulty,
            "expected_information_gain": self.expected_information_gain,
            "status": self.status,
            "parent_ids": self.parent_ids,
            "composite": self.composite,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Subproblem:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class Strategy:
    strategy_id: str
    name: str
    kind: TrackKind
    motivation: str
    prerequisites: list[str] = field(default_factory=list)
    related_work: list[str] = field(default_factory=list)
    advantages: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    expected_difficulty: float = 0.5
    verification_method: str = ""
    scientific_potential: float = 0.5
    novelty_potential: float = 0.3
    feasibility: float = 0.5
    information_gain: float = 0.5
    computational_cost: float = 0.4
    formalizability: float = 0.3
    abandoned: bool = False
    abandon_reason: str = ""

    @property
    def rank_score(self) -> float:
        # Not LLM confidence — explicit weighted rubric
        return round(
            0.2 * self.scientific_potential
            + 0.15 * self.information_gain
            + 0.15 * self.feasibility
            + 0.1 * self.formalizability
            + 0.1 * self.novelty_potential
            + 0.1 * (1 - self.computational_cost)
            + 0.1 * (1 - self.expected_difficulty)
            + 0.1 * (1.0 if self.verification_method else 0.3),
            4,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "kind": self.kind.value,
            "motivation": self.motivation,
            "prerequisites": self.prerequisites,
            "related_work": self.related_work,
            "advantages": self.advantages,
            "failure_modes": self.failure_modes,
            "required_tools": self.required_tools,
            "expected_difficulty": self.expected_difficulty,
            "verification_method": self.verification_method,
            "scientific_potential": self.scientific_potential,
            "novelty_potential": self.novelty_potential,
            "feasibility": self.feasibility,
            "information_gain": self.information_gain,
            "computational_cost": self.computational_cost,
            "formalizability": self.formalizability,
            "abandoned": self.abandoned,
            "abandon_reason": self.abandon_reason,
            "rank_score": self.rank_score,
            "not_llm_confidence": True,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Strategy:
        raw = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        if "kind" in raw and not isinstance(raw["kind"], TrackKind):
            raw["kind"] = TrackKind(raw["kind"])
        return cls(**raw)


@dataclass
class ResearchTrack:
    track_id: str
    kind: TrackKind
    strategy_id: str
    independent_state: dict[str, Any] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    contaminated_by: list[str] = field(default_factory=list)
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "kind": self.kind.value,
            "strategy_id": self.strategy_id,
            "independent_state": self.independent_state,
            "findings": self.findings,
            "failures": self.failures,
            "evidence_ids": self.evidence_ids,
            "contaminated_by": self.contaminated_by,
            "active": self.active,
            "independence_enforced": True,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchTrack:
        return cls(
            track_id=data["track_id"],
            kind=TrackKind(data["kind"]),
            strategy_id=data["strategy_id"],
            independent_state=dict(data.get("independent_state", {})),
            findings=list(data.get("findings", [])),
            failures=list(data.get("failures", [])),
            evidence_ids=list(data.get("evidence_ids", [])),
            contaminated_by=list(data.get("contaminated_by", [])),
            active=bool(data.get("active", True)),
        )


@dataclass
class TimelineEvent:
    event_id: str
    event_type: str
    detail: str
    created_at: str = field(default_factory=_utc_now)
    artifact_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "detail": self.detail,
            "created_at": self.created_at,
            "artifact_ids": self.artifact_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimelineEvent:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class ProblemUnderstanding:
    definitions: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    known_results_mentioned: list[str] = field(default_factory=list)
    required_conclusion: str = ""
    equivalent_formulations: list[str] = field(default_factory=list)
    boundary_cases: list[str] = field(default_factory=list)
    special_cases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "definitions": self.definitions,
            "variables": self.variables,
            "assumptions": self.assumptions,
            "known_results_mentioned": self.known_results_mentioned,
            "required_conclusion": self.required_conclusion,
            "equivalent_formulations": self.equivalent_formulations,
            "boundary_cases": self.boundary_cases,
            "special_cases": self.special_cases,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProblemUnderstanding:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class OpenProblem:
    problem_id: str
    title: str
    domain: str
    informal_statement: str
    formal_statement: str = ""
    origin: str = "researcher"
    known_status: str = "open"
    stage_level: int = StageLevel.L1_KNOWN_OUTCOME.value
    research_status: ResearchStatus = ResearchStatus.UNKNOWN
    understanding: ProblemUnderstanding = field(default_factory=ProblemUnderstanding)
    known_results: list[KnownResult] = field(default_factory=list)
    literature: list[LiteratureEntry] = field(default_factory=list)
    research_gaps: list[str] = field(default_factory=list)
    subproblems: list[Subproblem] = field(default_factory=list)
    strategies: list[Strategy] = field(default_factory=list)
    tracks: list[ResearchTrack] = field(default_factory=list)
    campaign_ids: list[str] = field(default_factory=list)
    discovery_ids: list[str] = field(default_factory=list)
    experiment_ids: list[str] = field(default_factory=list)
    proof_attempt_ids: list[str] = field(default_factory=list)
    counterexample_ids: list[str] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    research_objective: str = ""
    owner_id: str | None = None
    report: dict[str, Any] = field(default_factory=dict)
    stopping_reasons: list[str] = field(default_factory=list)
    verification_state: str = "UNVERIFIED"
    created_at: str = field(default_factory=_utc_now)
    last_updated: str = field(default_factory=_utc_now)
    is_millennium_attempt: bool = False
    is_scientific_discovery_claim: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "title": self.title,
            "domain": self.domain,
            "informal_statement": self.informal_statement,
            "formal_statement": self.formal_statement,
            "origin": self.origin,
            "known_status": self.known_status,
            "stage_level": self.stage_level,
            "research_status": self.research_status.value,
            "understanding": self.understanding.to_dict(),
            "known_results": [k.to_dict() for k in self.known_results],
            "literature": [L.to_dict() for L in self.literature],
            "research_gaps": self.research_gaps,
            "subproblems": [s.to_dict() for s in self.subproblems],
            "strategies": [s.to_dict() for s in self.strategies],
            "tracks": [t.to_dict() for t in self.tracks],
            "campaign_ids": self.campaign_ids,
            "discovery_ids": self.discovery_ids,
            "experiment_ids": self.experiment_ids,
            "proof_attempt_ids": self.proof_attempt_ids,
            "counterexample_ids": self.counterexample_ids,
            "timeline": [e.to_dict() for e in self.timeline],
            "constraints": self.constraints,
            "research_objective": self.research_objective,
            "owner_id": self.owner_id,
            "report": self.report,
            "stopping_reasons": self.stopping_reasons,
            "verification_state": self.verification_state,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "is_millennium_attempt": False,
            "is_scientific_discovery_claim": False,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OpenProblem:
        return cls(
            problem_id=data["problem_id"],
            title=data["title"],
            domain=data.get("domain", "mathematics"),
            informal_statement=data["informal_statement"],
            formal_statement=data.get("formal_statement", ""),
            origin=data.get("origin", "researcher"),
            known_status=data.get("known_status", "open"),
            stage_level=int(data.get("stage_level", 1)),
            research_status=ResearchStatus(data.get("research_status", "UNKNOWN")),
            understanding=ProblemUnderstanding.from_dict(data.get("understanding", {})),
            known_results=[KnownResult.from_dict(x) for x in data.get("known_results", [])],
            literature=[LiteratureEntry.from_dict(x) for x in data.get("literature", [])],
            research_gaps=list(data.get("research_gaps", [])),
            subproblems=[Subproblem.from_dict(x) for x in data.get("subproblems", [])],
            strategies=[Strategy.from_dict(x) for x in data.get("strategies", [])],
            tracks=[ResearchTrack.from_dict(x) for x in data.get("tracks", [])],
            campaign_ids=list(data.get("campaign_ids", [])),
            discovery_ids=list(data.get("discovery_ids", [])),
            experiment_ids=list(data.get("experiment_ids", [])),
            proof_attempt_ids=list(data.get("proof_attempt_ids", [])),
            counterexample_ids=list(data.get("counterexample_ids", [])),
            timeline=[TimelineEvent.from_dict(x) for x in data.get("timeline", [])],
            constraints=list(data.get("constraints", [])),
            research_objective=data.get("research_objective", ""),
            owner_id=data.get("owner_id"),
            report=dict(data.get("report", {})),
            stopping_reasons=list(data.get("stopping_reasons", [])),
            verification_state=data.get("verification_state", "UNVERIFIED"),
            created_at=data.get("created_at", _utc_now()),
            last_updated=data.get("last_updated", _utc_now()),
            is_millennium_attempt=False,
            is_scientific_discovery_claim=False,
        )
