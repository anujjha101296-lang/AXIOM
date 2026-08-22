# AXIOM Phase 14 — Interactive Theorem Prover Bridge & Formal Verification Engine

## Overview

Phase 14 implements a unified multi-prover formal verification engine supporting **Lean 4**, **Coq**, and **Isabelle/HOL**. It translates mathematical theorems, validates tactic scripts, filters out incomplete proof tags (`sorry`, `admit`, `oops`), and provides a unified REST API for formal proof verification.

---

## Supported Interactive Theorem Provers

| Prover | File Extension | Key Tactics / Methods | Placeholder Filter |
|--------|----------------|------------------------|--------------------|
| **Lean 4** | `.lean` | `omega`, `rfl`, `simp`, `ring`, `decide`, `linarith` | `sorry` |
| **Coq** | `.v` | `reflexivity`, `auto`, `simpl`, `intros`, `induction`, `lia` | `admit`, `Admitted` |
| **Isabelle/HOL** | `.thy` | `by simp`, `by auto`, `by blast`, `by fastforce` | `sorry`, `oops` |

---

## Component Architecture

1. **`axiom/formal_prover/models.py`**: Pydantic v2 models for `FormalTheorem`, `FormalProof`, `ProofStep`, `FormalVerificationResult`, `ProverType`, `FormalStatus`.
2. **`axiom/formal_prover/lean4_bridge.py`**: Lean 4 source generator, tactic script validator, and `sorry` placeholder detector.
3. **`axiom/formal_prover/coq_bridge.py`**: Coq Gallina script generator, tactic validator, and `admit` placeholder detector.
4. **`axiom/formal_prover/isabelle_bridge.py`**: Isabelle/HOL theory generator, method validator, and `sorry`/`oops` placeholder detector.
5. **`axiom/formal_prover/engine.py`**: Unified multi-prover routing engine with automatic JSON result persistence to `evaluation_results/phase14/`.
6. **`axiom/services/api_gateway/routes/formal_prover.py`**: REST API router mounting `POST /api/v1/formal-prover/verify`.

---

## REST API

### `POST /api/v1/formal-prover/verify`
Verifies a formal proof script in Lean 4, Coq, or Isabelle.

**Request:**
```json
{
  "name": "add_comm_demo",
  "statement": "∀ (a b : Nat), a + b = b + a",
  "prover": "LEAN4",
  "tactic_script": "  intro a b\n  omega"
}
```

**Response:**
```json
{
  "verification_id": "...",
  "theorem_name": "add_comm_demo",
  "prover": "LEAN4",
  "status": "VERIFIED",
  "proof_code": "import Mathlib\n\ntheorem add_comm_demo : ∀ (a b : Nat), a + b = b + a := by\n  intro a b\n  omega",
  "error_message": null,
  "verification_time_ms": 1.01,
  "verified_at": "2026-08-22T13:52:00Z"
}
```

---

## Verification & Benchmarks

```bash
# Run unit tests
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python -m pytest tests/test_phase14_formal_prover.py -v

# Run 8-suite benchmark
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python benchmarks/phase14_formal_prover_benchmark.py
```
