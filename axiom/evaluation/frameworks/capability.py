"""
Department A/B — Scientific & Mathematical Benchmarking
Core benchmark models, scoring schemas, and the level-classification engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any


class EvidenceState(StrEnum):
    """How a capability score was produced (S0-E4 evidence gate)."""

    MEASURED = "measured"
    SIMULATED = "simulated"
    ESTIMATED = "estimated"
    BASELINE = "baseline"
    UNAVAILABLE = "unavailable"


_EVIDENCE_RANK = {
    EvidenceState.UNAVAILABLE: 0,
    EvidenceState.BASELINE: 1,
    EvidenceState.ESTIMATED: 2,
    EvidenceState.SIMULATED: 3,
    EvidenceState.MEASURED: 4,
}


def derive_evidence_state(
    benchmark_count: int,
    *,
    estimated: bool = False,
    simulated: bool = False,
    baseline: bool = False,
) -> EvidenceState:
    """Classify evidence quality for a dimension score."""
    if baseline:
        return EvidenceState.BASELINE
    if benchmark_count <= 0:
        return EvidenceState.UNAVAILABLE
    if estimated:
        return EvidenceState.ESTIMATED
    if simulated:
        return EvidenceState.SIMULATED
    return EvidenceState.MEASURED


def rollup_evidence_tier(states: dict[str, str]) -> dict[str, Any]:
    """Compute aggregate evidence tier from per-dimension states."""
    if not states:
        return {"aggregate": EvidenceState.UNAVAILABLE.value, "dimensions": {}}
    numeric = {
        k: _EVIDENCE_RANK.get(EvidenceState(v), 0) for k, v in states.items()
    }
    min_rank = min(numeric.values())
    rank_to_state = {v: k.value for k, v in _EVIDENCE_RANK.items()}
    return {
        "aggregate": rank_to_state.get(min_rank, EvidenceState.UNAVAILABLE.value),
        "dimensions": states,
        "weakest_dimension": min(numeric, key=numeric.get),
    }


class CapabilityDimension(str, Enum):
    MATHEMATICAL_REASONING = "mathematical_reasoning"
    PROOF_VERIFICATION = "proof_verification"
    CONJECTURE_GENERATION = "conjecture_generation"
    KNOWLEDGE_QUALITY = "knowledge_quality"
    COUNTEREXAMPLE_SEARCH = "counterexample_search"
    RESEARCH_PLANNING = "research_planning"
    LITERATURE_SYNTHESIS = "literature_synthesis"
    RESEARCH_PRODUCTIVITY = "research_productivity"


# Dimension weights for composite score (sum to 1.0)
DIMENSION_WEIGHTS: dict[CapabilityDimension, float] = {
    CapabilityDimension.MATHEMATICAL_REASONING: 0.20,
    CapabilityDimension.PROOF_VERIFICATION: 0.18,
    CapabilityDimension.CONJECTURE_GENERATION: 0.15,
    CapabilityDimension.KNOWLEDGE_QUALITY: 0.12,
    CapabilityDimension.COUNTEREXAMPLE_SEARCH: 0.12,
    CapabilityDimension.RESEARCH_PLANNING: 0.10,
    CapabilityDimension.LITERATURE_SYNTHESIS: 0.08,
    CapabilityDimension.RESEARCH_PRODUCTIVITY: 0.05,
}

# Level thresholds: [L1, L2, L3, L4, L5] — minimum score to reach each level
LEVEL_THRESHOLDS: dict[CapabilityDimension, list[float]] = {
    CapabilityDimension.MATHEMATICAL_REASONING: [0.40, 0.55, 0.70, 0.82, 0.95],
    CapabilityDimension.PROOF_VERIFICATION: [0.50, 0.60, 0.70, 0.82, 0.95],
    CapabilityDimension.CONJECTURE_GENERATION: [0.10, 0.25, 0.40, 0.60, 0.80],
    CapabilityDimension.KNOWLEDGE_QUALITY: [0.20, 0.40, 0.55, 0.75, 0.90],
    CapabilityDimension.COUNTEREXAMPLE_SEARCH: [0.10, 0.30, 0.50, 0.70, 0.90],
    CapabilityDimension.RESEARCH_PLANNING: [0.20, 0.40, 0.60, 0.75, 0.90],
    CapabilityDimension.LITERATURE_SYNTHESIS: [0.40, 0.55, 0.65, 0.78, 0.90],
    CapabilityDimension.RESEARCH_PRODUCTIVITY: [0.10, 0.25, 0.45, 0.65, 0.85],
}

LEVEL_NAMES: list[str] = [
    "L0: None",
    "L1: Basic",
    "L2: Undergraduate",
    "L3: Graduate",
    "L4: Research-Adjacent",
    "L5: Research-Active",
]

READINESS_COMPOSITE_THRESHOLD = 0.85  # Required for prize submission attempt


@dataclass
class BenchmarkCase:
    """A single benchmark test case."""
    id: str
    description: str
    category: str
    expected_answer: Any
    difficulty: str = "undergraduate"  # undergraduate, graduate, research


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark case."""
    case_id: str
    score: float          # 0.0 = completely wrong, 1.0 = perfect
    passed: bool
    time_ms: float
    notes: str = ""
    raw_output: Any = None


