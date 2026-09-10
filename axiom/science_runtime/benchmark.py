from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .critic import critique_evidence
from .report import build_lorenz_evidence_bundle


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    rho: float
    experiment_id: str
    convergence: list[dict[str, Any]]
    independent_check: dict[str, float | bool]
    provenance: dict[str, Any]
    critic: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark": self.name,
            "rho": self.rho,
            "experiment_id": self.experiment_id,
            "convergence": self.convergence,
            "independent_check": self.independent_check,
            "provenance": self.provenance,
            "critic": self.critic,
        }


def run_lorenz_reference_benchmark(rho: float = 28.0) -> BenchmarkResult:
    """Run the deterministic Lorenz benchmark from one canonical evidence bundle."""
    bundle = build_lorenz_evidence_bundle(rho)
    convergence_errors = [
        float(point["reference_error"])
        for point in bundle.convergence
        if point["reference_error"] is not None
    ]
    independent = bundle.independent_check
    critic = critique_evidence(
        evidence_tier=bundle.evidence_tier,
        reproducible=True,
        convergence_errors=convergence_errors,
        independent_relative_error=float(independent["relative_error"]),
        finite=bool(independent["finite"]),
        has_provenance=bool(bundle.provenance),
    )
    return BenchmarkResult(
        name="lorenz-evidence-v1",
        rho=rho,
        experiment_id=bundle.experiment_id,
        convergence=bundle.convergence,
        independent_check=independent,
        provenance=bundle.provenance,
        critic=critic.to_dict(),
    )
