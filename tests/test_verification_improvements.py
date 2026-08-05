import pytest
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import ConceptNode, MathematicalClaimNode, EpistemicStatus, VerificationTier
from axiom.core.verification.smt_gateway import SmtGateway
from axiom.core.verification.lean_exporter import LeanExporter
from axiom.evaluation.prize_readiness import PrizeReadinessScorer

def test_smt_gateway_nonlinear_real_arithmetic():
    smt = SmtGateway()
    
    # 1. Valid NRA: x * y <= 10, when x in [1, 2] and y in [3, 4]
    # Max value of x*y is 8.0, so x*y <= 10.0 holds.
    is_valid, counterexample = smt.verify_real_inequality(
        lhs="x * y",
        rhs="10.0",
        variables=["x", "y"],
        bounds={"x": (1.0, 2.0), "y": (3.0, 4.0)}
    )
    assert is_valid is True
    assert counterexample is None

    # 2. Refuted NRA: x * y <= 5, same bounds.
    # E.g. x=2.0, y=3.0 => 6.0 > 5.0. Counterexample must be found.
    is_valid, counterexample = smt.verify_real_inequality(
        lhs="x * y",
        rhs="5.0",
        variables=["x", "y"],
        bounds={"x": (1.0, 2.0), "y": (3.0, 4.0)}
    )
    assert is_valid is False
    assert counterexample is not None
    assert "x" in counterexample
    assert "y" in counterexample
    assert counterexample["x"] * counterexample["y"] > 5.0

def test_smt_gateway_polynomial_identities():
    smt = SmtGateway()
    
    # 1. Valid binomial expansion: (x + y)^2 == x^2 + 2*x*y + y^2
    is_valid, counterexample = smt.verify_polynomial_identity(
        equation="(x + y)**2 == x**2 + 2*x*y + y**2",
        variables=["x", "y"]
    )
    assert is_valid is True
    assert counterexample is None
    
    # 2. Invalid expansion: (x + y)^2 == x^2 + y^2
    # E.g. x=1.0, y=1.0 => 4.0 != 2.0. Counterexample must be found.
    is_valid, counterexample = smt.verify_polynomial_identity(
        equation="(x + y)**2 == x**2 + y**2",
        variables=["x", "y"]
    )
    assert is_valid is False
    assert counterexample is not None
    assert "x" in counterexample
    assert "y" in counterexample
    assert (counterexample["x"] + counterexample["y"])**2 != counterexample["x"]**2 + counterexample["y"]**2

def test_lean_exporter_auto_tactic_generation():
    exporter = LeanExporter()
    
    # 1. Numerical goal: 2 + 2 = 4 (purely numeric, no vars in variables dict)
    tactic_num = exporter.auto_generate_tactic("2 + 2 = 4", {})
    assert tactic_num == "norm_num"
    
    # 2. Polynomial variable equality: x + y = y + x
    tactic_poly = exporter.auto_generate_tactic("x + y = y + x", {"x": "Int", "y": "Int"})
    assert tactic_poly == "ring"
    
    # 3. Reflexivity: x + 0 = x + 0
    tactic_rfl = exporter.auto_generate_tactic("x + 0 = x + 0", {"x": "Int"})
    assert tactic_rfl == "rfl"
    
    # 4. Inequality: x + 1 > x
    tactic_ineq = exporter.auto_generate_tactic("x + 1 > x", {"x": "Int"})
    assert tactic_ineq == "linarith"
    
    # 5. Fallback
    tactic_fallback = exporter.auto_generate_tactic("some_complex_relation(x)", {"x": "Int"})
    assert tactic_fallback == "sorry"

def test_dynamic_prize_readiness_scorer():
    store = EpistemicStore(db_path=":memory:")
    scorer = PrizeReadinessScorer(store=store)
    
    # Get initial scores (without any EGS nodes)
    initial_scores = {prob.name: score for prob, score in scorer.score_all()}
    initial_riemann = initial_scores["Riemann Hypothesis"]
    
    # Seed the store with Riemann zeta function relevant concepts and papers
    store.add_node(ConceptNode(
        id="con-zeta",
        name="Riemann Zeta Function",
        definition="The analytic function defined by the Dirichlet series sum 1/n^s.",
        metadata={}
    ))
    
    # Retrieve updated scores
    updated_scores = {prob.name: score for prob, score in scorer.score_all()}
    updated_riemann = updated_scores["Riemann Hypothesis"]
    
    # Score should increase because "zeta" and "riemann" keywords match the node
    assert updated_riemann > initial_riemann
    
    # Add a verified theorem node with "critical line" and "zero"
    store.add_node(MathematicalClaimNode(
        id="thm-zeta-zeros",
        name="Zeta critical line zeros",
        statement="All non-trivial zeros lie on the critical line Re(s) = 1/2.",
        status=EpistemicStatus.VERIFIED,
        tier=VerificationTier.TIER_2_PROVEN,
        metadata={}
    ))
    
    further_scores = {prob.name: score for prob, score in scorer.score_all()}
    further_riemann = further_scores["Riemann Hypothesis"]
    
    assert further_riemann > updated_riemann
