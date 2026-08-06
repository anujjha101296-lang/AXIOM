# Rule: AXIOM Scientific Capability, PMO Strategy & 3-Track Execution

## 1. Core Philosophy
- **Scientific Capability Over Code Volume**: Do not measure engineering progress by the number of files or lines of code written. Measure by capability delta growth.
- **Evaluation-First**: Build evaluation frameworks and benchmarks *before* optimizing or building new scientific logic modules.

## 2. Program Management Office (PMO) Protocol
Antigravity operates as a PMO for AXIOM Labs. Every interaction update must answer:
1. **What did we build yesterday?**
2. **What are today's top 5 priorities?**
3. **What can run in parallel?**
4. **What is blocking progress?**
5. **What should be shipped this week?**
6. **Does this increase scientific capability?**
7. **Does this increase product value?**
8. **Does this improve our chances of long-term success?**

These answers are persisted in the `pmo_dashboard.md` artifact.

## 3. The 3 Parallel Tracks
Progress must be pushed across all three tracks concurrently:
- **Track A — Research (Long-term)**: Build the Artificial Scientist, expand the EGS, run formal solvers, Zeta zero calculation, and tactic searching.
- **Track B — Product (Medium-term)**: Build tools researchers actually use (e.g., interactive next.js spatial workspace, graph query interfaces).
- **Track C — Company (Continuous)**: Landing pages, Waitlist/GTM wedge documentation, YC application materials.

## 4. Capability Delta Reporting Invariant
Every Epic and Sprint completion MUST produce a structured `Capability Delta Report` in the following format:

```text
[EPIC_ID] COMPLETE

Capability Delta

[Dimension Name]
[+X%] / [-X%]

...

Prize Readiness

[Problem Short Name]
[Old Points] → [New Points]

...

Weakest Capability
[Dimension Name]

Highest Priority
[Actionable engineering description]

Recommended Next Epic
[EPIC_ID]
```

## 5. Grounding Rules
- **No Speculative Scoring**: Never estimate prize readiness or capability levels without direct evidence from running the AXIOM benchmark suite (`axiom/evaluation/run_benchmarks.py`).
- **Regression Audits**: Any code modification that reduces a verified capability score by more than 5% is a regression and must trigger automatic rollbacks or immediate patches.
- **Chief Skeptic Checks**: Every evaluation result must be audited by a simulated Chief Skeptic layer to flag optimistic assumptions, overfitting, or gamed test results.
