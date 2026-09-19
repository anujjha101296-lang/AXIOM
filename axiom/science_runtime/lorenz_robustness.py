from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from typing import Any

from .lorenz import State, _distance, simulate_lorenz


ROBUSTNESS_VERSION = "lorenz-robustness-v0.1"
EVIDENCE_TIERS = (
    "NUMERICAL_OBSERVATION",
    "NUMERICALLY_ROBUST",
    "INDEPENDENTLY_CHECKED",
)


@dataclass(frozen=True)
class RobustnessConfig:
    rho_values: tuple[float, ...] = (20.0, 24.0, 28.0, 32.0, 40.0)
    dt_grid: tuple[float, ...] = (0.02, 0.01, 0.005)
    horizon: float = 2.0
    perturbation: float = 1e-9
    lyapunov_renormalization_interval: float = 0.05
    poincare_transient: float = 2.0
    poincare_horizon: float = 10.0
    poincare_dt: float = 0.01
    convergence_tolerance: float = 1.0
    lyapunov_tolerance: float = 0.15
    solver_relative_tolerance: float = 0.10

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MetricProvenance:
    metric: str
    version: str
    rho: float
    dt: float
    horizon: float
    method: str
    parameters: dict[str, float]
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RobustnessObservation:
    rho: float
    finite_time_lyapunov: float
    lyapunov_positive: bool
    perturbation_initial: float
    perturbation_final: float
    perturbation_growth_factor: float
    timestep_reference_error: float
    timestep_robust: bool
    independent_solver_relative_error: float
    independently_checked: bool
    poincare_count: int
    poincare_mean_y: float | None
    poincare_std_y: float | None
    attractor_x_range: tuple[float, float]
    attractor_z_range: tuple[float, float]
    regime: str
    evidence_tier: str
    provenance: tuple[MetricProvenance, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["provenance"] = [item.to_dict() for item in self.provenance]
        return result


def _stable_hash(payload: Any) -> str:
    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _std(values: list[float]) -> float | None:
    if not values:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def finite_time_lyapunov(
    rho: float,
    *,
    dt: float = 0.005,
    horizon: float = 2.0,
    perturbation: float = 1e-9,
    renormalization_interval: float = 0.05,
) -> tuple[float, float]:
    """Estimate a finite-time largest Lyapunov exponent with deterministic resets.

    This is a numerical observable. It is not a proof of chaos.
    """
    if min(dt, horizon, perturbation, renormalization_interval) <= 0:
        raise ValueError("dt, horizon, perturbation and renormalization_interval must be positive")
    steps_per_segment = round(renormalization_interval / dt)
    if not math.isclose(steps_per_segment * dt, renormalization_interval, abs_tol=1e-12):
        raise ValueError("renormalization_interval must be an integer multiple of dt")
    segments = round(horizon / renormalization_interval)
    if not math.isclose(segments * renormalization_interval, horizon, abs_tol=1e-12):
        raise ValueError("horizon must be an integer multiple of renormalization_interval")

    base: State = (1.0, 1.0, 1.0)
    perturbed: State = (1.0 + perturbation, 1.0, 1.0)
    log_sum = 0.0
    final_distance = perturbation

    for _ in range(segments):
        a = simulate_lorenz(rho, dt=dt, steps=steps_per_segment, initial_state=base)[-1]
        b = simulate_lorenz(rho, dt=dt, steps=steps_per_segment, initial_state=perturbed)[-1]
        distance = _distance(a, b)
        if not math.isfinite(distance) or distance <= 0:
            raise FloatingPointError("invalid trajectory separation")
        log_sum += math.log(distance / perturbation)
        direction = tuple((b_i - a_i) * perturbation / distance for a_i, b_i in zip(a, b))
        base = a
        perturbed = tuple(a_i + d_i for a_i, d_i in zip(a, direction))
        final_distance = distance

    return log_sum / horizon, final_distance


def perturbation_sensitivity(
    rho: float,
    *,
    dt: float = 0.01,
    horizon: float = 2.0,
    perturbation: float = 1e-9,
) -> dict[str, float | bool]:
    if min(dt, horizon, perturbation) <= 0:
        raise ValueError("dt, horizon and perturbation must be positive")
    steps = round(horizon / dt)
    if not math.isclose(steps * dt, horizon, abs_tol=1e-12):
        raise ValueError("horizon must be an integer multiple of dt")
    a = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=(1.0, 1.0, 1.0))[-1]
    b = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=(1.0 + perturbation, 1.0, 1.0))[-1]
    final_distance = _distance(a, b)
    growth = final_distance / perturbation
    return {
        "initial_distance": perturbation,
        "final_distance": final_distance,
        "growth_factor": growth,
        "amplified": growth > 1.0,
        "finite": math.isfinite(growth),
    }


def poincare_statistics(
    rho: float,
    *,
    dt: float = 0.01,
    transient: float = 2.0,
    horizon: float = 10.0,
) -> dict[str, Any]:
    if min(dt, transient, horizon) <= 0:
        raise ValueError("dt, transient and horizon must be positive")
    total = round((transient + horizon) / dt)
    trajectory = simulate_lorenz(rho, dt=dt, steps=total)
    transient_steps = round(transient / dt)
    points = trajectory[transient_steps:]
    crossings: list[float] = []
    for previous, current in zip(points, points[1:]):
        if previous[0] < 0 <= current[0] and current[1] > 0:
            crossings.append(current[1])
    xs = [s[0] for s in points]
    zs = [s[2] for s in points]
    return {
        "count": len(crossings),
        "mean_y": _mean(crossings),
        "std_y": _std(crossings),
        "x_range": (min(xs), max(xs)),
        "z_range": (min(zs), max(zs)),
    }


