# AXIOM Engineering Roadmap

This is an evidence-led roadmap, not an automatic commitment. Re-rank work after each sprint using the process in `ENGINEERING.md`.

## Sprint 0 — Establish a trustworthy engineering baseline

**Objective:** make the repository's engineering contract, supported runtime, and verification baseline explicit before expanding scientific capability.

### Repository audit — 2026-08-05

| Rank | Finding | Impact | Required outcome |
|---:|---|---|---|
| P0 | Declared Python requirement is 3.10+, but tests were run with Python 3.9.6 and fail during Pydantic model import on `str | None`. | No trustworthy test baseline | Provision and document a Python 3.10+ environment; rerun the full suite. |
| P0 | Formal-prover adapters support fallback simulation. | Risk of overstating verification | Preserve explicit result-status boundaries in code, API docs, and tests. |
| P1 | EPIC-002 evaluation framework is present but uncommitted. | New scoring must be evidence-grounded | Review and integrate only after the supported test baseline is green. |
| P1 | Architecture is documented but lacks an operating contract for product-agnostic capability growth. | Inconsistent future decisions | Maintain `VISION.md`, `ENGINEERING.md`, and `ARCHITECTURE.md`. |

### Epics and acceptance criteria

#### S0-E1: Engineering contract — complete

- Add a durable vision, engineering contract, and architecture contract.
- Replace the obsolete auto-generated roadmap with an explicit, ranked engineering roadmap.
- Document safe autonomy and human-decision boundaries.

#### S0-E2: Supported runtime baseline — **core complete (2026-08-06)**

- Provide a Python 3.10+ development and CI runtime.
- Make the local setup and Docker configuration agree on the supported runtime.
- Run the complete suite under the supported runtime and record the result.

**Acceptance criterion:** all test collection errors caused by Python 3.9 compatibility are eliminated without weakening type annotations or validation semantics.

**Result:** Core suite green (`134/134` with `--ignore=tests/e2e`). Full suite `334/360`; 26 e2e failures documented (MDE API surface gap).

#### S0-E3: Verification truthfulness audit

- Audit public verification routes and result models.
- Ensure simulated, heuristic, and actual compiler-backed results are distinguishable end to end.
- Add regression tests for status labeling and unsupported-prover behavior.

**Acceptance criterion:** no API response can label a fallback/simulated verification as a formal proof.

**Result:** `axiom/core/verification/truthfulness.py` centralizes evidence modes; `/verify/conjecture`, `/verify/proof`, `/mip/formal/compile`, and `/mip/verify/claim` expose `evidence_mode` and `formally_proven`. Core suite `154/154`.

#### S0-E4: EPIC-002 integration gate

- Review the uncommitted capability framework against its documented evidence rules.
- Add focused tests for composite-score calculation, level classification, and estimated-score labeling.
- Integrate it only with a green supported-runtime baseline.

**Acceptance criterion:** all capability and prize-readiness scores include evidence state, benchmark count, and stated limitations.

## Deferred work

- Larger autonomous research-company workflows: requires Founder and Chief Scientist direction after Sprint 0 evidence is available.
- New product domains beyond mathematical intelligence: requires validated problem/customer evidence.
- Production deployment, customer outreach, spending, or publication: human decision required.

## Next decision

Authorize a Python 3.10+ runtime (local environment, CI, or Docker) for Sprint 0 E2. Once available, engineering can complete the baseline and return a test-backed review of the EPIC-002 work.
