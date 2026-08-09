"""Tests for FMTP formal mathematics loop."""

from __future__ import annotations

import pytest

from axiom.core.verification.truthfulness import assign_from_proof_search, assert_not_false_formal_proof
from axiom.formal_math.benchmarks import estimate_difficulty, list_benchmarks
from axiom.formal_math.compilation import classify_compilation, compile_proof
from axiom.formal_math.conjecture import generate_conjecture
from axiom.formal_math.counterexample import search_counterexample
from axiom.formal_math.decomposition import decompose_goal
from axiom.formal_math.dependency_graph import build_dependency_graph
from axiom.formal_math.explanation import explain_formal_artifact
from axiom.formal_math.formalization import formalize_informal
from axiom.formal_math.library_search import search_library
from axiom.formal_math.millennium_gate import evaluate_millennium_readiness
from axiom.formal_math.models import ProofArtifact, ProofCompilationStatus
from axiom.formal_math.proof_search import generate_proof_strategies
from axiom.formal_math.prover_registry import list_provers
from axiom.formal_math.repair import create_failure_record, suggest_repair_tactics
from axiom.formal_math.store import FormalMathStore


@pytest.fixture
def store() -> FormalMathStore:
    return FormalMathStore(":memory:")


def test_prover_registry():
    provers = list_provers()
    assert len(provers) >= 3
    ids = {p.prover_id for p in provers}
    assert "lean4" in ids
    assert "smt" in ids


def test_formalize_informal_statement():
    result = formalize_informal("Prove that for all n, n + 0 = n")
    assert result.structured_statement
    assert result.formal_spec is not None
    assert "theorem" in result.formal_spec
    assert result.status.value in ("successfully_formalized", "partially_formalized")


def test_formalize_flags_ambiguity():
    result = formalize_informal("Probably many numbers are usually prime sometimes")
    assert result.status.value in ("ambiguous", "partially_formalized", "failed_formalization")


def test_explain_does_not_overclaim():
    spec = "theorem test (n : Nat) : n + 0 = n := by sorry"
    explanation = explain_formal_artifact(spec, compilation_status="unknown")
    assert "sorry" in explanation.lower() or "not formally verified" in explanation.lower()


def test_proof_strategies_generated():
    strategies = generate_proof_strategies("∀ n : ℕ, n + 0 = n")
    assert len(strategies) >= 5
    assert all("confidence" in s for s in strategies)


def test_compile_proof_never_claims_verified_from_simulation():
    artifact = ProofArtifact(
        proof_id="prf_test",
        theorem_id="ent_test",
        version=1,
        created_at="2026-01-01T00:00:00Z",
        prover="lean4",
        prover_version="4.x",
        formal_statement="n + 0 = n",
        source_code="theorem test : 1 = 1 := by norm_num",
        compilation_status=ProofCompilationStatus.UNKNOWN,
    )
    status, output, _ = compile_proof(artifact)
    if "SIMULATION" in output:
        assert status != ProofCompilationStatus.FORMALLY_VERIFIED


def test_truthfulness_simulated_not_formal():
    assignment = assign_from_proof_search(True, "SIMULATION: valid")
    assert_not_false_formal_proof(assignment)
    assert not assignment.formally_proven


def test_counterexample_finds_modular():
    record = search_counterexample(
        "x + y == z for all x,y,z",
        equation="x + y == z",
        variables=["x", "y", "z"],
        modulus=5,
    )
    assert record is not None
    assert record.counterexample


def test_library_search():
    results = search_library("add comm")
    assert results
    assert results[0]["relevance_score"] > 0


def test_decompose_implication():
    result = decompose_goal("test_thm", "P → Q")
    assert len(result["subgoals"]) >= 2


def test_store_versioned_proofs(store: FormalMathStore):
    entity = store.register_entity("theorem", "add_zero", "n + 0 = n")
    artifact = ProofArtifact(
        proof_id="prf_v1",
        theorem_id=entity.entity_id,
        version=1,
        created_at="2026-01-01T00:00:00Z",
        prover="lean4",
        prover_version="4.x",
        formal_statement="n + 0 = n",
        source_code="theorem add_zero : 1 = 1 := by sorry",
        compilation_status=ProofCompilationStatus.PARTIALLY_FORMALIZED,
    )
    store.save_proof(artifact)
    loaded = store.get_proof("prf_v1")
    assert loaded is not None
    assert loaded.theorem_id == entity.entity_id


def test_dependency_graph(store: FormalMathStore):
    lemma = store.register_entity("lemma", "helper", "a + b = b + a")
    theorem = store.register_entity(
        "theorem", "main", "uses commutativity",
        dependencies=[lemma.entity_id],
    )
    graph = build_dependency_graph(store, theorem.entity_id)
    assert any(n["id"] == lemma.entity_id for n in graph["nodes"])


def test_failure_record_and_repair():
    record = create_failure_record("ent_1", "ring", "tactic failed", attempted_tactic="ring")
    assert record.failure_id.startswith("pfl_")
    tactics = suggest_repair_tactics("n + 0 = n", "ring", previous_attempts=["ring"])
    assert "ring" not in tactics


def test_conjecture_starts_unverified():
    conj = generate_conjecture("∀ a b : ℕ, a + b = b + a", name="commutativity")
    assert conj["status"] == "UNVERIFIED"


def test_millennium_gate_not_ready_by_default():
    result = evaluate_millennium_readiness()
    assert not result.ready
    assert result.blockers


def test_benchmarks_listed():
    benches = list_benchmarks()
    assert len(benches) >= 3


def test_difficulty_estimation():
    easy = estimate_difficulty("formalize n + 0 = n")
    hard = estimate_difficulty("prove millennium open problem conjecture")
    assert hard["human_expertise_required"] > easy["human_expertise_required"]
