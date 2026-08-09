# Verification Factory (VFACTORY)

Permanent autonomous verification system for AXIOM. Every capability must have evidence that it works.

## Purpose

Discover defects before users, researchers, or autonomous research campaigns encounter them. Never declare a capability complete merely because code, tests, or documentation exist.

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| Registry | `axiom/vfactory/registry.py` | 15 seeded capabilities with acceptance criteria |
| Store | `axiom/vfactory/store.py` | SQLite persistence for capabilities, runs, evidence |
| Pyramid | `axiom/vfactory/pyramid.py` | Test hierarchy levels 1–10 |
| Journeys | `axiom/vfactory/journeys.py` | User journeys A–D (no simulation) |
| Scorer | `axiom/vfactory/scorer.py` | Per-domain verification scores |
| Roles | `axiom/vfactory/roles.py` | 12 controlled verification worker roles |
| Orchestrator | `axiom/vfactory/orchestrator.py` | Continuous verify loop |

## API

- `GET /vfactory/manifest`
- `GET /vfactory/status`
- `GET /vfactory/capabilities`
- `GET /vfactory/scores`
- `POST /vfactory/run/cycle`
- `POST /vfactory/run/journey`

## Health check

```bash
make vfactory-health
```

## Governance artifacts

- `VERIFICATION_STATUS.md`
- `VERIFICATION_MATRIX.md`
- `REGRESSION_LOG.md`
- `E2E_STATUS.md`

## Acceptance

VFACTORY-1 is complete when:

1. Registry seeds >= 14 capabilities
2. Journeys A–D pass against real stores
3. Verification cycle produces scored evidence
4. `make vfactory-health` passes
5. 14+ unit tests in `tests/test_vfactory.py`
