# Open Problem Research Lab — Status

**Updated:** 2026-08-09  
**Package:** `axiom/open_problems/`  
**Branch:** `cursor/integrate-mainline-dc7e`

## Audit (reuse, do not rebuild)

| Existing | Reused for |
|----------|------------|
| FRCE `FrontierCampaignEngine` | Campaigns, decompose, strategies, cycles |
| Discovery Engine | Hypotheses, counterexamples, formal bridge |
| SKAI | Literature/seed acquisition, gaps |
| FMTP | Formalization attempts |
| SEC | Computational experiments |
| Arena ladder | Staged Level 1–9 progression (no Millennium claim) |

## Implemented (v1)

- First-class `OpenProblem` with gated research statuses
- Intake / understand (definitions, variables, assumptions, conclusion)
- Known-result map (proven / disproven / conjectured / empirical / unknown) — categories never merged
- Literature map stubs filled from seeded SKAI text (UNTRUSTED where external)
- Decomposition into scored subproblems
- Competing strategies + independent tracks (analytical / computational / formal / counterexample / literature)
- Persistent campaigns linked to FRCE + Discovery
- Timeline events (no fabrication)
- Staged progression Levels 1–9; Level 9 Millennium **not** auto-started
- API `/open-problems/*` + UI `/open-problems`
- Level-1 campaign: known-false conjecture → **REFUTED** via counterexample-first (composite enumeration)

## Level-1 evidence

See `docs/OPEN_PROBLEM_LEVEL1_RUN.json`. Status `REFUTED` / `REFUTED_BY_COUNTEREXAMPLE`. Not a scientific discovery claim. Not Millennium.

## Level-2 evidence

See `docs/OPEN_PROBLEM_LEVEL2_RUN.json`. Known theorem (`add_comm`) → literature enrichment (SKAI + formal library) → `PROOF_ATTEMPTED` → `FORMALIZATION_ATTEMPTED_UNVERIFIED`. Not RESOLVED.

## Failure fixed this cycle

Discovery `quality_check` rejected **all** hypotheses when the research question embedded `(known false)`, which skipped counterexample search. Affirmative H1 rejection retained; null/scoped/abstention survive; trap + small-case odd-composite probe restored.

## Honesty

- Never claim RESOLVED without verification gate
- Never claim Millennium readiness
- Computational evidence ≠ proof
- Missing literature ≠ novelty

## Replit / env

| Item | Value |
|------|-------|
| Env | `AXIOM_API_TOKEN`, `AXIOM_DB_PATH`, `JWT_SECRET_KEY` (no secrets in git) |
| API startup | `source .venv/bin/activate && make dev` → `:8000` |
| UI | `cd ui && npm run dev -- --hostname 0.0.0.0 --port 3000` → `/open-problems` |
| Database | SQLite via `AXIOM_DB_PATH` (shared with Discovery/FRCE/SEC) |
| Workers | In-process cycles (`POST /open-problems/{id}/cycle`); no separate worker required for v1 |
| Research tools | Reuses FRCE + Discovery + SEC sandbox |
| Formal tools | FMTP bridge via Discovery when available |
| Benchmark | `cd /tmp && pytest /workspace/tests/test_open_problem_lab.py -q` |

## OPLAB-1 progress

- `enrich_literature_map`: SKAI acquire/synthesize/survey + allowlisted HTTPS URLs + formal `search_library`
- Level-2 known-theorem campaign with formal bridge timeline events
- Still missing: broader external prior-art crawl; Level-3 historical conjecture reproduction gate

## Next (OPLAB-1 continued / OPLAB-2)

Level-3 historical conjecture run; stronger independent verification of formalization.
