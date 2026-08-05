# Program Management Office Contract

Read [CONSTITUTION.md](CONSTITUTION.md), [CURRENT_STATE.md](CURRENT_STATE.md), [TASK_QUEUE.md](TASK_QUEUE.md), [ROADMAP.md](ROADMAP.md), [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md), [CAPABILITIES.md](CAPABILITIES.md), [PRODUCT.md](PRODUCT.md), [GTM.md](GTM.md), [RESEARCH.md](RESEARCH.md), [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md), and [MEMORY.md](MEMORY.md) before performing PMO work.

## Mandate

The PMO makes progress legible and keeps three concurrent tracks aligned with AXIOM's purpose. It does not replace the task queue, invent completion, or authorize external commitments.

| Track | Near-term outcome | Primary evidence |
|---|---|---|
| A — Research | A measurable, reproducible artificial-scientist capability | Benchmarks, provenance, verification, and independent review |
| B — Product | A workflow researchers can repeatedly use and value | Observed use, usability tests, and direct user feedback |
| C — Company | A credible learning and distribution engine | Approved market evidence, pilots, operating artifacts, and shipped public materials |

The operating goal is compounding organizational capability, not maximizing feature count, demos, or unsupported scientific claims. The PMO applies the human-approval boundaries in [CONSTITUTION.md](CONSTITUTION.md): no external outreach, marketing claim, spend, deployment, contract, publication, or material data use without human authorization.

## Sources of truth and authority

| Question | Authoritative source | PMO responsibility |
|---|---|---|
| What is true now, completed, blocked, and highest priority? | [CURRENT_STATE.md](CURRENT_STATE.md) | Reconcile the daily brief to it; flag contradictions rather than silently choosing a different fact. |
| What is the next executable work? | [TASK_QUEUE.md](TASK_QUEUE.md) | Preserve its rank and dependency logic; propose additions only with a decision record. |
| What outcomes and sequencing matter? | [ROADMAP.md](ROADMAP.md) | Test whether this week's plan advances a measurable horizon outcome. |
| What did we learn or decide? | [MEMORY.md](MEMORY.md) | Ensure durable outcomes have an append-only record and evidence links. |
| What capability is actually mature? | [CAPABILITIES.md](CAPABILITIES.md) | Prevent a plan from treating prototypes as validated capability. |
| What evidence and relationships support a claim? | [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md) | Require provenance and explicit links for material claims. |

Git history, test/benchmark logs, and reproducible artifacts outrank a PMO narrative. The PMO must label each statement as **fact**, **proposal**, or **assumption**. If a status cannot be independently supported, write `unknown`, not `complete`.

## Daily operating brief

Create or refresh one dated daily brief at the start and end of each meaningful workday. Keep the current brief in `CURRENT_STATE.md`; keep a dated copy in an approved project-log location when one exists. Do not overwrite the memory ledger: record enduring events in [MEMORY.md](MEMORY.md) using its append-only protocol.

The brief must answer these questions directly:

1. **Yesterday's output:** commits, artifacts, test/benchmark results, decisions, and learnings; state `no verified output recorded` when appropriate.
2. **Today's top five priorities:** first use the highest-ranked unblocked queue items; list track, owner, dependency, acceptance signal, and why it outranks alternatives.
3. **Parallel work:** work may run concurrently only when file ownership, dependencies, and external-approval boundaries do not conflict.
4. **Blockers:** blocker, affected task, evidence, owner/authority required, safe workaround, and next review time.
5. **Week shipping target:** one bounded, demonstrable internal or approved external outcome, its evidence threshold, and its explicit non-goal.
6. **Strategic value:** for each priority, state its contribution to scientific capability, user/product value, and long-term organizational learning. A blank contribution is a reason to deprioritize it.

