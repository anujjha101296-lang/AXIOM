from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .lorenz import State, _rhs, simulate_lorenz


@dataclass(frozen=True)
class ConvergencePoint:
    dt: float
    steps: int
    final_state: State
    mean_abs_x: float
    max_abs_x: float
    reference_error: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "dt": self.dt,
            "steps": self.steps,
            "final_state": self.final_state,
            "mean_abs_x": self.mean_abs_x,
            "max_abs_x": self.max_abs_x,
            "reference_error": self.reference_error,
        }


def _distance(a: State, b: State) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def timestep_convergence(
    rho: float,
    *,
    horizon: float = 2.0,
    dts: tuple[float, ...] = (0.02, 0.01, 0.005),
    initial_state: State = (1.0, 1.0, 1.0),
) -> list[ConvergencePoint]:
    """Compare RK4 solutions over a short, bounded horizon.

    Chaotic systems eventually diverge pointwise even under tiny numerical
    perturbations, so convergence is assessed over a deliberately short horizon
    and against the finest requested timestep. This is numerical verification,
    not a proof of chaos.
    """
    if horizon <= 0 or not dts:
        raise ValueError("horizon and dts must be positive/non-empty")
    if any(dt <= 0 for dt in dts):
        raise ValueError("all dts must be positive")
    points: list[ConvergencePoint] = []
    trajectories: list[tuple[float, list[State]]] = []
    for dt in dts:
        steps = round(horizon / dt)
        if not math.isclose(steps * dt, horizon, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"horizon={horizon} is not an integer multiple of dt={dt}")
        trajectory = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=initial_state)
        trajectories.append((dt, trajectory))

    reference = trajectories[-1][1][-1]
    reference_dt = trajectories[-1][0]
    for dt, trajectory in trajectories:
        xs = [abs(state[0]) for state in trajectory]
        points.append(
            ConvergencePoint(
                dt=dt,
                steps=len(trajectory) - 1,
                final_state=trajectory[-1],
                mean_abs_x=sum(xs) / len(xs),
                max_abs_x=max(xs),
                reference_error=None if dt == reference_dt else _distance(trajectory[-1], reference),
            )
        )
    return points


def _midpoint_step(state: State, dt: float, rho: float, sigma: float, beta: float) -> State:
    """Second-order midpoint integrator, intentionally independent of RK4 code."""
    k1 = _rhs(state, sigma, rho, beta)
    midpoint = tuple(a + 0.5 * dt * b for a, b in zip(state, k1))
    k2 = _rhs(midpoint, sigma, rho, beta)
    return tuple(a + dt * b for a, b in zip(state, k2))  # type: ignore[return-value]


def simulate_lorenz_midpoint(
    rho: float,
    *,
    sigma: float = 10.0,
    beta: float = 8.0 / 3.0,
    dt: float = 0.001,
    steps: int = 2000,
    initial_state: State = (1.0, 1.0, 1.0),
) -> list[State]:
    """Independent numerical integration path for cross-checking RK4."""
    if dt <= 0 or steps <= 0:
        raise ValueError("dt and steps must be positive")
    trajectory = [initial_state]
    state = initial_state
    for _ in range(steps):
        state = _midpoint_step(state, dt, rho, sigma, beta)
        if not all(math.isfinite(v) for v in state):
            raise FloatingPointError("midpoint integration diverged to a non-finite state")
        trajectory.append(state)
    return trajectory


def independent_cross_check(
    rho: float,
    *,
    horizon: float = 1.0,
    dt: float = 0.001,
    initial_state: State = (1.0, 1.0, 1.0),
) -> dict[str, float | bool]:
    """Cross-check RK4 against an independent midpoint implementation."""
    steps = round(horizon / dt)
    if not math.isclose(steps * dt, horizon, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("horizon must be an integer multiple of dt")
    rk4 = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=initial_state)[-1]
    midpoint = simulate_lorenz_midpoint(rho, dt=dt, steps=steps, initial_state=initial_state)[-1]
    error = _distance(rk4, midpoint)
    scale = max(1.0, _distance(midpoint, (0.0, 0.0, 0.0)))
    return {"final_state_error": error, "relative_error": error / scale, "finite": math.isfinite(error)}
