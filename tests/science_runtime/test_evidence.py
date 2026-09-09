from axiom.science_runtime.evidence import independent_cross_check, timestep_convergence


def test_lorenz_timestep_convergence_is_finite():
    points = timestep_convergence(28.0, horizon=1.0, dts=(0.02, 0.01, 0.005))
    assert [point.steps for point in points] == [50, 100, 200]
    assert all(point.reference_error is None or point.reference_error >= 0.0 for point in points)
    assert all(all(abs(value) < 1e6 for value in point.final_state) for point in points)


def test_lorenz_independent_cross_check_is_finite():
    result = independent_cross_check(28.0, horizon=0.5, dt=0.001)
    assert result["finite"] is True
    assert result["final_state_error"] >= 0.0
    assert result["relative_error"] >= 0.0


def test_convergence_rejects_incompatible_horizon():
    try:
        timestep_convergence(28.0, horizon=1.0, dts=(0.03, 0.01))
    except ValueError as exc:
        assert "integer multiple" in str(exc)
    else:
        raise AssertionError("expected incompatible horizon/dt to be rejected")
