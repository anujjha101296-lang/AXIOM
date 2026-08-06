"""Tests for Research Validation Program."""

from __future__ import annotations

import os
import tempfile

import pytest

from axiom.research_validation.dataset import dataset_stats, load_known_answer_dataset
from axiom.research_validation.engine import ResearchValidationEngine
from axiom.research_validation.models import ResearchRunConfig
from axiom.research_validation.reproducibility import config_hash
from axiom.research_validation.scoring import score_answer


@pytest.fixture
def temp_rvp_db():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "rvp_test.db")
        yield db


def test_dataset_has_hundreds_of_problems():
    stats = dataset_stats()
    assert stats["total"] >= 200


def test_hidden_answer_not_in_public_dict():
    dataset = load_known_answer_dataset()
    problem = next(iter(dataset.values()))
    public = problem.public_dict()
    assert "hidden_answer" not in public
    assert "answer_keywords" not in public


def test_validation_run_produces_capability_score(temp_rvp_db):
    engine = ResearchValidationEngine(temp_rvp_db)
    problems = engine.list_problems(stage=0, limit=3)
    config = ResearchRunConfig(stage=0, problem_ids=[p["id"] for p in problems])
    results = engine.run_validation(config)
    assert len(results) == 3
    for r in results:
        d = r.capability_score.to_dict()
        assert "composite" in d
        assert "problem_understanding" in d
        assert r.pipeline.research_report
        assert r.pipeline.reasoning_tree
        assert r.provenance["hidden_answer_accessed"] is False


def test_discovery_pipeline_artifacts(temp_rvp_db):
    engine = ResearchValidationEngine(temp_rvp_db)
    results = engine.run_stage_batch(stage=0, limit=2)
    p = results[0].pipeline.to_dict()
    assert "hypothesis_list" in p
    assert "rejected_hypotheses" in p
    assert "failed_attempts" in p
    assert "lessons_learned" in p
    assert "confidence_estimates" in p
    assert "future_work" in p


def test_reproducibility_config_hash():
    c1 = ResearchRunConfig(stage=1, problem_ids=["a", "b"], seed=42)
    c2 = ResearchRunConfig(stage=1, problem_ids=["a", "b"], seed=42)
    c3 = ResearchRunConfig(stage=1, problem_ids=["a", "b"], seed=43)
    assert config_hash(c1) == config_hash(c2)
    assert config_hash(c1) != config_hash(c3)


def test_score_answer_uses_keywords_only():
    dataset = load_known_answer_dataset()
    problem = dataset["ka_algebra_sum_n"]
    low = score_answer("unrelated text", problem)
    high = score_answer("The closed form is n(n+1)/2 and for n=100 we get 5050 via gauss arithmetic series", problem)
    assert high > low
