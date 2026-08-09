# Evidence Status

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Claim registry | ✅ New | SQLite `er_*` tables, versioned claims |
| Evidence objects | ✅ New | Typed evidence with provenance |
| Source provenance | ✅ New | `POST /evidence/sources` |
| Provenance graph | ✅ New | Edge table linking claims, evidence, experiments |
| Discovery gate | ✅ New | Status upgrades and discovery labels gated |
| Integrity audit | ✅ New | `GET /evidence/integrity`, health check |
| Dashboard | ✅ New | `GET /evidence/dashboard` |

**Overall maturity:** Early — foundations in place; integration with research campaigns ongoing.

## Implemented (E&R-1)

- `ClaimRegistry` with versioned claims and evidence objects
- Discovery gate preventing unauthorized status upgrades
- Provenance graph edges (supports, contradicts, derived_from, etc.)
- Integrity audit for missing provenance and broken links
- `/evidence/*` API with optional authentication

## Open gaps

- Automatic registration of SCEP runs as experiments (planned)
- Counterexample engine integration (future)
- Formal prover integrations (Lean, Isabelle, Coq — future)
- Research package export format (future)

## Refresh

```bash
make erl-health
```
