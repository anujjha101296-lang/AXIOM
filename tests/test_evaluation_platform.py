"""
Integration and regression test suite for AXIOM EPIC-002 Scientific Capability Evaluation Platform.
Validates capability snapshot math, level classification, prize readiness computation, and delta reports.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
import pytest

from axiom.evaluation.frameworks.capability import (
    CapabilityDimension,
    classify_level,
    make_dimension_score,
    CapabilitySnapshot,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report
from axiom.evaluation.run_benchmarks import init_db, save_run


def test_level_classification():
    """Verify that dimension scores are classified into the correct levels."""
    # MR thresholds: [0.40, 0.55, 0.70, 0.82, 0.95]
    assert classify_level(0.39, CapabilityDimension.MATHEMATICAL_REASONING) == 0
    assert classify_level(0.40, CapabilityDimension.MATHEMATICAL_REASONING) == 1
    assert classify_level(0.65, CapabilityDimension.MATHEMATICAL_REASONING) == 2
    assert classify_level(0.70, CapabilityDimension.MATHEMATICAL_REASONING) == 3
    assert classify_level(0.96, CapabilityDimension.MATHEMATICAL_REASONING) == 5


def test_composite_score_computation():
    """Verify weighted average computation for S_composite."""
    snapshot = CapabilitySnapshot(run_id="test_run", timestamp="2026-08-06T00:00:00Z")
    snapshot.dimension_scores = [
        make_dimension_score(CapabilityDimension.MATHEMATICAL_REASONING, 1.0, 1),  # weight 0.20
        make_dimension_score(CapabilityDimension.PROOF_VERIFICATION, 0.5, 1),     # weight 0.18 -> 0.09
        make_dimension_score(CapabilityDimension.CONJECTURE_GENERATION, 0.0, 1), # weight 0.15 -> 0.0
        make_dimension_score(CapabilityDimension.KNOWLEDGE_QUALITY, 0.0, 1),     # weight 0.12 -> 0.0
        make_dimension_score(CapabilityDimension.COUNTEREXAMPLE_SEARCH, 0.0, 1), # weight 0.12 -> 0.0
        make_dimension_score(CapabilityDimension.RESEARCH_PLANNING, 0.0, 1),     # weight 0.10 -> 0.0
        make_dimension_score(CapabilityDimension.LITERATURE_SYNTHESIS, 0.0, 1), # weight 0.08 -> 0.0
        make_dimension_score(CapabilityDimension.RESEARCH_PRODUCTIVITY, 0.0, 1), # weight 0.05 -> 0.0
    ]
    comp = snapshot.compute_composite()
    # Expected: 1.0 * 0.20 + 0.5 * 0.18 = 0.29
    assert abs(comp - 0.29) < 0.0001
    assert snapshot.estimated_dimensions == []


def test_prize_readiness_grounding():
    """Verify that prize readiness scores correlate directly with benchmark scores."""
    engine = PrizeReadinessEngine()
    
    # Low benchmark scores
    low_scores = {d.value: 0.10 for d in CapabilityDimension}
    low_readiness = engine.compute_all(low_scores)
    rh_low = next(r for r in low_readiness if r.problem_id == "riemann_hypothesis")
    
    # High benchmark scores
    high_scores = {d.value: 0.90 for d in CapabilityDimension}
    high_readiness = engine.compute_all(high_scores)
    rh_high = next(r for r in high_readiness if r.problem_id == "riemann_hypothesis")
    
    assert rh_high.score > rh_low.score
    assert rh_low.score < 0.20
    assert rh_high.score > 0.60


def test_delta_report_markdown():
    """Verify that delta report format meets strict user specs."""
    curr_snapshot = CapabilitySnapshot(run_id="curr", timestamp="2026-08-06T00:00:00Z")
    curr_snapshot.dimension_scores = [
        make_dimension_score(CapabilityDimension.MATHEMATICAL_REASONING, 0.80, 10),
        make_dimension_score(CapabilityDimension.PROOF_VERIFICATION, 0.70, 7),
        make_dimension_score(CapabilityDimension.CONJECTURE_GENERATION, 0.60, 5),
        make_dimension_score(CapabilityDimension.KNOWLEDGE_QUALITY, 0.50, 5),
        make_dimension_score(CapabilityDimension.COUNTEREXAMPLE_SEARCH, 0.40, 5),
        make_dimension_score(CapabilityDimension.RESEARCH_PLANNING, 0.40, 5),
        make_dimension_score(CapabilityDimension.LITERATURE_SYNTHESIS, 0.40, 10),
        make_dimension_score(CapabilityDimension.RESEARCH_PRODUCTIVITY, 0.40, 3),
    ]
    curr_snapshot.compute_composite()
    
    scores_map = {s.dimension.value: s.raw_score for s in curr_snapshot.dimension_scores}
    engine = PrizeReadinessEngine()
    readiness = engine.compute_all(scores_map)
    
    # Without previous run (baseline mode)
    report = generate_delta_report(
        epic_name="EPIC-002",
        prev_snapshot=None,
        curr_snapshot=curr_snapshot,
        prev_readiness=None,
        curr_readiness=readiness
    )
    
    md = report.to_markdown()
    assert "EPIC-002 COMPLETE" in md
    assert "Capability Delta" in md
    assert "Mathematical Reasoning" in md
    assert "Prize Readiness" in md
    assert "Riemann" in md
    assert "Weakest Capability" in md
    assert "Highest Priority" in md


def test_database_persistence():
    """Verify that runs and readiness scores save correctly to SQLite database."""
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        init_db(temp_db)
        
        snapshot = CapabilitySnapshot(run_id="r123", timestamp="2026-08-06")
        snapshot.dimension_scores = [
            make_dimension_score(CapabilityDimension.MATHEMATICAL_REASONING, 0.75, 10),
            make_dimension_score(CapabilityDimension.PROOF_VERIFICATION, 0.60, 5),
            make_dimension_score(CapabilityDimension.CONJECTURE_GENERATION, 0.50, 5),
            make_dimension_score(CapabilityDimension.KNOWLEDGE_QUALITY, 0.50, 5),
            make_dimension_score(CapabilityDimension.COUNTEREXAMPLE_SEARCH, 0.40, 5),
            make_dimension_score(CapabilityDimension.RESEARCH_PLANNING, 0.40, 5),
            make_dimension_score(CapabilityDimension.LITERATURE_SYNTHESIS, 0.40, 10),
            make_dimension_score(CapabilityDimension.RESEARCH_PRODUCTIVITY, 0.40, 3),
        ]
        snapshot.compute_composite()
        
        engine = PrizeReadinessEngine()
        readiness = engine.compute_all({s.dimension.value: s.raw_score for s in snapshot.dimension_scores})
        
        save_run(temp_db, snapshot, readiness)
        
        # Query and assert
        conn = sqlite3.connect(temp_db)
        run_row = conn.execute("SELECT run_id, composite_score FROM eval_runs").fetchone()
        readiness_count = conn.execute("SELECT COUNT(*) FROM eval_readiness").fetchone()[0]
        conn.close()
        
        assert run_row is not None
        assert run_row[0] == "r123"
        assert readiness_count == 6
        
    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)
