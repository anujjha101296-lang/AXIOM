# Next Research Targets

## ONE Recommended Initiative

### P3-WF — Mount Workflow Engine HTTP API

Expose the existing workflow engine (`axiom/workflow/`) via `/workflows/*` and link
workflow runs to H1-OBS provenance records. H1-OBS is complete; autonomous research
(Program 3) is blocked until workflows are callable over HTTP.

## Staged Progression

| Priority | Target | Rationale |
|---------:|--------|-----------|
| 1 | Mount `/workflows` router in `main.py` | Code exists; 404 blocks autonomous research |
| 2 | Merge research loop branch | Long-horizon discovery orchestration |
| 3 | Stage 1 known-answer batch (n≥50) | Measure answer-score trend with provenance |
| 4 | Wire LLM to research reports | Replace heuristic templates |
| 5 | Formal prover CI (Lean 4) | Convert simulated proof tier to measured |

## Weak Dimensions (from latest runs)

- **human intervention required** — 0.219
- **recovery from failure** — 0.408
- **literature retrieval** — 0.600

---
*Exactly one initiative recommended per cycle. See `.axiom/TASK_QUEUE.md`.*