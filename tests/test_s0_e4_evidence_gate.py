"""S0-E4 EPIC-002 evidence integration gate tests."""

from __future__ import annotations

import os
import tempfile

import pytest

from axiom.evaluation.frameworks.evidence import (
    REQUIRED_SCORE_FIELDS,
    assert_gated_dimension,
    build_baseline_dimensions_dict,
)
from axiom.evaluation.run_benchmarks import init_db
from axiom.config import settings
import axiom.services.api_gateway.routes.eval_api as eval_api


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


def test_baseline_scores_are_evidence_gated():
    """Empty DB must return baseline scores with all S0-E4 fields."""
    baseline = build_baseline_dimensions_dict()
    assert len(baseline) == 8
    for dim_name, info in baseline.items():
        assert_gated_dimension(dim_name, info)
        assert info["evidence_state"] == "baseline"
        assert info["benchmark_count"] == 0
        assert info["estimated"] is True


def test_get_scores_empty_db_is_gated(temp_eval_db):
    scores = eval_api.get_capability_scores()
    assert len(scores) == 8
    for dim_name, info in scores.items():
        assert_gated_dimension(dim_name, info)


def test_post_run_scores_are_gated(temp_eval_db):
    response = eval_api.trigger_benchmark()
    for dim_name, info in response["dimensions"].items():
        assert_gated_dimension(dim_name, info)
        assert info["benchmark_count"] > 0

    pv = response["dimensions"]["proof_verification"]
    assert pv["evidence_state"] == "simulated"
    assert pv["estimated"] is True
    assert any("simulation" in lim.lower() for lim in pv["limitations"])


def test_prize_readiness_includes_limitations(temp_eval_db):
    readiness = eval_api.get_prize_readiness()
    assert len(readiness) == 6
    for item in readiness:
        assert "limitations" in item
        assert len(item["limitations"]) >= 1
        assert "evidence_state" in item


def test_required_fields_constant():
    assert "evidence_state" in REQUIRED_SCORE_FIELDS
    assert "benchmark_count" in REQUIRED_SCORE_FIELDS
    assert "limitations" in REQUIRED_SCORE_FIELDS