@dataclass
class DimensionScore:
    """Score for a single capability dimension."""
    dimension: CapabilityDimension
    raw_score: float      # 0.0 – 1.0
    level: int            # 0 – 5
    level_name: str
    confidence: float     # 0.0 – 1.0: statistical confidence in score
    benchmark_count: int  # number of benchmark cases contributing
    estimated: bool = False  # True if score is estimated (no benchmark evidence)
    evidence_state: EvidenceState = EvidenceState.UNAVAILABLE

    @property
    def weighted_score(self) -> float:
        return self.raw_score * DIMENSION_WEIGHTS[self.dimension]


@dataclass
class CapabilitySnapshot:
    """Full snapshot of all 8 capability dimension scores."""
    run_id: str
    timestamp: str
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    composite_score: float = 0.0
    estimated_dimensions: list[str] = field(default_factory=list)
    evidence_tier: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def compute_composite(self) -> float:
        """S_composite = Σ w_d × S_d"""
        total = sum(s.weighted_score for s in self.dimension_scores)
        self.composite_score = round(total, 4)
        self.estimated_dimensions = [
            s.dimension.value for s in self.dimension_scores if s.estimated
        ]
        states = {s.dimension.value: s.evidence_state.value for s in self.dimension_scores}
        self.evidence_tier = rollup_evidence_tier(states)
        self.limitations = self._build_limitations()
        return self.composite_score

    def _build_limitations(self) -> list[str]:
        limits: list[str] = []
        for s in self.dimension_scores:
            if s.evidence_state == EvidenceState.SIMULATED:
                limits.append(
                    f"{s.dimension.value}: simulated formal verification — not compiler-backed proof"
                )
            elif s.evidence_state == EvidenceState.ESTIMATED:
                limits.append(f"{s.dimension.value}: estimated score — limited benchmark evidence")
            elif s.evidence_state == EvidenceState.BASELINE:
                limits.append(f"{s.dimension.value}: baseline placeholder — run benchmarks for measurement")
            elif s.benchmark_count == 0:
                limits.append(f"{s.dimension.value}: no benchmark cases executed")
        if self.estimated_dimensions:
            limits.append(
                f"Composite includes estimated dimensions: {', '.join(self.estimated_dimensions)}"
            )
        agg = self.evidence_tier.get("aggregate", EvidenceState.UNAVAILABLE.value)
        if agg in (EvidenceState.SIMULATED.value, EvidenceState.BASELINE.value, EvidenceState.ESTIMATED.value):
            limits.append(f"Aggregate evidence tier is '{agg}' — do not treat scores as independently verified")
        return limits

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "composite_score": self.composite_score,
            "estimated_dimensions": self.estimated_dimensions,
            "evidence_tier": self.evidence_tier,
            "limitations": self.limitations,
            "dimensions": {
                s.dimension.value: {
                    "score": s.raw_score,
                    "level": s.level,
                    "level_name": s.level_name,
                    "confidence": s.confidence,
                    "benchmark_count": s.benchmark_count,
                    "estimated": s.estimated,
                    "evidence_state": s.evidence_state.value,
                    "weighted": s.weighted_score,
                }
                for s in self.dimension_scores
            },
        }


def classify_level(score: float, dimension: CapabilityDimension) -> int:
    """Return the capability level (0–5) for a given score and dimension."""
    thresholds = LEVEL_THRESHOLDS[dimension]
    for level in range(4, -1, -1):  # L5 to L1
        if score >= thresholds[level]:
            return level + 1
    return 0


def make_dimension_score(
    dimension: CapabilityDimension,
    raw_score: float,
    benchmark_count: int,
    confidence: float = 0.8,
    estimated: bool = False,
    simulated: bool = False,
    baseline: bool = False,
    evidence_state: EvidenceState | None = None,
) -> DimensionScore:
    """Construct a DimensionScore with level classification and evidence state."""
    level = classify_level(raw_score, dimension)
    state = evidence_state or derive_evidence_state(
        benchmark_count,
        estimated=estimated,
        simulated=simulated,
        baseline=baseline,
    )
    return DimensionScore(
        dimension=dimension,
        raw_score=round(raw_score, 4),
        level=level,
        level_name=LEVEL_NAMES[level],
        confidence=confidence,
        benchmark_count=benchmark_count,
        estimated=estimated,
        evidence_state=state,
    )


# Dimensions that use simulated formal verification when compilers are absent
_SIMULATED_DIMENSIONS = frozenset({CapabilityDimension.PROOF_VERIFICATION})


def make_dimension_score_from_benchmark(
    dimension: CapabilityDimension,
    raw_score: float,
    benchmark_count: int,
    confidence: float = 0.8,
    estimated: bool = False,
) -> DimensionScore:
    """Build dimension score with correct simulated flag for proof verification."""
    simulated = dimension in _SIMULATED_DIMENSIONS and benchmark_count > 0
    return make_dimension_score(
        dimension,
        raw_score,
        benchmark_count,
        confidence=confidence,
        estimated=estimated,
        simulated=simulated,
    )
