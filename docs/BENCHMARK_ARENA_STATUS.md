# Research Benchmark Arena Status

**Updated:** 2026-08-09  
**Package:** `axiom/evaluation/arena/`  
**Dataset:** `arena_v1` (60 cases)

## Audit (reuse)

| Existing | Role in Arena |
|----------|---------------|
| SCEP `axiom/evaluation/` | Capability scoring, SQLite eval tables, CLI runner |
| Discovery Engine | Honesty / FDR / multi-agent / memory cases |
| FMTP formalize | Formal math cases |
| SEC sandbox + counterexample | Experiment + counterexample cases |
| TSS `content_trust` | Security probe in score aggregation |
| `/eval` API | Sibling; Arena adds `/arena/*` |

**Not duplicated:** SCEP dimension suite remains; Arena adds research-task object model, tiers, gates, versioned 60-case suite, readiness, regression, UI.

## Baseline → improvement

| | Baseline | After fix |
|--|----------|-----------|
| Passed | 59/60 | 60/60 |
| Mean | 0.9917 | 1.0 |
| Failures | `fm_04` | none |
| research_depth | 0.0 | 1.0 |
| security | 0.5 (default) | 1.0 (measured probe) |
| Highest unlocked tier | 7 | 7 (Tiers 8–10 gated on long-horizon evidence) |

**Top baseline weaknesses fixed:** research_depth scoring coverage; formal hedging (`sometimes`); security measurement via injection detector.

**Artifacts:** `docs/ARENA_BASELINE.json`, `docs/ARENA_IMPROVEMENT_CYCLE.json`

## Honesty rules

- No fabricated scores
- Prose ≠ formal verification
- Missing retrieval ≠ novelty
- Higher tiers require gate evidence (Tier 8–10 need long-horizon floor)
- Hidden eval answers not exposed via catalog API
- Millennium never auto-claimed

## API / UI

- `GET /arena/catalog` · `POST /arena/run` · `GET /arena/runs` · `GET /arena/readiness`
- UI: `/arena`

## Replit / env

Uses `AXIOM_DB_PATH`. No new secrets. Ground truth stays in grader module, not catalog JSON.
