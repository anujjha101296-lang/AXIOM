# Research Capability Score

Unified 10-dimension score (0.0–1.0 per dimension). Composite averages all dimensions;
Human Intervention Required is inverted (lower intervention = higher contribution).

## Current Aggregate Scores

| Dimension | Score |
|-----------|------:|
| Evidence Quality | 0.750 |
| Human Intervention Required | 0.233 |
| Knowledge Integration | 0.714 |
| Literature Retrieval | 0.600 |
| Planning | 0.700 |
| Problem Understanding | 0.861 |
| Reasoning | 0.814 |
| Recovery From Failure | 0.413 |
| Reproducibility | 0.900 |
| Verification | 0.767 |
| **Composite (approx)** | **0.675** |

## Interpretation

- Scores below 0.5 indicate heuristic baseline; LLM-backed runs expected to improve reasoning and literature retrieval.
- Verification and evidence quality depend on formal tooling integration (S0-E3/S0-E4).

---
*Per-run scores stored in `rvp_runs` SQLite table.*