def classify_rho(
    rho: float,
    *,
    lyapunov: float,
    poincare_count: int,
    perturbation_growth: float,
) -> str:
    if lyapunov > 0 and poincare_count >= 3 and perturbation_growth > 10:
        return "sensitive_numerical_regime"
    if poincare_count == 0:
        return "non_crossing_regime"
    return "bounded_nonchaotic_or_unresolved"


def build_robustness_observation(
    rho: float,
    *,
    config: RobustnessConfig | None = None,
) -> RobustnessObservation:
    cfg = config or RobustnessConfig()
    if rho <= 0:
        raise ValueError("rho must be positive")

    # Timestep robustness against the finest requested grid point.
    trajectories = []
    for dt in cfg.dt_grid:
        steps = round(cfg.horizon / dt)
        if not math.isclose(steps * dt, cfg.horizon, abs_tol=1e-12):
            raise ValueError("horizon must be an integer multiple of every dt")
        trajectories.append((dt, simulate_lorenz(rho, dt=dt, steps=steps)))
    reference = trajectories[-1][1][-1]
    reference_dt = trajectories[-1][0]
    timestep_error = max(
        _distance(traj[-1], reference)
        for dt, traj in trajectories
        if dt != reference_dt
    ) if len(trajectories) > 1 else 0.0

    # Independent solver agreement reuses the independent midpoint implementation
    # already exercised by the evidence layer, avoiding a second copy here.
    from .evidence import independent_cross_check
    solver = independent_cross_check(rho, horizon=1.0, dt=0.001)

    lyap, _ = finite_time_lyapunov(
        rho,
        dt=cfg.dt_grid[-1],
        horizon=cfg.horizon,
        perturbation=cfg.perturbation,
        renormalization_interval=cfg.lyapunov_renormalization_interval,
    )
    sensitivity = perturbation_sensitivity(
        rho, dt=cfg.dt_grid[-1], horizon=cfg.horizon, perturbation=cfg.perturbation
    )
    poincare = poincare_statistics(
        rho,
        dt=cfg.poincare_dt,
        transient=cfg.poincare_transient,
        horizon=cfg.poincare_horizon,
    )

    timestep_ok = timestep_error < cfg.convergence_tolerance
    solver_ok = bool(solver["finite"]) and solver["relative_error"] < cfg.solver_relative_tolerance
    lyapunov_ok = math.isfinite(lyap)
    tier = "INDEPENDENTLY_CHECKED" if solver_ok else ("NUMERICALLY_ROBUST" if timestep_ok and lyapunov_ok else "NUMERICAL_OBSERVATION")
    regime = classify_rho(
        rho,
        lyapunov=lyap,
        poincare_count=int(poincare["count"]),
        perturbation_growth=float(sensitivity["growth_factor"]),
    )
    common = {
        "rho": rho,
        "dt": cfg.dt_grid[-1],
        "horizon": cfg.horizon,
        "method": "RK4 + paired perturbation + timestep ladder + independent midpoint + Poincare section",
    }
    provenance = tuple(
        MetricProvenance(
            metric=name,
            version=ROBUSTNESS_VERSION,
            rho=rho,
            dt=cfg.dt_grid[-1],
            horizon=cfg.horizon,
            method=common["method"],
            parameters={"rho": rho, "dt": cfg.dt_grid[-1], "horizon": cfg.horizon},
            content_hash=_stable_hash((ROBUSTNESS_VERSION, name, common)),
        )
        for name in (
            "finite_time_lyapunov",
            "perturbation_sensitivity",
            "timestep_robustness",
            "independent_solver_agreement",
            "poincare_statistics",
            "rho_regime_classification",
        )
    )
    return RobustnessObservation(
        rho=rho,
        finite_time_lyapunov=lyap,
        lyapunov_positive=lyap > 0,
        perturbation_initial=float(sensitivity["initial_distance"]),
        perturbation_final=float(sensitivity["final_distance"]),
        perturbation_growth_factor=float(sensitivity["growth_factor"]),
        timestep_reference_error=timestep_error,
        timestep_robust=timestep_ok,
        independent_solver_relative_error=float(solver["relative_error"]),
        independently_checked=solver_ok,
        poincare_count=int(poincare["count"]),
        poincare_mean_y=poincare["mean_y"],
        poincare_std_y=poincare["std_y"],
        attractor_x_range=tuple(poincare["x_range"]),
        attractor_z_range=tuple(poincare["z_range"]),
        regime=regime,
        evidence_tier=tier,
        provenance=provenance,
    )


def build_robustness_report(
    *,
    config: RobustnessConfig | None = None,
) -> dict[str, Any]:
    cfg = config or RobustnessConfig()
    observations = [build_robustness_observation(rho, config=cfg) for rho in cfg.rho_values]
    return {
        "benchmark": ROBUSTNESS_VERSION,
        "epistemic_boundary": "Numerical observations are not formal proof.",
        "config": cfg.to_dict(),
        "observations": [item.to_dict() for item in observations],
        "summary": {
            "rho_count": len(observations),
            "independently_checked_count": sum(item.independently_checked for item in observations),
            "robust_count": sum(item.timestep_robust for item in observations),
        },
    }