Use the [daily brief template](#daily-brief-template) below. Use the [weekly review template](templates/WEEKLY_REVIEW.md) at the end of each operating week or milestone.

## Update mechanics

### Start of day

1. Read the source-of-truth documents in the order above; inspect `git status`, relevant recent commits, and the latest reproducible test/benchmark output.
2. Reconcile yesterday's planned acceptance signals with observed results. Mark a result as complete only when the signal is met.
3. Select the first unblocked task in [TASK_QUEUE.md](TASK_QUEUE.md). If it is blocked, preserve the blocker and select the next independent safe task under its queue protocol.
4. Allocate independent work across Tracks A–C only when each workstream has a named artifact, acceptance signal, and no overlapping mutable-file ownership.

### During execution

- Record material decisions with alternatives, evidence quality, assumptions, risks, owner, and review date according to [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md).
- Treat proposed website copy, customer outreach, pricing, public demos, and fundraising as internal drafts until a human approves external use.
- Escalate a human decision in [CURRENT_STATE.md](CURRENT_STATE.md) when it is required; continue independent, safe work instead of waiting.
- Stop or park a workstream when its stated stop condition is met, then record the result rather than relabeling it as progress.

### End of day

1. Verify claims against commits, tests, benchmark artifacts, or recorded evidence.
2. Update [CURRENT_STATE.md](CURRENT_STATE.md) with factual completion, blockers, and the next highest priority.
3. Update [TASK_QUEUE.md](TASK_QUEUE.md) only for ranked, acceptance-defined work; update [ROADMAP.md](ROADMAP.md) only when evidence changes sequencing or an outcome.
4. Append durable decisions, failures, experiments, and evidence to [MEMORY.md](MEMORY.md); add material nodes and edges to [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md).
5. Commit focused changes following [ENGINEERING.md](ENGINEERING.md). Do not stage work owned by another workstream.

## Prioritization and capacity rules

Apply the formula and mandatory gates in [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md). P0 integrity, security, data-loss, false-claim, and supported-build failures outrank all three tracks.

For non-P0 work, reserve capacity deliberately:

- **Research:** at least one bounded uncertainty-reducing experiment or baseline-improving task whenever an executable, evidence-backed task exists.
- **Product:** at least one internal workflow-validation or usability artifact whenever the research baseline is not at risk. A product candidate becomes a queued task only after it states user, job, current alternative, value hypothesis, evidence, smallest test, and stop condition as required by [PRODUCT.md](PRODUCT.md).
- **Company:** maintain a current positioning, documentation, waitlist/website plan, or pilot-readiness artifact as an internal draft. Moving it outside the repository requires the appropriate human approval under [GTM.md](GTM.md).

Capacity allocation is a hypothesis, not a quota. A track may receive zero active implementation capacity when dependencies, evidence, or the P0 gate justify it; record why and when it will be reconsidered.

## Dependency and parallelism protocol

Before starting concurrent work, publish a compact workstream card in the daily brief:

| Field | Requirement |
|---|---|
| Workstream | Track and outcome |
| Owner | One accountable owner/team |
| Inputs | Required source docs, code, evidence, or human approval |
| Mutable paths | Exclusive files/directories, or an explicit merge order |
| Acceptance signal | Test, benchmark, review, or validated observation |
| Stop condition | What makes the work no longer worth continuing |
| Handoff | Where evidence and next task will be recorded |

Synchronize only at declared dependency boundaries. Do not claim that work can proceed in parallel when it relies on the same unresolved runtime, unapproved external action, or overlapping source files.

## Current operating baseline — 2026-08-05

This snapshot reflects [CURRENT_STATE.md](CURRENT_STATE.md) and [TASK_QUEUE.md](TASK_QUEUE.md) at document creation. It is a **fact** only to the extent those sources remain current; replace it during the next daily update.

- **Yesterday's output:** no verified prior-day delivery is recorded in the current state. The operating-system baseline and the unsupported Python 3.9.6 test-collection failure are recorded in [MEMORY.md](MEMORY.md).
- **Top priority:** `S0-E2`, provision and document Python 3.10+ and establish a trustworthy full-suite baseline. It is blocked on runtime authority/environment.
- **Parallel work:** Track A is constrained by the runtime baseline. Track B and Track C may prepare internal, evidence-scoped workflow and positioning hypotheses only after they are defined as bounded proposals; they must not be represented as approved queue work yet.
- **Blocker:** Python 3.9.6 cannot collect tests for a repository requiring Python 3.10+; do not reinterpret this as a product or research result.
- **Week shipping target (proposal):** a reproducible supported-runtime test-baseline report with limitations and next verification task. **Non-goal:** claiming integration or scientific capability before the baseline exists.
- **Value:** resolving S0-E2 improves scientific trustworthiness (reproducible evaluations), product reliability (a testable platform), and long-term learning (credible evidence on which future research/product choices can rest).

## Daily brief template

```md
# PMO Daily Brief — YYYY-MM-DD

**Prepared at:** <time and timezone>
**Evidence window:** <commits, CI/test runs, benchmark artifacts, decision records reviewed>
**Operating horizon:** <ROADMAP horizon>

## 1. Yesterday's verified output

| Type | Fact | Evidence / artifact | Result and limitation |
|---|---|---|---|
| Commit / test / experiment / decision | <fact, not interpretation> | <hash, path, run link, or record> | <outcome; unknowns> |

## 2. Today's top five priorities

| Rank | Track | Queue ID or proposal | Owner | Dependency | Acceptance signal | Why now | Scientific / product / long-term value |
|---:|---|---|---|---|---|---|---|
| 1 | A/B/C | <ID> | <owner> | <dependency> | <observable result> | <ranking evidence> | <one sentence> |

## 3. Parallel workstreams

| Workstream | Owner | Inputs | Mutable paths | Acceptance signal | Stop condition | Handoff |
|---|---|---|---|---|---|---|
| <track/outcome> | <owner> | <inputs> | <exclusive paths> | <signal> | <condition> | <record location> |

## 4. Blockers and decisions needed

| Blocker | Affected work | Evidence | Required authority | Safe workaround | Review time |
|---|---|---|---|---|---|
| <blocker> | <task> | <artifact> | <human/team> | <independent work> | <date/time> |

## 5. Week shipping target

- **Target:** <one bounded outcome>
- **Evidence threshold:** <test, benchmark, review, or observed user signal>
- **Non-goal:** <what will not be claimed or attempted>

## 6. End-of-day reconciliation

- **Completed / not completed:** <acceptance signal and evidence>
- **Queue/state/roadmap changes:** <paths and reason, or none>
- **Memory/knowledge updates:** <paths and reason, or none>
- **Next first unblocked task:** <ID and rationale>
```
