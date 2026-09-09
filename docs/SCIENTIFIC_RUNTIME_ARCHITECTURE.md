# AXIOM Scientific Runtime Architecture

## Design rule

> Agents decide what to investigate; deterministic scientific systems decide what the evidence supports.

## Runtime contract

1. Accept a scientific question.
2. Produce one bounded structured hypothesis/experiment plan.
3. Validate all parameters against an allowlist and resource budget.
4. Execute only registered scientific tools.
5. Record immutable experiment inputs and outputs.
6. Critique evidence against explicit gates.
7. Verify with an independent computational path where possible.
8. Repeat only within the run budget.
9. Emit a reproducible report and machine-readable event stream.

## Persistence

The first persistence adapter is append-only JSONL because it works offline and
is trivial to inspect/replay. The stable event schema is designed for migration
to the existing SQLAlchemy/PostgreSQL layer. PostgreSQL should become the system
of record once concurrent research runs and team workloads require it.

## Agent providers

`ScientificPlanner` is provider-neutral. The deterministic planner is the offline
reference implementation. Ollama and OpenAI adapters can be plugged in without
changing scientific execution, evidence tiers, or verification semantics.

## Safety boundaries

- No unrestricted shell execution from an agent.
- No arbitrary network access from the scientific executor.
- Explicit experiment and runtime budgets.
- Numerical observations cannot be promoted to formal proofs.
- Human approval remains required for irreversible external actions.
