# Verification Status

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Claim status ladder | ✅ | UNKNOWN → … → VERIFIED → FORMALLY_VERIFIED |
| Discovery gate | ✅ | Major labels require verification + human review |
| Independent verification | ⚠️ Partial | Manual flags; automated paths pending |
| Formal verification | ⚠️ Partial | Lean exporter exists; E&R gate enforces verifier identity |
| Differential verification | ⚠️ Planned | Multi-model/algorithm comparison not yet automated |
| Counterexample search | ⚠️ Planned | SMT gateway exists; counterexample registry pending |

## Verification rules

1. `VERIFIED` cannot be granted from simulation-only evidence
2. `FORMALLY_VERIFIED` requires `formal_proof` evidence with `formally_verified=true` and verifier identity
3. Informal model-generated proofs are never labeled `FORMALLY_VERIFIED`
4. Discovery labels require independent verification, reproduction, and human review

## Future integrations

- Lean, Isabelle, Coq theorem provers
- Independent evidence search for scientific claims
- Property-based and randomized counterexample testing

## Refresh

```bash
make erl-health
```
