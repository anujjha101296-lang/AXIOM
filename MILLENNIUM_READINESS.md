# Millennium Readiness

**Last updated:** 2026-08-09  
**Loop:** FMTP (updated from E&R)

## Purpose

Readiness framework for extremely difficult mathematical problems. This document does **not** implement a solver for any specific Millennium Prize Problem.

## Readiness requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Formal definitions | ✅ | FMTP entity registry |
| Literature coverage | ⚠️ Partial | Research workspace + arXiv ingestion |
| Known-result database | ⚠️ Partial | Knowledge graph + library search |
| Proof search | ✅ | FMTP proof search engine |
| Counterexample search | ✅ | SMT + randomized testing |
| Symbolic mathematics | ⚠️ Partial | SymPy via tool registry |
| Formal verification | ⚠️ Partial | Lean4 compile when installed; simulation otherwise |
| Independent verification | ⚠️ Partial | E&R discovery gate |
| Reproduction | ⚠️ Partial | H1-OBS + E&R reproduction engine |
| Expert review | ⚠️ Manual | Human review flag in discovery gate |
| Long-running research | ✅ | GCP campaign framework |
| Research provenance | ✅ | H1-OBS + E&R claim registry |
| Failure memory | ✅ | FMTP failure records |
| Versioned proof artifacts | ✅ | `fmtp_proofs` + version archive |
| Benchmark level ≥ 4 | ❌ | Current max demonstrated: level 4 defined, not passed |

## Gate policy

No claim may be labeled `PROOF_OF_OPEN_PROBLEM` without:

- `FORMALLY_VERIFIED` status from actual prover
- Independent verification
- Successful reproduction
- Human expert review
- Documented evidence chain
- Millennium readiness gate score ≥ 0.75

## API

```bash
GET /formal/millennium/readiness
```

## Safety

"I don't know" and "interesting but unverified" are successful outcomes. A false discovery is worse than a failed research attempt.

## Refresh

```bash
make fmtp-health
```
