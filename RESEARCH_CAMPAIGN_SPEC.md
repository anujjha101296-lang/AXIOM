# Research Campaign Specification

## Campaign object

```text
Campaign
├── Objective, Problem Definition, Domain, Difficulty
├── Ladder Level (0–9), Success Criteria, Constraints
├── Phase (state machine)
├── Contribution Level (graduated, not binary)
├── Resource Budget (time, compute, model/tool calls, exploration fraction)
├── Research Graph (nodes: problems, lemmas, hypotheses, experiments)
├── Strategies (competing approaches with scores)
├── Hypotheses (linked to E&R claims)
├── Cycles (iteration records)
├── Checkpoints (immutable snapshots)
├── Human Gates (pending review triggers)
├── Memory (institutional learnings)
├── Journal & Decisions
└── Cross-loop IDs (experiments, claims, proofs, GCP)
```

## State machine

```text
PROPOSED → SCOPED → RESEARCHING → HYPOTHESIS_GENERATION → INVESTIGATION
  → VERIFICATION → REVIEW → (CONTINUE | PIVOT) → RESEARCHING

Terminal: SUCCESSFUL_CONTRIBUTION | PARTIAL_PROGRESS | EXHAUSTED | BLOCKED
          DISPROVED | ABANDONED | PAUSED
```

## Research graph node fields

- `node_id`, `node_type`, `title`
- `status`, `confidence`
- `dependencies`, `evidence_ids`
- `owner_role`, `next_action`
- `provenance`, `metadata`

## Contribution levels (ordered)

`no_progress` → `useful_observation` → `new_conjecture` → `counterexample`
→ `new_lemma` → `verified_lemma` → `partial_theorem` → `new_method`
→ `published_contribution` → `major_breakthrough` → `potential_complete_solution`

## Human gate triggers

- Novel claim
- Evidence conflict
- Major direction change
- Formal proof success
- Counterexample found
- Potential contribution
- Resource threshold exceeded
- External publication request
