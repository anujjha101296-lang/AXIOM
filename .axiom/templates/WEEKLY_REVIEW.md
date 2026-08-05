# AXIOM Weekly Operating Review Template

Use this template after each operating week or material milestone. Read [../CONSTITUTION.md](../CONSTITUTION.md), [../PMO.md](../PMO.md), [../CURRENT_STATE.md](../CURRENT_STATE.md), [../TASK_QUEUE.md](../TASK_QUEUE.md), [../ROADMAP.md](../ROADMAP.md), [../DECISION_FRAMEWORK.md](../DECISION_FRAMEWORK.md), [../CAPABILITIES.md](../CAPABILITIES.md), [../KNOWLEDGE_GRAPH.md](../KNOWLEDGE_GRAPH.md), and [../MEMORY.md](../MEMORY.md) first.

Do not replace current operational state with this template. Report only verified results, label proposals and assumptions, and append enduring decisions and learning to `MEMORY.md`.

```md
# AXIOM Weekly Operating Review — Week of YYYY-MM-DD

**Review owner:** <name/team>
**Evidence reviewed:** <commits, test/benchmark outputs, research artifacts, approved user evidence>
**Horizon:** <roadmap horizon>

## Executive result

- **Week shipping target:** <target from last review>
- **Outcome:** met / partially met / not met / invalidated
- **Evidence:** <artifact links>
- **Confidence and limitations:** <what this result does not establish>

## Track review

| Track | Intended outcome | Verified output | Evidence quality | Learning | Decision: scale / revise / kill / park |
|---|---|---|---|---|---|
| A — Research | <outcome> | <result> | <tier> | <learning> | <decision> |
| B — Product | <outcome> | <result> | <tier> | <learning> | <decision> |
| C — Company | <outcome> | <result> | <tier> | <learning> | <decision> |

## Capability and trust review

| Capability or claim | Prior maturity / status | Current evidence | Change justified? | Limitation / next proof point |
|---|---|---|---|---|
| <capability> | <status> | <artifact> | yes / no | <limit> |

## Delivery, quality, and risk

| Area | Signal | Evidence | Risk | Owner and action |
|---|---|---|---|---|
| Build/test reliability | <signal> | <run> | <risk> | <action> |
| Security / integrity | <signal> | <review> | <risk> | <action> |
| Documentation / operability | <signal> | <artifact> | <risk> | <action> |

## Decisions and kill list

| Item | Alternatives considered | Evidence | Decision | Review date | Required record updates |
|---|---|---|---|---|---|
| <item> | <alternatives> | <evidence> | <decision> | <date> | <MEMORY / KNOWLEDGE_GRAPH / queue / roadmap> |

## Next week

1. **Week shipping target:** <one bounded outcome>
2. **Top five ranked priorities:** <queue IDs or explicitly marked proposals with acceptance signals>
3. **Parallel workstreams:** <owners, dependencies, exclusive paths, synchronization points>
4. **Human decisions required:** <approval needed; no external action before approval>
5. **First unblocked task:** <ID and reason>

## Required reconciliation

- [ ] `CURRENT_STATE.md` reflects verified completions, blockers, and the current first priority.
- [ ] `TASK_QUEUE.md` contains only acceptance-defined, dependency-aware ranked work.
- [ ] `ROADMAP.md` changed only where evidence altered an outcome or sequence.
- [ ] `MEMORY.md` has append-only records for enduring decisions, failures, experiments, and evidence.
- [ ] `KNOWLEDGE_GRAPH.md` links material claims, artifacts, and dependencies with provenance.
- [ ] Changes are tested where applicable and committed in focused units.
```
