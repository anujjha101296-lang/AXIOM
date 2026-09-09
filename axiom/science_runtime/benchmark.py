from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .critic import critique_evidence
from .evidence import independent_cross_check, timestep_convergence
from .lorenz import run_lorenz_experiment


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    rho: float
    experiment_id: str
    convergence: list[dict[str, Any]]
    independent_check: dict[str, float | bool]
    critic: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark": self.name,
            "rho": self.rho,
            "experiment_id": self.experiment_id,
            "convergence": self.convergence,
            "independent_check": self.independent_check,
            "critic": self.critic,
        }


def run_lorenz_reference_benchmark(rho: float = 28.0) -> BenchmarkResult:
    """Run the fixed, deterministic Lorenz evidence benchmark."""
    record, _ = run_lorenz_experiment(rho, dt=0.01, steps=10000)
    convergence = timestep_convergence(rho)
    convergence_errors = [
        point.reference_error for point in convergence if point.reference_error is not None
    ]
    independent = independent_cross_check(rho)
    critic = critique_evidence(
        evidence_tier=record.evidence_tier,
        reproducible=record.reproducible,
        convergence_errors=convergence_errors,
        independent_relative_error=float(independent["relative_error"]),
        finite=bool(independent["finite"]),
        has_provenance=True,
    )
    return BenchmarkResult(
        name="lorenz-evidence-v1",
        rho=rho,
        experiment_id=record.experiment_id,
        convergence=[point.to_dict() for point in convergence],
        independent_check=independent,
        critic=critic.to_dict(),
    )
