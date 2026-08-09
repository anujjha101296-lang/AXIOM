# Mathematical Capability

**Last updated:** 2026-08-09  
**Loop:** FMTP

## Capability matrix

| Capability | Maturity | Evidence |
|------------|--------|----------|
| Understand formal math | Early | Prover registry, explanation pipeline |
| Formalize informal math | Early | Lean exporter integration |
| Search libraries | Early | Semantic search over seed library |
| Generate proof strategies | Early | 8 strategies + MIP tactics |
| Test conjectures | Early | Counterexample engine (SMT) |
| Generate formal proofs | Early | MIP Lean4 generator |
| Repair failed proofs | Early | Failure analysis + tactic suggestions |
| Compose verified lemmas | Planned | Dependency graph only |
| Explain formal results | Early | Linked explanations |
| Reproduce published math | Planned | Level 4 benchmarks defined |
| Assist human mathematicians | Early | `/formal/*` API |

## SCEP dimensions

Formal math capability maps to EPIC-002 dimensions:

- `mathematical_reasoning`
- `proof_verification`
- `conjecture_generation`
- `counterexample_search`

## Refresh

```bash
make fmtp-health
make cel-health
```
