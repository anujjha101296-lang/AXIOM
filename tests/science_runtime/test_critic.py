from axiom.science_runtime.critic import critique_evidence


def test_critic_accepts_strong_numerical_bundle():
    critique = critique_evidence(
        evidence_tier="NUMERICAL_OBSERVATION",
        reproducible=True,
        convergence_errors=[0.02, 0.005],
        independent_relative_error=0.001,
        finite=True,
        has_provenance=True,
    )
    assert critique.verdict == "ACCEPT_NUMERICAL_EVIDENCE"
    assert all(critique.checks.values())


def test_critic_rejects_missing_provenance():
    critique = critique_evidence(
        evidence_tier="NUMERICAL_OBSERVATION",
        reproducible=True,
        convergence_errors=[0.02],
        independent_relative_error=0.001,
        finite=True,
        has_provenance=False,
    )
    assert critique.verdict == "REJECT_OR_REPEAT"
    assert "Provenance metadata is incomplete." in critique.concerns


def test_critic_rejects_proof_upgrade():
    critique = critique_evidence(
        evidence_tier="FORMAL_PROOF",
        reproducible=True,
        convergence_errors=[0.02],
        independent_relative_error=0.001,
        finite=True,
        has_provenance=True,
    )
    assert critique.verdict == "REJECT_OR_REPEAT"
    assert critique.checks["evidence_tier_declared"] is False
