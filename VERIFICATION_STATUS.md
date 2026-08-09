# Verification Status

**Last updated:** 2026-08-09  
**System:** VFACTORY (Verification Factory) + E&R

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Capability registry | ✅ | 15 capabilities seeded via `/vfactory` |
| Test pyramid | ⚠️ Partial | Levels 1–2, 8 automated; 9–10 partial |
| User journeys A–D | ✅ | Executable via VFACTORY orchestrator |
| Verification scoring | ✅ | Per-domain + overall scores |
| Independent verification | ⚠️ Partial | Journey tests use real stores, not mocks |
| Claim status ladder (E&R) | ✅ | UNKNOWN → … → VERIFIED → FORMALLY_VERIFIED |
| Discovery gate | ✅ | Major labels require verification + human review |
| Formal verification | ⚠️ Partial | Lean exporter + compilation gate; prover optional |
| E2E browser tests | ⚠️ Pending | 226 tests excluded from CI |
| Performance baselines | ❌ Not automated | — |
| Load testing | ❌ Not automated | — |

## Verification Factory API

- `GET /vfactory/manifest` — pyramid levels, journeys, roles
- `GET /vfactory/status` — scores, capabilities, recent runs
- `POST /vfactory/run/cycle` — full verification cycle
- `POST /vfactory/run/journey` — single journey test

## Verification rules

1. `VERIFIED` cannot be granted from simulation-only evidence
2. `FORMALLY_VERIFIED` requires actual prover validation
3. Informal model-generated proofs are never labeled `FORMALLY_VERIFIED`
4. A capability is complete only when acceptance criteria are demonstrated by executable verification

## Refresh

```bash
make vfactory-health
make erl-health
```

See also: [VERIFICATION_MATRIX.md](VERIFICATION_MATRIX.md), [E2E_STATUS.md](E2E_STATUS.md), [REGRESSION_LOG.md](REGRESSION_LOG.md)
