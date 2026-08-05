#!/usr/bin/env python3
"""
AXIOM MIP Validation Script
Tests pure-Python modules that work without pydantic/z3 dependencies.
Run: python3 tests/mip/validate_mip.py
"""
import sys
import os
import sqlite3
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PASSED = []
FAILED = []


def test(name):
    """Decorator for test functions."""
    def decorator(fn):
        try:
            fn()
            PASSED.append(name)
            print(f"  ✓ {name}")
        except Exception as exc:
            FAILED.append((name, str(exc)))
            print(f"  ✗ {name}: {exc}")
        return fn
    return decorator


print("\n══════════════════════════════════════════════════════════════")
print("  AXIOM MIP — EPIC-001 Validation Suite")
print("══════════════════════════════════════════════════════════════")
print()

# ─────────────────────────────────────────────────────────────
print("Dept A: Mathematical Ontology")
# ─────────────────────────────────────────────────────────────

@test("ObjectType has 15 types")
def _():
    from axiom.mip.knowledge.ontology import MathObjectType
    assert len(list(MathObjectType)) == 15

@test("EdgeType has 11 types")
def _():
    from axiom.mip.knowledge.ontology import MathEdgeType
    assert len(list(MathEdgeType)) == 11

@test("Domain classification — Riemann → number_theory")
def _():
    from axiom.mip.knowledge.ontology import classify_domain, MathDomain
    assert classify_domain("Riemann zeta function zeros") == MathDomain.NUMBER_THEORY

@test("Domain classification — group ring field → algebra")
def _():
    from axiom.mip.knowledge.ontology import classify_domain, MathDomain
    assert classify_domain("For all groups G the ring homomorphism") == MathDomain.ALGEBRA

@test("Domain classification — continuous function → analysis")
def _():
    from axiom.mip.knowledge.ontology import classify_domain, MathDomain
    assert classify_domain("every continuous measurable function") == MathDomain.ANALYSIS

@test("Unknown domain for nonsense text")
def _():
    from axiom.mip.knowledge.ontology import classify_domain, MathDomain
    assert classify_domain("xyzabc12345") == MathDomain.UNKNOWN

@test("All domains have non-empty keyword lists")
def _():
    from axiom.mip.knowledge.ontology import DOMAIN_KEYWORDS
    assert len(DOMAIN_KEYWORDS) > 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        assert len(kws) > 0

print()
# ─────────────────────────────────────────────────────────────
print("Dept A: SQLite v5 Migration")
# ─────────────────────────────────────────────────────────────

_db = tempfile.mktemp(suffix=".db")

@test("Migration runs without error")
def _():
    from axiom.mip.knowledge.migrations import run_v5_migration
    run_v5_migration(_db)

@test("check_v5_applied returns True after migration")
def _():
    from axiom.mip.knowledge.migrations import check_v5_applied
    assert check_v5_applied(_db) is True

