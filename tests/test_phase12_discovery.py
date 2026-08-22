"""Tests for Phase 12 — Autonomous Mathematical Discovery & Formal Verification Engine."""
import pytest
from axiom.discovery.generator import ConjectureGenerator
from axiom.discovery.prover import AutomatedProver
from axiom.discovery.pipeline import DiscoveryPipeline
from axiom.discovery.models import FormulaType, ProofStatus


def test_conjecture_generator():
    gen = ConjectureGenerator()
    sum_cands = gen.generate_summation_candidates()
    ineq_cands = gen.generate_inequality_candidates()

    assert len(sum_cands) >= 5
    assert len(ineq_cands) >= 2
    assert all(c.formula_type == FormulaType.SUMMATION for c in sum_cands)
    assert all(c.formula_type == FormulaType.INEQUALITY for c in ineq_cands)


def test_automated_prover_summation():
    gen = ConjectureGenerator()
    prover = AutomatedProver()
    sum_cands = gen.generate_summation_candidates()

    # Test closed-form summation proof on k * 2^k
    cand = sum_cands[0]
    res = prover.prove_summation(cand, sample_depth=5)

    assert res.status == ProofStatus.PROVED
    assert res.closed_form is not None
    assert res.inductive_samples_checked == 5
    assert res.verification_time_ms > 0


def test_automated_prover_smt_inequality():
    gen = ConjectureGenerator()
    prover = AutomatedProver()
    ineq_cands = gen.generate_inequality_candidates()

    # Test x^3 + y^3 < (x + y)^3 for x,y > 0
    cand = ineq_cands[0]
    res = prover.verify_inequality_smt(cand)

    assert res.status == ProofStatus.PROVED
    assert "Z3 SMT" in res.proof_method
    assert res.counterexample is None


def test_discovery_pipeline():
    pipeline = DiscoveryPipeline()
    report = pipeline.run_discovery_cycle()

    assert report["total_candidates"] >= 7
    assert report["proved"] >= 7
    assert report["disproved"] == 0
    assert len(report["results"]) == report["total_candidates"]
