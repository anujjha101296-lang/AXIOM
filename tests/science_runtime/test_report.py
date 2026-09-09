from axiom.science_runtime.report import build_lorenz_evidence_bundle, render_markdown_report


def test_evidence_bundle_is_structured_and_hashed():
    bundle = build_lorenz_evidence_bundle(
        28.0,
        horizon=0.5,
        dts=(0.02, 0.01, 0.005),
        cross_check_horizon=0.25,
        cross_check_dt=0.001,
    )
    assert bundle.schema_version == "axiom.science.evidence.v1"
    assert bundle.evidence_tier == "NUMERICAL_OBSERVATION"
    assert len(bundle.content_sha256) == 64
    assert bundle.provenance["deterministic_seed"] == 0
    assert len(bundle.convergence) == 3


def test_report_explicitly_limits_claim_strength():
    bundle = build_lorenz_evidence_bundle(
        28.0,
        horizon=0.25,
        dts=(0.025, 0.01, 0.005),
        cross_check_horizon=0.1,
        cross_check_dt=0.001,
    )
    report = render_markdown_report(bundle)
    assert "does not constitute a mathematical proof" in report
    assert "Limitations" in report
    assert "Provenance" in report
