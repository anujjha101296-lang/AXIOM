"""
Department A/B — Scientific & Mathematical Benchmarking
Core benchmark models, scoring schemas, and the level-classification engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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

    def compute_composite(self) -> float:
        """S_composite = Σ w_d × S_d"""
        total = sum(s.weighted_score for s in self.dimension_scores)
        self.composite_score = round(total, 4)
        self.estimated_dimensions = [
            s.dimension.value for s in self.dimension_scores if s.estimated
        ]
        return self.composite_score

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "composite_score": self.composite_score,
            "estimated_dimensions": self.estimated_dimensions,
            "dimensions": {
                s.dimension.value: {
                    "score": s.raw_score,
                    "level": s.level,
                    "level_name": s.level_name,
                    "confidence": s.confidence,
                    "benchmark_count": s.benchmark_count,
                    "estimated": s.estimated,
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
) -> DimensionScore:
    """Construct a DimensionScore with level classification."""
    level = classify_level(raw_score, dimension)
    return DimensionScore(
        dimension=dimension,
        raw_score=round(raw_score, 4),
        level=level,
        level_name=LEVEL_NAMES[level],
        confidence=confidence,
        benchmark_count=benchmark_count,
        estimated=estimated,
    )
