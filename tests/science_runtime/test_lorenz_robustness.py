import math

import pytest

from axiom.science_runtime.lorenz_robustness import (
    ROBUSTNESS_VERSION,
    RobustnessConfig,
    build_robustness_observation,
    build_robustness_report,
    classify_rho,
    finite_time_lyapunov,
    poincare_statistics,
    perturbation_sensitivity,
)


def test_robustness_version_and_provenance_are_present():
    obs = build_robustness_observation(
        28.0,
        config=RobustnessConfig(
            dt_grid=(0.02, 0.01),
            horizon=1.0,
            lyapunov_renormalization_interval=0.05,
            poincare_transient=0.5,
            poincare_horizon=1.0,
            poincare_dt=0.01,
        ),
    )
    assert obs.evidence_tier in {"NUMERICAL_OBSERVATION", "NUMERICALLY_ROBUST", "INDEPENDENTLY_CHECKED"}
    assert len(obs.provenance) == 6
    assert all(item.version == ROBUSTNESS_VERSION for item in obs.provenance)
    assert all(len(item.content_hash) == 64 for item in obs.provenance)


def test_finite_time_lyapunov_is_deterministic_and_finite():
    kwargs = dict(dt=0.01, horizon=1.0, perturbation=1e-9, renormalization_interval=0.05)
    first = finite_time_lyapunov(28.0, **kwargs)
    second = finite_time_lyapunov(28.0, **kwargs)
    assert first == pytest.approx(second, rel=0, abs=1e-12)
    assert all(math.isfinite(value) for value in first)


def test_perturbation_sensitivity_is_machine_checkable():
    result = perturbation_sensitivity(28.0, dt=0.01, horizon=1.0)
    assert result["finite"] is True
    assert result["initial_distance"] > 0
    assert result["final_distance"] >= 0
    assert result["growth_factor"] >= 0


def test_poincare_statistics_are_bounded_and_reproducible():
    kwargs = dict(dt=0.01, transient=0.5, horizon=2.0)
    first = poincare_statistics(28.0, **kwargs)
    second = poincare_statistics(28.0, **kwargs)
    assert first == second
    assert first["count"] >= 0
    assert first["x_range"][0] <= first["x_range"][1]
    assert first["z_range"][0] <= first["z_range"][1]


def test_regime_classifier_requires_multiple_observables():
    assert classify_rho(28.0, lyapunov=0.1, poincare_count=5, perturbation_growth=20) == "sensitive_numerical_regime"
    assert classify_rho(1.0, lyapunov=-0.1, poincare_count=0, perturbation_growth=1) == "non_crossing_regime"


def test_report_contains_all_requested_observable_families():
    report = build_robustness_report(
        config=RobustnessConfig(
            rho_values=(28.0,),
            dt_grid=(0.02, 0.01),
            horizon=1.0,
            lyapunov_renormalization_interval=0.05,
            poincare_transient=0.5,
            poincare_horizon=1.0,
            poincare_dt=0.01,
        )
    )
    obs = report["observations"][0]
    for key in (
        "finite_time_lyapunov",
        "perturbation_growth_factor",
        "timestep_reference_error",
        "independent_solver_relative_error",
        "poincare_count",
        "regime",
        "evidence_tier",
    ):
        assert key in obs
    assert report["epistemic_boundary"].endswith("formal proof.")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dt": 0.0},
        {"horizon": 0.0},
        {"perturbation": 0.0},
        {"renormalization_interval": 0.0},
    ],
)
def test_lyapunov_rejects_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        finite_time_lyapunov(28.0, **kwargs)
