from axiom.science_runtime.lorenz import run_lorenz_experiment, simulate_lorenz


def test_lorenz_is_reproducible():
    a, traj_a = run_lorenz_experiment(28.0, steps=1000)
    b, traj_b = run_lorenz_experiment(28.0, steps=1000)
    assert a.to_dict() == b.to_dict()
    assert traj_a == traj_b


def test_lorenz_parameter_changes_result():
    a, _ = run_lorenz_experiment(20.0, steps=1000)
    b, _ = run_lorenz_experiment(28.0, steps=1000)
    assert a.result["final_state"] != b.result["final_state"]


def test_invalid_integrator_inputs_are_rejected():
    try:
        simulate_lorenz(28.0, dt=0)
    except ValueError:
        pass
    else:
        raise AssertionError("dt=0 must be rejected")
