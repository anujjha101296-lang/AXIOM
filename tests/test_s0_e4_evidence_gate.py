"""S0-E4 evidence gate tests — capability and prize-readiness truthfulness."""

from __future__ import annotations

import os
import tempfile

import pytest

from axiom.config import settings
from axiom.evaluation.frameworks.capability import (
    CapabilityDimension,
    CapabilitySnapshot,
    EvidenceState,
    derive_evidence_state,
    make_dimension_score,
    make_dimension_score_from_benchmark,
    rollup_evidence_tier,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.run_benchmarks import init_db
import axiom.services.api_gateway.routes.eval_api as eval_api


def test_derive_evidence_state_classification():
    assert derive_evidence_state(0) == EvidenceState.UNAVAILABLE
    assert derive_evidence_state(0, baseline=True) == EvidenceState.BASELINE
    assert derive_evidence_state(3, estimated=True) == EvidenceState.ESTIMATED
    assert derive_evidence_state(3, simulated=True) == EvidenceState.SIMULATED
    assert derive_evidence_state(3) == EvidenceState.MEASURED


def test_rollup_evidence_tier_weakest_wins():
    tier = rollup_evidence_tier(
        {
            "mathematical_reasoning": EvidenceState.MEASURED.value,
            "proof_verification": EvidenceState.SIMULATED.value,
        }
    )
    assert tier["aggregate"] == EvidenceState.SIMULATED.value
    assert tier["weakest_dimension"] == "proof_verification"


def test_capability_snapshot_includes_evidence_metadata():
    snapshot = CapabilitySnapshot(run_id="e4", timestamp="2026-08-08T00:00:00Z")
    snapshot.dimension_scores = [
        make_dimension_score_from_benchmark(
            CapabilityDimension.MATHEMATICAL_REASONING, 0.8, 5
        ),
        make_dimension_score_from_benchmark(
            CapabilityDimension.PROOF_VERIFICATION, 0.6, 4
        ),
    ]
    snapshot.compute_composite()
    payload = snapshot.to_dict()

    assert payload["evidence_tier"]["aggregate"] == EvidenceState.SIMULATED.value
    assert payload["limitations"]
    for dim in payload["dimensions"].values():
        assert "evidence_state" in dim
        assert "benchmark_count" in dim


def test_proof_verification_marked_simulated_when_benchmarked():
    score = make_dimension_score_from_benchmark(
        CapabilityDimension.PROOF_VERIFICATION, 0.5, 3
    )
    assert score.evidence_state == EvidenceState.SIMULATED
    assert score.benchmark_count == 3


def test_prize_readiness_includes_evidence_fields():
    engine = PrizeReadinessEngine()
    scores = engine.compute_all(
        {
            "mathematical_reasoning": 0.4,
            "proof_verification": 0.35,
            "literature_synthesis": 0.4,
            "counterexample_search": 0.35,
            "research_planning": 0.3,
        }
    )
    for item in scores:
        data = item.to_dict()
        assert "benchmark_count" in data
        assert "evidence_tier" in data
        assert "limitations" in data
        assert data["benchmark_count"] > 0
        assert data["evidence_tier"] in {s.value for s in EvidenceState}


@pytest.fixture
def temp_eval_db():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "test_s0_e4.db")
        init_db(db_file)
        old_db = settings.db_path
        settings.db_path = db_file
        try:
            yield db_file
        finally:
            settings.db_path = old_db


def test_eval_api_baseline_scores_include_evidence_state(temp_eval_db):
    scores = eval_api.get_capability_scores()
    for info in scores.values():
        assert info.get("evidence_state") == EvidenceState.BASELINE.value
        assert info.get("benchmark_count", 0) == 0


def test_eval_run_response_includes_evidence_gate_fields(temp_eval_db):
    response = eval_api.trigger_benchmark()
    assert "evidence_tier" in response
    assert "limitations" in response
    assert response["evidence_tier"]["aggregate"] in {s.value for s in EvidenceState}
    assert isinstance(response["limitations"], list)

    for readiness in response["readiness"]:
        assert "evidence_tier" in readiness
        assert "benchmark_count" in readiness
        assert "limitations" in readiness
