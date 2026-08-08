# AXIOM Operating System v1.0

## Continuous Evolution Loop

AXIOM is not a sequence of prompts. It is a **self-improving research organization** that continuously decides what to build next based on evidence, benchmarks, and recorded progress.

Every worker — human or AI — operates inside this loop. No task is "done" until evidence is recorded, state is updated, and the next highest-leverage work is queued.

```text
                        GRAND VISION
                              │
                              ▼
                Long-Term Scientific Roadmap
                              │
                              ▼
                Quarterly Strategic Objectives
                              │
                              ▼
                  Current Research Campaigns
                              │
                              ▼
               Capability Gap Identification
                              │
                              ▼
               Highest Leverage Initiative
                              │
                              ▼
                Architecture / Design Review
                              │
                              ▼
                     Implementation
                              │
                              ▼
                     Automated Testing
                              │
                              ▼
                     Benchmark Testing
                              │
                              ▼
                  Human Scientific Review
                              │
                              ▼
                Repository Documentation
                              │
                              ▼
                   Commit / Push / Release
                              │
                              ▼
                   Research Validation
                              │
                              ▼
                 Lessons Learned / Reflection
                              │
                              ▼
          Updated Capability Graph & Roadmap
                              │
                              └──────────────► Repeat
```

### End state

Eventually the loop collapses to:

```text
Observe → Learn → Reason → Discover → Verify → Publish → Learn Again
```

At that point AXIOM is an autonomous scientific research organization whose engineering, product, and research improve through the same disciplined feedback cycle.

---

## Seven Operating Layers

AXIOM runs seven nested loops. Each layer has a cadence, participants, inputs, outputs, and stop conditions.

| Layer | Name | Cadence | Automated? | Authority |
|------:|------|---------|------------|-----------|
| 1 | Strategic | Monthly | **No** | Founder + Chief Scientist + CTO |
| 2 | Engineering | Daily | Yes (Cursor agents) | Engineering contract |
| 3 | Research | Per campaign | Partial | Research + SME contracts |
| 4 | Product | Per release | Partial | Product contract + human approval |
| 5 | Scientific Capability | Weekly | Yes (benchmarks) | SCEP + capability map |
| 6 | Learning | Continuous | Partial | Memory + knowledge graph |
| 7 | Frontier Research | Per campaign tier | Partial | Grand Challenge Program |

---

## Layer 1 — Strategic Loop (Monthly)

**Never automated.** Humans set direction; the repository records decisions.

### Participants

- Founder
- Chief Scientist
- CTO (Cursor)

### Questions

1. What is our long-term scientific direction?
2. Are we still aligned with the mission?
3. Which capabilities matter most now?
4. What did we learn this month?
5. What should be abandoned?
6. What should become the next research campaign?

### Outputs

- Updated `ROADMAP.md` (quarterly objectives)
- Updated `TASK_QUEUE.md` (ranked initiatives)
- New or continued GCP campaign (`GRAND_CHALLENGE_PROGRAM.md`)
- Decision records in `MEMORY.md`

### Template

Use `.axiom/templates/MONTHLY_STRATEGIC_REVIEW.md`.

### Stop conditions

- External-action gate: spending, deployment, outreach, publication require human approval per `CONSTITUTION.md`.

---

## Layer 2 — Engineering Loop (Daily)

Cursor agents execute continuously inside repository scope.

```text
Read Repository
        ↓
Read Current State          (.axiom/CURRENT_STATE.md)
        ↓
Read Benchmarks             (SCEP, GCP, campaign results)
        ↓
Read Technical Debt         (TECH_DEBT_BOARD.md when present)
        ↓
Read Product Feedback       (when available)
        ↓
Select Highest ROI Task     (.axiom/TASK_QUEUE.md + DECISION_FRAMEWORK.md)
        ↓
Design
        ↓
Implement                   (.axiom/ENGINEERING.md)
        ↓
Test
        ↓
Benchmark
        ↓
Document
        ↓
Commit / Push
        ↓
Repeat
```

### Stops only for

- Founder decision
- Product decision requiring human approval
- Credentials / secrets
- Legal constraints
- External dependency unavailable

### Session entry

Every agent session begins with `AGENTS.md` → `CONSTITUTION.md` → `CURRENT_STATE.md` → `TASK_QUEUE.md`.

---

## Layer 3 — Research Loop (Per Campaign)

Every research campaign follows the scientific method cycle. When the Scientific Method Engine (SME) is available, it enforces this path. Until then, campaigns follow the same phases manually.

```text
Research Question
        ↓
Literature Review
        ↓
Knowledge Graph
        ↓
Hypothesis Generation       (>= 2 competing hypotheses)
        ↓
Criticism
        ↓
Experiment
        ↓
Verification                (explicit evidence tier)
        ↓
Reflection
        ↓
Research Report
        ↓
Capability Update           (.axiom/CAPABILITIES.md)
        ↓
Repeat
```

### Implementation

| Phase | Subsystem |
|-------|-----------|
| Campaign orchestration | `axiom/grand_challenge/` (GCP) |
| Scientific method | `axiom/scientific_method/` (SME, when merged) |
| Execution engine | `axiom/research_kernel/` (when merged) |
| Knowledge | `axiom/core/knowledge_graph/` |
| Verification | `axiom/core/verification/` |

---

## Layer 4 — Product Loop (Per Release)

Every release answers four questions:

```text
Did users understand it?
        ↓
Did they finish their task?
        ↓
Did they return?
        ↓
What confused them?
        ↓
Fix highest pain points
        ↓
Release again
```

### Contract

See `.axiom/PRODUCT.md`. Product claims require observed evidence — not assumed utility.

### Current product surface

- Research Workspace: `/research` API + UI
- API documentation: `/docs`

