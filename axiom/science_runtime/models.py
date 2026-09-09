from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LorenzResult:
    sigma: float
    rho: float
    beta: float
    dt: float
    steps: int
    initial_state: tuple[float, float, float]
    final_state: tuple[float, float, float]
    mean_abs_x: float
    max_abs_x: float
    divergence_indicator: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentRecord:
    experiment_id: str
    question: str
    hypothesis: str
    model: str
    parameters: dict[str, float]
    method: str
    seed: int
    result: dict[str, Any]
    evidence_tier: str
    reproducible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
