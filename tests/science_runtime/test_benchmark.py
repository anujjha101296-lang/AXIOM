from axiom.science_runtime.benchmark import run_lorenz_reference_benchmark


def test_reference_benchmark_has_stable_contract():
    result = run_lorenz_reference_benchmark(28.0)
    assert result.name == "lorenz-evidence-v1"
    assert result.rho == 28.0
    assert result.experiment_id.startswith("lorenz-")
    assert len(result.convergence) == 3
    assert result.independent_check["finite"] is True
    assert result.critic["verdict"] in {"ACCEPT_NUMERICAL_EVIDENCE", "REJECT_OR_REPEAT"}


def test_reference_benchmark_never_claims_formal_proof():
    result = run_lorenz_reference_benchmark(28.0)
    assert result.critic["checks"]["evidence_tier_declared"] is True
