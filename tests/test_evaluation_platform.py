"""
Integration and regression test suite for AXIOM EPIC-002 Scientific Capability Evaluation Platform (SCEP).
Validates requirements R1-R6:
- R1: Scientific Capability Framework L0-L5 taxonomy, thresholds, and composite formula.
- R2: Benchmark suite execution time (< 2 min), 5 categories with >= 3 test cases each, score normalization [0,1].
- R3: Prize Readiness Engine for 6 Millennium Problems, confidence intervals, benchmark grounding.
- R4: Capability Delta Report Generator JSON/Markdown format and 100-point integer readiness scaling.
- R5: Evaluation REST API endpoints and SQLite database persistence.
- R6: Independent Audit document structure and findings.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import time
import types
import pytest

# Ensure environment shims for optional FastAPI/Pydantic packages
if "pydantic" not in sys.modules:
    try:
        import pydantic
    except ImportError:
        m_pydantic = types.ModuleType("pydantic")
        class DummyBaseModel:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
            def dict(self):
                return self.__dict__
        def Field(default=None, **kwargs):
            return default
        def field_validator(*args, **kwargs):
            def decorator(f):
                return f
            return decorator
        m_pydantic.BaseModel = DummyBaseModel
        m_pydantic.Field = Field
        m_pydantic.field_validator = field_validator
        sys.modules["pydantic"] = m_pydantic

if "pydantic_settings" not in sys.modules:
    try:
        import pydantic_settings
    except ImportError:
        m_ps = types.ModuleType("pydantic_settings")
        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in self.__class__.__dict__.items():
                    if not k.startswith("_") and not callable(v):
                        setattr(self, k, v)
                for k, v in kwargs.items():
                    setattr(self, k, v)
        def SettingsConfigDict(**kwargs):
            return kwargs
        m_ps.BaseSettings = BaseSettings
        m_ps.SettingsConfigDict = SettingsConfigDict
        sys.modules["pydantic_settings"] = m_ps

if "fastapi" not in sys.modules:
    try:
        import fastapi
    except ImportError:
        m_fastapi = types.ModuleType("fastapi")
        class DummyRouter:
            def __init__(self, **kwargs):
                self.routes = {}
            def get(self, path, **kwargs):
                def decorator(func):
                    self.routes[("GET", path)] = func
                    return func
                return decorator
            def post(self, path, **kwargs):
                def decorator(func):
                    self.routes[("POST", path)] = func
                    return func
                return decorator
        class DummyHTTPException(Exception):
            def __init__(self, status_code, detail=None):
                self.status_code = status_code
                self.detail = detail
        m_fastapi.APIRouter = DummyRouter
        m_fastapi.HTTPException = DummyHTTPException
        m_fastapi.BackgroundTasks = object
        sys.modules["fastapi"] = m_fastapi

from axiom.evaluation.frameworks.capability import (
    CapabilityDimension,
    CapabilitySnapshot,
    DimensionScore,
    DIMENSION_WEIGHTS,
    LEVEL_NAMES,
    LEVEL_THRESHOLDS,
    classify_level,
    make_dimension_score,
)
from axiom.evaluation.frameworks.prize_readiness import (
    PrizeReadinessEngine,
    PrizeReadinessScore,
)
from axiom.evaluation.reporting.delta_report import (
    CapabilityDeltaReport,
    generate_delta_report,
)
from axiom.evaluation.benchmarks.suite import (
    run_math_reasoning_benchmarks,
    run_proof_verification_benchmarks,
    run_conjecture_benchmarks,
    run_knowledge_quality_benchmarks,
    run_counterexample_benchmarks,
    run_research_planning_benchmarks,
    run_literature_synthesis_benchmarks,
    run_research_productivity_benchmarks,
    REQUIRED_CATEGORIES_MAP,
)
from axiom.evaluation.run_benchmarks import init_db, save_run, get_latest_run


# ══════════════════════════════════════════════════════════════════════════════
# R1: Scientific Capability Framework (SCF)
# ══════════════════════════════════════════════════════════════════════════════

def test_r1_scf_level_classification_and_taxonomy():
    """Verify 8 capability dimensions, L0-L5 level names, and threshold boundaries."""
    # 8 dimensions
    all_dims = list(CapabilityDimension)
    assert len(all_dims) == 8
    
    # LEVEL_NAMES L0-L5
    assert len(LEVEL_NAMES) == 6
    assert LEVEL_NAMES[0] == "L0: None"
    assert LEVEL_NAMES[1] == "L1: Basic"
    assert LEVEL_NAMES[2] == "L2: Undergraduate"
    assert LEVEL_NAMES[3] == "L3: Graduate"
    assert LEVEL_NAMES[4] == "L4: Research-Adjacent"
    assert LEVEL_NAMES[5] == "L5: Research-Active"

    # Test exact threshold boundaries for every dimension
    for dim in CapabilityDimension:
        thresholds = LEVEL_THRESHOLDS[dim]
        assert len(thresholds) == 5, f"Expected 5 thresholds for {dim}"
        
        # Test L0
        assert classify_level(0.0, dim) == 0
        assert classify_level(thresholds[0] - 0.001, dim) == 0
        
        # Test L1
        assert classify_level(thresholds[0], dim) == 1
        assert classify_level(thresholds[1] - 0.001, dim) == 1
        
        # Test L2
        assert classify_level(thresholds[1], dim) == 2
        
        # Test L3
        assert classify_level(thresholds[2], dim) == 3
        
        # Test L4
        assert classify_level(thresholds[3], dim) == 4
        
        # Test L5
        assert classify_level(thresholds[4], dim) == 5
        assert classify_level(1.0, dim) == 5


def test_r1_scf_composite_score_formula():
    """Verify weighted average computation S_composite = Σ (w_d * S_d) and weights sum."""
    # Verify dimension weights sum to 1.0
    weight_sum = sum(DIMENSION_WEIGHTS.values())
    assert abs(weight_sum - 1.0) < 1e-6

    snapshot = CapabilitySnapshot(run_id="r1_test", timestamp="2026-08-06T00:00:00Z")
    
    # Assign known scores to test exact weighted sum
    scores_dict = {
        CapabilityDimension.MATHEMATICAL_REASONING: 1.0, # w=0.20 -> 0.20
        CapabilityDimension.PROOF_VERIFICATION: 0.5,     # w=0.18 -> 0.09
        CapabilityDimension.CONJECTURE_GENERATION: 0.0, # w=0.15 -> 0.00
        CapabilityDimension.KNOWLEDGE_QUALITY: 0.0,     # w=0.12 -> 0.00
        CapabilityDimension.COUNTEREXAMPLE_SEARCH: 0.0, # w=0.12 -> 0.00
        CapabilityDimension.RESEARCH_PLANNING: 0.0,     # w=0.10 -> 0.00
        CapabilityDimension.LITERATURE_SYNTHESIS: 0.0, # w=0.08 -> 0.00
        CapabilityDimension.RESEARCH_PRODUCTIVITY: 0.0, # w=0.05 -> 0.00
    }
    
    snapshot.dimension_scores = [
        make_dimension_score(dim, val, benchmark_count=5)
        for dim, val in scores_dict.items()
    ]
    
    composite = snapshot.compute_composite()
    # Expected: 1.0 * 0.20 + 0.5 * 0.18 = 0.29
    assert abs(composite - 0.29) < 1e-4
    assert snapshot.estimated_dimensions == []


# ══════════════════════════════════════════════════════════════════════════════
# R2: Benchmark Suite Execution & Normalization
# ══════════════════════════════════════════════════════════════════════════════

def test_r2_benchmark_suite_execution_and_normalization():
    """Verify benchmark execution time (< 2 min), 5 categories with >= 3 test cases each, scores in [0,1]."""
    start_time = time.time()
    
    # Execute all 8 benchmark categories
    mr_res, mr_score = run_math_reasoning_benchmarks()
    pv_res, pv_score = run_proof_verification_benchmarks()
    cg_res, cg_score = run_conjecture_benchmarks()
    kq_res, kq_score = run_knowledge_quality_benchmarks()
    ce_res, ce_score = run_counterexample_benchmarks()
    rp_res, rp_score = run_research_planning_benchmarks()
    ls_res, ls_score = run_literature_synthesis_benchmarks()
    rd_res, rd_score = run_research_productivity_benchmarks()

    elapsed = time.time() - start_time
    assert elapsed < 120.0, f"Benchmark execution took too long: {elapsed:.2f}s"

    suites = [
        ("Mathematical Reasoning", mr_res, mr_score),
        ("Proof Verification", pv_res, pv_score),
        ("Conjecture Generation", cg_res, cg_score),
        ("Knowledge Quality", kq_res, kq_score),
        ("Counterexample Search", ce_res, ce_score),
        ("Research Planning", rp_res, rp_score),
        ("Literature Synthesis", ls_res, ls_score),
        ("Research Productivity", rd_res, rd_score),
    ]

    # At least 5 categories
    assert len(suites) >= 5

    # Each category has >= 3 test cases and score in [0, 1]
    for name, res, score in suites:
        assert len(res) >= 3, f"{name} has fewer than 3 test cases: {len(res)}"
        assert 0.0 <= score <= 1.0, f"{name} aggregate score {score} outside [0, 1]"
        for case in res:
            assert 0.0 <= case.score <= 1.0, f"Case {case.case_id} score {case.score} outside [0, 1]"
            assert case.time_ms >= 0.0

    # Check mapping of the 5 required categories
    required_cats = [
        "algebra/calculus",
        "theorem reproduction",
        "proof verification",
        "conjecture novelty",
        "open problem decomposition",
    ]
    for cat in required_cats:
        assert cat in REQUIRED_CATEGORIES_MAP
        assert len(REQUIRED_CATEGORIES_MAP[cat]) >= 3


# ══════════════════════════════════════════════════════════════════════════════
# R3: Prize Readiness Engine
# ══════════════════════════════════════════════════════════════════════════════

def test_r3_prize_readiness_engine_6_problems():
    """Verify Prize Readiness Engine for all 6 Clay Millennium Problems."""
    engine = PrizeReadinessEngine()
    
    sample_scores = {d.value: 0.65 for d in CapabilityDimension}
    readiness_list = engine.compute_all(sample_scores)
    
    assert len(readiness_list) == 6
    
    expected_ids = {
        "riemann_hypothesis",
        "p_vs_np",
        "yang_mills",
        "birch_swinnerton_dyer",
        "navier_stokes",
        "hodge_conjecture",
    }
    actual_ids = {r.problem_id for r in readiness_list}
    assert actual_ids == expected_ids
    
    for r in readiness_list:
        assert 0.0 <= r.score <= 1.0
        ci_low, ci_high = r.confidence_interval
        assert 0.0 <= ci_low <= r.score <= ci_high <= 1.0
        assert len(r.prerequisites) > 0
        assert len(r.milestones_achieved) > 0
        assert len(r.capability_gaps) > 0


def test_r3_prize_readiness_benchmark_grounding():
    """Verify evidence grounding — changing benchmark scores directly alters readiness score."""
    engine = PrizeReadinessEngine()

    low_scores = {d.value: 0.10 for d in CapabilityDimension}
    high_scores = {d.value: 0.90 for d in CapabilityDimension}

    low_readiness = engine.compute_all(low_scores)
    high_readiness = engine.compute_all(high_scores)

    low_map = {r.problem_id: r.score for r in low_readiness}
    high_map = {r.problem_id: r.score for r in high_readiness}

    for pid in low_map:
        assert high_map[pid] > low_map[pid], f"Readiness for {pid} failed to increase with higher benchmark scores"


# ══════════════════════════════════════════════════════════════════════════════
# R4: Capability Delta Report Generator & Integer Scaling
# ══════════════════════════════════════════════════════════════════════════════

def test_r4_capability_delta_report_formatting_and_scaling():
    """Verify JSON/Markdown format and 100-point integer readiness scaling in report."""
    curr_snapshot = CapabilitySnapshot(run_id="run_curr", timestamp="2026-08-06T12:00:00Z")
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

    engine = PrizeReadinessEngine()
    readiness = engine.compute_all({s.dimension.value: s.raw_score for s in curr_snapshot.dimension_scores})

    prev_snapshot = {
        "run_id": "run_prev",
        "timestamp": "2026-08-05T12:00:00Z",
        "composite_score": 0.50,
        "dimensions": {
            "mathematical_reasoning": {"score": 0.70},
            "proof_verification": {"score": 0.60},
            "conjecture_generation": {"score": 0.50},
            "knowledge_quality": {"score": 0.50},
            "counterexample_search": {"score": 0.40},
            "research_planning": {"score": 0.40},
            "literature_synthesis": {"score": 0.40},
            "research_productivity": {"score": 0.40},
        }
    }

    prev_readiness = [
        {"problem_id": "riemann_hypothesis", "score": 0.31},
        {"problem_id": "p_vs_np", "score": 0.28},
        {"problem_id": "navier_stokes", "score": 0.26},
        {"problem_id": "birch_swinnerton_dyer", "score": 0.20},
        {"problem_id": "yang_mills", "score": 0.20},
        {"problem_id": "hodge_conjecture", "score": 0.18},
    ]

    report = generate_delta_report(
        epic_name="EPIC-002",
        prev_snapshot=prev_snapshot,
        curr_snapshot=curr_snapshot,
        prev_readiness=prev_readiness,
        curr_readiness=readiness,
    )

    # Test dictionary export
    r_dict = report.to_dict()
    assert r_dict["epic_name"] == "EPIC-002"
    assert r_dict["previous_run_id"] == "run_prev"
    assert r_dict["current_run_id"] == "run_curr"
    assert len(r_dict["readiness_deltas"]) == 6

    # Test 100-point integer readiness point conversion
    for r_delta in r_dict["readiness_deltas"]:
        assert isinstance(r_delta["prev_points"], int)
        assert isinstance(r_delta["curr_points"], int)

    # Test Markdown formatting matches exact structure
    md = report.to_markdown()
    assert "EPIC-002 COMPLETE" in md
    assert "Capability Delta" in md
    assert "Prize Readiness" in md
    assert "Riemann" in md
    assert "Weakest Capability" in md
    assert "Highest Priority" in md
    assert "Recommended Next Epic" in md


# ══════════════════════════════════════════════════════════════════════════════
# R5: Evaluation REST API & Database Persistence
# ══════════════════════════════════════════════════════════════════════════════

def test_r5_eval_api_functions():
    """Verify REST API backend functions (/eval/scores, /eval/run, /eval/history, /eval/prize-readiness)."""
    import axiom.services.api_gateway.routes.eval_api as eval_api
    from axiom.config import settings

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "eval_api_test.db")
        init_db(db_file)
        old_db = settings.db_path
        settings.db_path = db_file
        try:
            # 1. GET /eval/scores
            scores = eval_api.get_capability_scores()
            assert len(scores) == 8
            assert "mathematical_reasoning" in scores

            # 2. POST /eval/run
            run_resp = eval_api.trigger_benchmark()
            assert "run_id" in run_resp
            assert "composite_score" in run_resp
            assert len(run_resp["dimensions"]) == 8

            # 3. GET /eval/history
            history = eval_api.get_run_history()
            assert len(history) >= 1
            assert history[0]["run_id"] == run_resp["run_id"]

            # 4. GET /eval/prize-readiness
            readiness = eval_api.get_prize_readiness()
            assert len(readiness) == 6

        finally:
            settings.db_path = old_db


def test_r5_database_persistence_and_queries():
    """Verify SQLite persistence for eval_runs and eval_readiness tables."""
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        init_db(temp_db)

        snapshot = CapabilitySnapshot(run_id="db_run_1", timestamp="2026-08-06T15:00:00Z")
        snapshot.dimension_scores = [
            make_dimension_score(d, 0.70, 5) for d in CapabilityDimension
        ]
        snapshot.compute_composite()

        engine = PrizeReadinessEngine()
        readiness = engine.compute_all({d.value: 0.70 for d in CapabilityDimension})

        save_run(temp_db, snapshot, readiness)

        retrieved_run, retrieved_readiness = get_latest_run(temp_db)
        assert retrieved_run is not None
        assert retrieved_run["run_id"] == "db_run_1"
        assert len(retrieved_readiness) == 6

    finally:
        if os.path.exists(temp_db):
            os.unlink(temp_db)


# ══════════════════════════════════════════════════════════════════════════════
# R6: Independent Audit Document Structure & Findings
# ══════════════════════════════════════════════════════════════════════════════

def test_r6_audit_document_structure_and_findings():
    """Verify docs/audit/EPIC_002_audit.md exists and contains required findings and verdicts."""
    audit_file = "docs/audit/EPIC_002_audit.md"
    assert os.path.exists(audit_file), f"Audit document missing at {audit_file}"

    with open(audit_file, "r") as f:
        content = f.read()

    # Executive Summary & Departments
    assert "Independent Audit & Chief Skeptic Report" in content
    assert "Department I (Independent Audit)" in content
    assert "Department J (Chief Skeptic)" in content

    # Findings
    assert "Finding 1" in content or "Optimistic Assumptions" in content
    assert "Finding 2" in content or "Lack of Live Compilation" in content
    assert "Finding 3" in content or "Vulnerability to Benchmark Gaming" in content
    assert "Finding 4" in content or "Empty DB Baseline" in content

    # Risk Levels
    assert "HIGH" in content
    assert "CRITICAL" in content
    assert "MEDIUM" in content
    assert "LOW" in content

    # Prize Readiness Grounding Table for 6 Millennium Problems
    assert "Riemann Hypothesis" in content
    assert "P vs NP" in content
    assert "Navier" in content
    assert "Birch" in content
    assert "Yang" in content
    assert "Hodge" in content

    # Recommendations for EPIC-003
    assert "Skeptic's Recommendations for EPIC-003" in content or "EPIC-003" in content
