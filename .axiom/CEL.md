# Continuous Evolution Loop (CEL)

AXIOM engineering operates as a continuous organization, not a sequence of prompts. This document encodes the master loop for CTO-mode autonomous work.

## Mission

Move AXIOM toward:

1. Best AI-native research platform
2. Daily-use researcher product
3. Trustworthy scientific reasoning
4. Frontier scientific research contribution

Optimize **measurable capability**, not feature count.

## Master loop

```text
READ → EVALUATE → PRIORITIZE → ARCHITECTURE REVIEW → IMPLEMENT
  → VALIDATE → SCIENTIFIC VALIDATION → PRODUCT VALIDATION
  → LEARN → UPDATE REPOSITORY → COMMIT
```

Repeat until a stop condition applies.

### Step 1 — Read

- `.axiom/CURRENT_STATE.md`
- `.axiom/ROADMAP.md`
- `.axiom/TASK_QUEUE.md`
- `TECH_DEBT.md`
- `BENCHMARK_RESULTS.md`
- `PRODUCT_SCORECARD.md`
- `ENGINEERING_SCORECARD.md`
- Repository, git history, open issues, prior failures and regressions

### Step 2 — Evaluate repository health

Assess maturity, missing capabilities, broken workflows, product/research gaps, engineering risks, technical debt, benchmark regressions, security, and performance.

### Step 3 — Prioritize

Score each candidate on: user impact, scientific capability impact, engineering leverage, long-term strategic value, risk reduction, implementation cost, dependencies. Select **exactly one** highest-leverage initiative.

### Step 4 — Architecture review

Search the repository, reuse existing systems, avoid duplication, refactor only when justified.

### Step 5 — Implementation

Design, implement, refactor carefully, add tests, documentation, logging, and metrics.

### Step 6 — Validation

Run unit, integration, e2e, benchmark, static analysis, security, performance, and regression tests. Fix failures before continuing.

### Step 7 — Scientific validation

When research functionality changes: run research benchmarks, compare to prior release, measure accuracy, evidence quality, verification quality, reasoning quality, reproducibility, cost, and latency. Never claim improvement without benchmark evidence.

### Step 8 — Product validation

Confirm the change improves research workflow, onboarding, usability, reliability, speed, or research productivity.

### Step 9 — Learning

Record lessons, architecture decisions, failures, successful patterns, benchmark changes, and new technical debt. Update documentation.

### Step 10 — Repository update

Update `CURRENT_STATE.md`, `ROADMAP.md`, `CHANGELOG.md`, `TASK_QUEUE.md`, `BENCHMARK_RESULTS.md`, and scorecards.

### Step 11 — Commit

Meaningful commit, push, engineering summary: what changed, why, files modified, tests run, benchmarks, limitations, next initiative.

## Stop conditions

Pause only when:

- Founder decision required
- External credentials required
- Legal or compliance approval required
- Blocked by external dependencies

## Founding principles

Truth over fluency. Evidence over confidence. Benchmarks over opinions. General capability over one-off solutions. Reproducibility over impressive demos. Scientific integrity over speed.
