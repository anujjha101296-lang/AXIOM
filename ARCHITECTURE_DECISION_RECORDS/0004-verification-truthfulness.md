# ADR-0004: Verification Truthfulness Labeling

**Status:** Accepted  
**Date:** 2026-08-06  
**Related:** S0-E3

## Context

Formal prover adapters (Lean, Coq, Isabelle) can fall back to simulation when compilers are absent. API responses previously risked overstating verification strength.

## Decision

Centralize evidence classification in `axiom/core/verification/truthfulness.py`:

- Every verification result exposes `evidence_mode` and `formally_proven`
- Only actual compiler success may yield formal-proof tier labels
- Simulated, heuristic, and SMT paths are explicitly labeled
- Regression tests in `tests/test_verification_truthfulness.py` enforce the contract

## Consequences

- **Positive:** No API response can claim formal proof from a fallback path
- **Positive:** Contributors have a single module to update for labeling rules
- **Negative:** UI and docs must display evidence mode, not just pass/fail
- **Invariant:** Do not merge changes that hide `evidence_mode` from public responses
