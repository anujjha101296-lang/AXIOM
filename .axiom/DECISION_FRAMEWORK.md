# Decision Framework

Read `CONSTITUTION.md`, `CURRENT_STATE.md`, `TASK_QUEUE.md`, `ROADMAP.md`, `PRODUCT.md`, `RESEARCH.md`, and `MEMORY.md` before prioritizing work.

## Decision record

Every material decision records: context, alternatives, evidence and its quality, assumptions, risks, expected outcome, owner, expiry/review date, and decision. Store a concise record in `MEMORY.md` and link supporting artifacts in `KNOWLEDGE_GRAPH.md`.

## Prioritization

For ordinary tasks, score each 1–5:

`(impact + dependency unlock + scientific value + engineering value + prize-readiness impact) × confidence × reversibility ÷ effort`

Use the score to compare candidates, not to hide judgment. Evidence quality adjusts confidence: direct observed outcomes and reproducible benchmarks outrank expert opinion, desk research, prototypes, and model inference.

## Mandatory gates

- **P0 gate:** security, data loss, false verification/scientific claims, and supported-build failure take priority.
- **Experiment gate:** uncertain investments require a hypothesis, smallest test, success metric, and stop condition.
- **External-action gate:** a human must approve spending, deployment, outreach, contracts, publication, and material data access.
- **Kill gate:** abandon or park work when the experiment fails, evidence weakens, a cheaper alternative exists, or it no longer advances an active capability.

Link resulting tasks to `TASK_QUEUE.md`, strategic changes to `ROADMAP.md`, and enduring learning to `MEMORY.md`.
