# Millennium Readiness

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Purpose

Readiness framework for extremely difficult mathematical problems. This document does **not** implement a solver for any specific Millennium Prize Problem.

## Readiness requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Formal definitions | ⚠️ Partial | Epistemic graph supports claim nodes |
| Literature coverage | ⚠️ Partial | Research workspace + arXiv ingestion |
| Known-result database | ⚠️ Partial | Knowledge graph |
| Proof search | ⚠️ Planned | MCTS + Lean export exist |
| Counterexample search | ⚠️ Planned | SMT gateway exists |
| Symbolic mathematics | ⚠️ Partial | MIP/MDE modules |
| Formal verification | ⚠️ Partial | Lean exporter; verifier integration pending |
| Independent verification | ⚠️ Partial | E&R discovery gate |
| Reproduction | ⚠️ Partial | H1-OBS + E&R reproduction engine |
| Expert review | ⚠️ Manual | Human review flag in discovery gate |
| Long-running research | ✅ | GCP campaign framework |
| Research provenance | ✅ | H1-OBS + E&R claim registry |
| Failure memory | ⚠️ Partial | Rejected claims preserved |
| Versioned proof artifacts | ✅ | Claim versioning |

## Gate policy

No claim may be labeled `PROOF_OF_OPEN_PROBLEM` without:

- `FORMALLY_VERIFIED` status
- Independent verification
- Successful reproduction
- Human expert review
- Documented evidence chain

## Safety

"I don't know" and "interesting but unverified" are successful outcomes. A false discovery is worse than a failed research attempt.
