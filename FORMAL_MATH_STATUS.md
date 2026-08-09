# Formal Mathematics Status

**Last updated:** 2026-08-09  
**Loop:** FMTP (Formal Mathematics & Theorem-Proving)

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Prover registry | ✅ New | Lean4, Coq, Isabelle, SMT, SymPy |
| Math knowledge layer | ✅ New | Entities, proofs, dependencies in `fmtp_*` tables |
| Informal → formal | ✅ New | Pipeline with ambiguity detection |
| Formal → informal | ✅ New | Linked explanations, no overclaiming |
| Proof search | ✅ New | 8 strategy types + tactic suggestions |
| Library search | ✅ New | Builtin seed library + semantic search |
| Proof compilation | ✅ New | Truthfulness guards — simulation ≠ verified |
| Counterexample engine | ✅ New | SMT modular + randomized |
| Failure memory | ✅ New | Proof failures with repair suggestions |
| Millennium gate | ✅ New | Blocks premature prize campaigns |

**Overall maturity:** Early — foundations in place; Lean4 not installed in default environment.

## Refresh

```bash
make fmtp-health
```