---

## Layer 5 — Scientific Capability Loop (Weekly)

**Do not ask:** "Did we add features?"

**Ask:** "Can AXIOM now do something it couldn't do last month?"

### Measures

| Dimension | Evidence source |
|-----------|----------------|
| Theorem / math understanding | SCEP `mathematical_reasoning` |
| Literature synthesis | SCEP `literature_synthesis` |
| Hypothesis quality | SCEP `conjecture_generation` + campaign journals |
| Verification accuracy | SCEP `proof_verification` + truthfulness audit |
| Autonomous planning | SCEP `research_planning` + workflow completion |
| Hallucination / false claims | Verification truthfulness tests |
| Benchmark scores | `make` benchmark targets, delta reports |

### Commands

```bash
make test                    # regression gate
python3 -m axiom.evaluation.run_benchmarks   # SCEP full suite
make gcp-benchmark           # campaign pipeline validation
```

### Capability promotion rule

A capability moves up the maturity ladder in `CAPABILITIES.md` only when:
1. Benchmark evidence exists
2. Limitations are documented
3. A human or independent review confirms (for `reproducible` and above)

---

## Layer 6 — Learning Loop (Continuous)

Every failure becomes organizational data.

```text
Failure
        ↓
Root Cause
        ↓
Knowledge Update            (KNOWLEDGE_GRAPH.md)
        ↓
Memory Update               (MEMORY.md)
        ↓
Benchmark Added             (if repeatable)
        ↓
Regression Test Added       (if code defect)
        ↓
Never Repeat Same Failure
```

### Rules

- Failed hypotheses are first-class outputs
- Regression tests protect fixed defects
- `docs/capability_delta_*.md` are milestone artifacts — do not bulk-commit

---

## Layer 7 — Frontier Research Loop (Campaign Tiers)

Millennium Prize problems are **near the end of the pipeline**, not the beginning.

```text
Known Problems              (GCP Tier 0)
        ↓
Reproduce Results           (GCP Tier 1)
        ↓
Known Proofs                (GCP Tier 1)
        ↓
Paper Reproduction          (GCP Tier 2)
        ↓
Small Open Problems         (GCP Tier 3)
        ↓
Domain Challenges           (GCP Tier 4)
        ↓
Frontier Problems           (GCP Tier 5 — readiness only)
        ↓
Potential Prize-Level Research   (human-authorized, evidence-gated)
```

### Authority

- Tier advancement requires readiness gates (`READINESS_GATES.md`)
- Tier 5 does not authorize prize solution attempts
- See `PRIZE_TRACK.md` for prize governance

---

## Engineering Cadence

| Frequency | Activities |
|-----------|------------|
| **Daily** | Improve one capability; run tests; run benchmarks; push focused commits |
| **Weekly** | Sprint review; product review; scientific review; update `CURRENT_STATE.md` |
| **Monthly** | Capability review; architecture review; research roadmap update; strategic review |
| **Quarterly** | Major release; new research campaigns; public benchmark publication (human-approved) |

---

## North Star Metrics

Do **not** measure: lines of code, number of agents, number of prompts.

See `.axiom/NORTH_STAR_METRICS.md` for definitions and current measurement status.

| Domain | Examples |
|--------|----------|
| Product | Weekly active researchers, sessions completed, time saved, retention |
| Scientific | Benchmark improvement, verification accuracy, autonomous task completion |
| Engineering | Test pass rate, regression rate, build stability |
| Research | Papers reproduced, hypotheses evaluated, failed hypotheses recorded |

**Honest rule:** If a metric is not yet measured, record `unavailable` — never invent values.

---

## Repository Map

Conceptual organization and where it lives today. See `.axiom/REPOSITORY_MAP.md`.

---

## Worker Protocol

### Starting a session

1. Read `CONSTITUTION.md`
2. Read `OPERATING_SYSTEM.md` (this document)
3. Read `CURRENT_STATE.md` and `TASK_QUEUE.md`
4. Read relevant domain contract
5. Execute highest-priority unblocked task
6. Test, benchmark, document
7. Update state, queue, memory, capabilities as appropriate
8. Commit and push

### Ending a session

- [ ] Tests pass (or failures documented with blockers)
- [ ] Benchmarks run if capability-affecting
- [ ] `CURRENT_STATE.md` updated
- [ ] `TASK_QUEUE.md` updated if priorities changed
- [ ] Durable learnings in `MEMORY.md`
- [ ] Focused commit pushed
- [ ] PR created/updated if on feature branch

### What workers must not do

- Fabricate benchmark results or capability claims
- Skip state updates after meaningful work
- Treat prompt completion as organizational progress
- Advance GCP tiers without passing readiness gates
- Claim prize progress without evidence and human authorization

---

## Document Index

| Document | Role in OS |
|----------|------------|
| `CONSTITUTION.md` | Principles and authority boundaries |
| `OPERATING_SYSTEM.md` | This document — master loop |
| `CURRENT_STATE.md` | Live organizational state |
| `TASK_QUEUE.md` | Ranked executable work |
| `ROADMAP.md` | Long-term outcomes |
| `CAPABILITIES.md` | Capability maturity inventory |
| `NORTH_STAR_METRICS.md` | What we measure |
| `REPOSITORY_MAP.md` | Code ↔ concept mapping |
| `DECISION_FRAMEWORK.md` | Prioritization formula |
| `ENGINEERING.md` | Layer 2 contract |
| `RESEARCH.md` | Layer 3 contract |
| `PRODUCT.md` | Layer 4 contract |
| `PMO.md` | Daily/weekly operating cadence |
| `GRAND_CHALLENGE_PROGRAM.md` | Layer 7 campaigns |
| `PRIZE_TRACK.md` | Frontier governance |
