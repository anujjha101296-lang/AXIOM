# Campaign Orchestration

How FRCE connects AXIOM's research loops.

## Architecture

```text
                    FRCE Orchestrator
                           │
     ┌─────────┬───────────┼───────────┬─────────┐
     ▼         ▼           ▼           ▼         ▼
   SIMR      SEC        FMTP        E&R       GCP
 (routing) (experiments) (formal)  (evidence) (ladder)
```

## Cycle execution

1. **Scope** — decompose problem into research graph nodes
2. **Plan** — `compile_research_plan()` generates competing strategies
3. **Allocate** — exploit/explore split across strategies (max 5 workers)
4. **Investigate** — parallel tracks:
   - Computational → SEC `execute_experiment()` (sandboxed)
   - Formal → FMTP `formalize_informal()`
   - Literature → observation recorded (v1 stub)
5. **Collect** — register claims and evidence in E&R
6. **Evaluate** — pivot decision (continue / pivot / escalate / pause / abandon)
7. **Checkpoint** — immutable snapshot
8. **Human gate** — if contribution threshold or formal proof trigger

## Cross-loop IDs

Campaigns maintain linkage:
- `experiment_ids` → SEC store
- `claim_ids` → E&R registry
- `proof_ids` → FMTP store
- `gcp_campaign_id` → GCP tier campaigns
- `routing_plan_id` → SIMR execution plan

## Security

All computational code runs through SEC sandbox — never in application process.
Campaign credentials do not inherit production secrets.