@test("mip_objects table exists")
def _():
    conn = sqlite3.connect(_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mip_objects'").fetchone()
    conn.close()
    assert row is not None

@test("mip_edges table exists")
def _():
    conn = sqlite3.connect(_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mip_edges'").fetchone()
    conn.close()
    assert row is not None

@test("mip_conjectures table exists")
def _():
    conn = sqlite3.connect(_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mip_conjectures'").fetchone()
    conn.close()
    assert row is not None

@test("mip_memory_snapshots table exists")
def _():
    conn = sqlite3.connect(_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mip_memory_snapshots'").fetchone()
    conn.close()
    assert row is not None

@test("mip_proof_attempts table exists")
def _():
    conn = sqlite3.connect(_db)
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mip_proof_attempts'").fetchone()
    conn.close()
    assert row is not None

@test("At least 10 domains seeded")
def _():
    conn = sqlite3.connect(_db)
    count = conn.execute("SELECT COUNT(*) FROM mip_domains").fetchone()[0]
    conn.close()
    assert count >= 10, f"Got {count}"

@test("Migration is idempotent (runs twice safely)")
def _():
    from axiom.mip.knowledge.migrations import run_v5_migration
    run_v5_migration(_db)  # Run again

os.unlink(_db)

print()
# ─────────────────────────────────────────────────────────────
print("Dept F: Millennium Problem Decomposition Trees")
# ─────────────────────────────────────────────────────────────

@test("All 6 Millennium Problems exist")
def _():
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    expected = {"riemann_hypothesis", "p_vs_np", "yang_mills",
                "birch_swinnerton_dyer", "navier_stokes", "hodge_conjecture"}
    assert set(MILLENNIUM_TREES.keys()) == expected

@test("Riemann Hypothesis has ≥4 child lemmas")
def _():
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    rh = MILLENNIUM_TREES["riemann_hypothesis"]
    assert len(rh.children) >= 4

@test("P(L) formula: P(L) = (impact × feasibility) / cost")
def _():
    from axiom.mip.strategy.millennium_trees import Lemma
    l = Lemma(id="t", name="t", description="t", domain="a",
              estimated_impact=0.8, feasibility=0.5, estimated_cost=0.4)
    expected = round((0.8 * 0.5) / 0.4, 4)
    assert l.priority_index == expected, f"{l.priority_index} != {expected}"

@test("Zero cost returns 0 priority (no divide by zero)")
def _():
    from axiom.mip.strategy.millennium_trees import Lemma
    l = Lemma(id="t", name="t", description="t", domain="a",
              estimated_impact=1.0, feasibility=1.0, estimated_cost=0.0)
    assert l.priority_index == 0.0

@test("Prioritized queue for RH has ≥5 lemmas")
def _():
    from axiom.mip.strategy.millennium_trees import get_prioritized_queue
    q = get_prioritized_queue("riemann_hypothesis")
    assert len(q) >= 5, f"Got {len(q)}"

@test("Prioritized queue is sorted descending by P(L)")
def _():
    from axiom.mip.strategy.millennium_trees import get_prioritized_queue
    q = get_prioritized_queue("riemann_hypothesis")
    scores = [item["priority_index"] for item in q]
    assert scores == sorted(scores, reverse=True)

@test("Computational verification lemma has high feasibility (≥0.8)")
def _():
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    rh = MILLENNIUM_TREES["riemann_hypothesis"]
    comp = next((c for c in rh.children if c.id == "rh_computational_verification"), None)
    assert comp is not None
    assert comp.feasibility >= 0.8

@test("All 6 problems have non-empty decomposition queues")
def _():
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES, get_prioritized_queue
    for pid in MILLENNIUM_TREES:
        q = get_prioritized_queue(pid)
        assert len(q) >= 2, f"{pid} has only {len(q)} lemmas"

@test("Tree to_dict returns required keys")
def _():
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    d = MILLENNIUM_TREES["p_vs_np"].to_dict()
    for key in ["id", "name", "domain", "priority_index", "children"]:
        assert key in d

print()
# ─────────────────────────────────────────────────────────────
print("Dept G: Mathematical Memory")
# ─────────────────────────────────────────────────────────────

@test("Record and retrieve failed tactics")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory
    m = EpisodicMemory()
    m.record_failed_tactic("t1", "ring")
    m.record_failed_tactic("t1", "simp")
    f = m.get_failed_tactics("t1")
    assert "ring" in f and "simp" in f

@test("No duplicate failed tactics recorded")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory
    m = EpisodicMemory()
    m.record_failed_tactic("t1", "ring")
    m.record_failed_tactic("t1", "ring")
    assert m.get_failed_tactics("t1").count("ring") == 1

@test("Clear resets all memory")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory
    m = EpisodicMemory()
    old_sid = m.session_id
    m.record_failed_tactic("t1", "ring")
    m.add_hypothesis("∀ n, n² ≥ 0")
    m.clear()
    assert m.session_id != old_sid
    assert m.get_failed_tactics("t1") == []
    assert m.active_hypotheses == []

@test("to_dict contains required keys")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory
    m = EpisodicMemory()
    d = m.to_dict()
    for k in ["session_id", "active_hypotheses", "failed_tactics_summary"]:
        assert k in d

@test("FailureGuard filters known-failed tactics")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory, FailureGuard
    m = EpisodicMemory()
    m.record_failed_tactic("t1", "ring")
    m.record_failed_tactic("t1", "simp")
    guard = FailureGuard(m)
    filtered = guard.filter_tactics("t1", ["ring", "simp", "linarith", "norm_num"])
    assert "ring" not in filtered
    assert "simp" not in filtered
    assert "linarith" in filtered

@test("FailureGuard allows all tactics for unknown theorem")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory, FailureGuard
    m = EpisodicMemory()
    guard = FailureGuard(m)
    tactics = ["ring", "simp", "linarith"]
    assert guard.filter_tactics("unknown_theorem", tactics) == tactics

@test("SemanticMemory save and retrieve failed tactics")
def _():
    from axiom.mip.memory.episodic import EpisodicMemory, SemanticMemory
    db = tempfile.mktemp(suffix=".db")
    from axiom.mip.knowledge.migrations import run_v5_migration
    run_v5_migration(db)
    m = EpisodicMemory()
    m.problem_id = "riemann_hypothesis"
    m.record_failed_tactic("rh_lemma_1", "ring")
    sem = SemanticMemory(db_path=db)
    snap_id = sem.save_snapshot(m)
    assert snap_id is not None
    failed = sem.get_all_failed_tactics("rh_lemma_1")
    assert "ring" in failed
    os.unlink(db)

print()
# ─────────────────────────────────────────────────────────────
print("Dept B: Formal Mathematics (no compiler required)")
# ─────────────────────────────────────────────────────────────

@test("Lean4 fallback simulation — valid script passes")
def _():
    from axiom.mip.formal.lean4 import _simulate_lean4_check
    script = "import Mathlib\ntheorem foo : 1 = 1 := by ring\n"
    ok, out = _simulate_lean4_check(script)
    assert ok is True

@test("Lean4 fallback simulation — missing theorem fails")
def _():
    from axiom.mip.formal.lean4 import _simulate_lean4_check
    ok, out = _simulate_lean4_check("-- just a comment")
    assert ok is False

@test("Lean4 tactic suggestion — ring for equality")
def _():
    from axiom.mip.formal.lean4 import suggest_tactics
    t = suggest_tactics("a + b = b + a")
    assert "ring" in t

@test("Lean4 tactic suggestion — linarith for inequality")
def _():
    from axiom.mip.formal.lean4 import suggest_tactics
    t = suggest_tactics("if a ≤ b and b ≤ c then a ≤ c")
    assert "linarith" in t

@test("Lean4 MATHLIB_TACTICS has ≥20 entries")
def _():
    from axiom.mip.formal.lean4 import MATHLIB_TACTICS
    assert len(MATHLIB_TACTICS) >= 20

@test("Coq fallback simulation — valid script passes")
def _():
    from axiom.mip.formal.coq import _simulate_coq_check
    ok, _ = _simulate_coq_check("Theorem t : True. Proof. exact I. Qed.")
    assert ok is True

@test("Isabelle fallback simulation — valid script passes")
def _():
    from axiom.mip.formal.isabelle import _simulate_isabelle_check
    script = "theory T imports Main begin theorem t: shows \"True\" proof - show ?thesis by simp qed end"
    ok, _ = _simulate_isabelle_check(script)
    assert ok is True

print()
# ─────────────────────────────────────────────────────────────
print("Dept D: Conjecture Generator")
# ─────────────────────────────────────────────────────────────

@test("Tautology detection — x = x is tautology")
def _():
    from axiom.mip.conjecture.generator import _is_tautology
    assert _is_tautology("x = x") is True

@test("Tautology detection — non-trivial claim is not tautology")
def _():
    from axiom.mip.conjecture.generator import _is_tautology
    assert _is_tautology("∀ n : ℕ, n² ≥ 0") is False

@test("Novelty score is in [0.0, 1.0]")
def _():
    from axiom.mip.conjecture.generator import compute_novelty_score
    score = compute_novelty_score("∀ n : ℕ, n² ≥ n for large n", ["∀ a b, a + b = b + a"])
    assert 0.0 <= score <= 1.0

@test("DUAL strategy produces a result for ∀ quantifier")
def _():
    from axiom.mip.conjecture.generator import _strategy_dual
    result = _strategy_dual("∀ x : ℕ, x ≥ 0", "nonneg")
    assert result is not None and "∃" in result

@test("BOUND strategy produces a result for inequality")
def _():
    from axiom.mip.conjecture.generator import _strategy_bound
    result = _strategy_bound("∀ n, n ≤ n²", "sq_bound")
    assert result is not None

@test("COMPOSE strategy produces a result for two statements")
def _():
    from axiom.mip.conjecture.generator import _strategy_compose
    result = _strategy_compose("a + b = b + a", "a * b = b * a", "add_comm", "mul_comm")
    assert result is not None and "composition" in result.lower()

@test("Generator produces ≥1 conjecture from bootstrap")
def _():
    from axiom.mip.conjecture.generator import ConjectureGenerator
    db = tempfile.mktemp(suffix=".db")
    from axiom.mip.knowledge.migrations import run_v5_migration
    run_v5_migration(db)
    gen = ConjectureGenerator(db_path=db, min_novelty=0.01)
    results = gen.generate(n_conjectures=3)
    os.unlink(db)
    assert len(results) >= 1

print()
# ─────────────────────────────────────────────────────────────
print("Dept H: Verification Consensus")
# ─────────────────────────────────────────────────────────────

@test("Verdict enum has 4 values")
def _():
    from axiom.mip.verification.consensus import Verdict
    assert len(list(Verdict)) == 4

@test("Sanity checker verifies known algebraic identity")
def _():
    from axiom.mip.verification.consensus import _run_syntactic_sanity, Verdict
    r = _run_syntactic_sanity("a + b = b + a")
    assert r.verdict == Verdict.VERIFIED

@test("Sanity checker rejects single character claim")
def _():
    from axiom.mip.verification.consensus import _run_syntactic_sanity, Verdict
    r = _run_syntactic_sanity("a")
    assert r.verdict != Verdict.VERIFIED

@test("Consensus engine returns a ConsensusResult")
def _():
    from axiom.mip.verification.consensus import VerificationConsensus
    engine = VerificationConsensus(timeout_seconds=10)
    result = engine.verify("a + b = b + a")
    assert result.final_verdict is not None
    assert result.agreement_ratio >= 0.0
    assert result.total_execution_time_ms >= 0

print()
print("══════════════════════════════════════════════════════════════")
print(f"  RESULTS: {len(PASSED)} passed, {len(FAILED)} failed")
print("══════════════════════════════════════════════════════════════")
if FAILED:
    print()
    print("FAILURES:")
    for name, err in FAILED:
        print(f"  ✗ {name}")
        print(f"    {err}")
    sys.exit(1)
else:
    print()
    print("  🎉 All tests passed!")
    sys.exit(0)
