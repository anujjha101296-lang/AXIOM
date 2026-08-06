# Product Health Report

**Generated:** 2026-08-06T18:29:46Z
**Product Health Score:** **31/100**

## What is broken?

- **No per-user data isolation** — Add user_id scoping to research store queries and migrations.
- **Shared SQLite store (no tenancy)** — Partition research data by authenticated user_id.
- **MDE API surface gap (26 e2e failures)** — Mount remaining MDE routes or narrow e2e scope with honest docs.
- **E2E test gap: MDE API surface** — Mount MDE routes or mark e2e as xfail with honest tracking

## What should be tested?

- Per-user data isolation (auth + research store scoping)
- Register/login/register spam and brute-force resistance
- PDF upload edge cases (scanned PDFs, large files)
- Research Q&A with configured vs mock model gateway

## What should be documented?

- MVP_READINESS.md blockers kept current after each release
- Demo vs Research mode contracts (`docs/MODES.md` when available)
- API authentication flows in `docs/api.md`

## Product Engineering Council View

**Ship contributor onboarding docs; resolve P0 MVP blockers before public alpha.**

Missing required docs: 0.0; workspace wedge is demo-ready, not production-ready.

---
*Product health reflects Research Workspace wedge readiness, not full platform vision.*