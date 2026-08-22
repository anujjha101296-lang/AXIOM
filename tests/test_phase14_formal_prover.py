"""Tests for Phase 14 — Interactive Theorem Prover Bridge & Formal Verification Engine."""
import pytest
from axiom.formal_prover.models import (
    FormalTheorem,
    ProverType,
    FormalStatus,
)
from axiom.formal_prover.lean4_bridge import Lean4Bridge
from axiom.formal_prover.coq_bridge import CoqBridge
from axiom.formal_prover.isabelle_bridge import IsabelleBridge
from axiom.formal_prover.engine import FormalVerificationEngine


def test_lean4_verification_success():
    bridge = Lean4Bridge()
    thm = FormalTheorem(
        name="add_comm_demo",
        statement="∀ (a b : Nat), a + b = b + a",
        prover=ProverType.LEAN4,
    )
    tactic_script = "  intro a b\n  omega"
    res = bridge.verify_lean4_script(thm, tactic_script)

    assert res.status == FormalStatus.VERIFIED
    assert "omega" in res.proof_code
    assert res.error_message is None


def test_lean4_verification_rejects_sorry():
    bridge = Lean4Bridge()
    thm = FormalTheorem(
        name="fake_thm",
        statement="∀ (n : Nat), n = n + 1",
        prover=ProverType.LEAN4,
    )
    tactic_script = "  sorry"
    res = bridge.verify_lean4_script(thm, tactic_script)

    assert res.status == FormalStatus.UNPROVED_SORRY
    assert "sorry" in res.error_message.lower()


def test_coq_verification_success():
    bridge = CoqBridge()
    thm = FormalTheorem(
        name="plus_O_n",
        statement="forall n : nat, 0 + n = n",
        prover=ProverType.COQ,
    )
    tactic_script = "  intros n. reflexivity."
    res = bridge.verify_coq_script(thm, tactic_script)

    assert res.status == FormalStatus.VERIFIED
    assert "reflexivity" in res.proof_code


def test_isabelle_verification_success():
    bridge = IsabelleBridge()
    thm = FormalTheorem(
        name="add_comm_isabelle",
        statement="((a::nat) + b = b + a)",
        prover=ProverType.ISABELLE,
    )
    tactic_script = "  by simp"
    res = bridge.verify_isabelle_script(thm, tactic_script)

    assert res.status == FormalStatus.VERIFIED
    assert "simp" in res.proof_code


def test_unified_formal_engine():
    engine = FormalVerificationEngine()
    thm = FormalTheorem(
        name="engine_test",
        statement="a + 0 = a",
        prover=ProverType.LEAN4,
    )
    res = engine.verify_theorem(thm, "  rfl")

    assert res.status == FormalStatus.VERIFIED
    assert res.prover == ProverType.LEAN4
