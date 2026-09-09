from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from .evidence import independent_cross_check, timestep_convergence
from .lorenz import run_lorenz_experiment


@dataclass(frozen=True)
class EvidenceBundle:
    schema_version: str
    experiment_id: str
    generated_at_utc: str
    question: str
    hypothesis: str
    model: str
    parameters: dict[str, Any]
    convergence: list[dict[str, Any]]
    independent_check: dict[str, Any]
    primary_result: dict[str, Any]
    evidence_tier: str
    interpretation: str
    limitations: list[str]
    provenance: dict[str, Any]
    content_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_lorenz_evidence_bundle(
    rho: float,
    *,
    horizon: float = 2.0,
    dts: tuple[float, ...] = (0.02, 0.01, 0.005),
    cross_check_horizon: float = 1.0,
    cross_check_dt: float = 0.001,
) -> EvidenceBundle:
    record, _ = run_lorenz_experiment(rho, dt=dts[-1], steps=round(horizon / dts[-1]))
    convergence = timestep_convergence(rho, horizon=horizon, dts=dts)
    independent = independent_cross_check(rho, horizon=cross_check_horizon, dt=cross_check_dt)
    payload = {
        "record": record.to_dict(),
        "convergence": [point.to_dict() for point in convergence],
        "independent_check": independent,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = sha256(canonical.encode("utf-8")).hexdigest()
    provenance = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "integrator": "fixed-step classical RK4",
        "independent_integrator": "explicit second-order midpoint",
        "deterministic_seed": 0,
        "input_digest_sha256": sha256(canonical.encode("utf-8")).hexdigest(),
    }
    interpretation = (
        f"At rho={rho:g}, the paired-trajectory experiment produced measurable "
        "sensitivity under the declared numerical setup. Convergence and an "
        "independent integrator cross-check provide numerical robustness evidence. "
        "This bundle does not constitute a mathematical proof of chaos."
    )
    return EvidenceBundle(
        schema_version="axiom.science.evidence.v1",
        experiment_id=record.experiment_id,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        question=record.question,
        hypothesis=record.hypothesis,
        model=record.model,
        parameters=record.parameters,
        convergence=[point.to_dict() for point in convergence],
        independent_check=independent,
        primary_result=record.result,
        evidence_tier=record.evidence_tier,
        interpretation=interpretation,
        limitations=[
            "Finite precision and finite timestep limit the numerical claim.",
            "Pointwise trajectory divergence is not by itself a proof of chaos.",
            "The convergence check uses a short horizon and a declared timestep ladder.",
            "The independent midpoint solver is a numerical cross-check, not a formal verifier.",
        ],
        provenance=provenance,
        content_sha256=digest,
    )


def render_markdown_report(bundle: EvidenceBundle) -> str:
    lines = [
        "# AXIOM Lorenz Reproducible Research Report",
        "",
        f"**Experiment:** `{bundle.experiment_id}`  ",
        f"**Evidence tier:** `{bundle.evidence_tier}`  ",
        f"**Content SHA-256:** `{bundle.content_sha256}`",
        "",
        "## Question",
        bundle.question,
        "",
        "## Hypothesis",
        bundle.hypothesis,
        "",
        "## Model",
        f"`{bundle.model}`",
        "",
        "## Numerical evidence",
        "| dt | steps | reference error |",
        "|---:|---:|---:|",
    ]
    for point in bundle.convergence:
        error = point["reference_error"]
        error_text = "reference" if error is None else f"{error:.6e}"
        lines.append(f"| {point['dt']:.6g} | {point['steps']} | {error_text} |")
    lines.extend([
        "",
        "### Independent integration check",
        f"Final-state absolute error: `{bundle.independent_check['final_state_error']:.6e}`",
        f"Relative error: `{bundle.independent_check['relative_error']:.6e}`",
        f"Finite result: `{bundle.independent_check['finite']}`",
        "",
        "## Interpretation",
        bundle.interpretation,
        "",
        "## Limitations",
    ])
    lines.extend(f"- {item}" for item in bundle.limitations)
    lines.extend([
        "",
        "## Provenance",
        f"- Python: `{bundle.provenance['python']}`",
        f"- Platform: `{bundle.provenance['platform']}`",
        f"- Primary integrator: `{bundle.provenance['integrator']}`",
        f"- Independent integrator: `{bundle.provenance['independent_integrator']}`",
        f"- Deterministic seed: `{bundle.provenance['deterministic_seed']}`",
    ])
    return "\n".join(lines) + "\n"


def write_bundle(bundle: EvidenceBundle, json_path: str, markdown_path: str) -> None:
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(bundle.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(markdown_path, "w", encoding="utf-8") as handle:
        handle.write(render_markdown_report(bundle))
