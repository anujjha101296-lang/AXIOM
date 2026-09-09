# AXIOM Technical Evolution

## Objective

Evolve AXIOM from a broad research-platform codebase into an evidence-first scientific intelligence system. The architecture must make it easy to add models and scientific domains without allowing model output to become scientific evidence by itself.

## 1. System boundaries

```text
User / API / UI
      |
      v
Research Orchestrator
      |
      +--> Planner / specialist agents
      |
      +--> Scientific tool registry
      |       +--> numerical solvers
      |       +--> symbolic algebra
      |       +--> theorem provers
      |       +--> data analysis
      |
      +--> Evidence pipeline
              +--> provenance
              +--> reproducibility
              +--> independent checks
              +--> claim/evidence graph
```

The scientific tool layer is deterministic wherever possible. Agents can select tools, propose hypotheses, and interpret outputs, but they cannot directly manufacture a verified claim.

## 2. Agent architecture

Start with one orchestrator and add specialists only when an evaluation demonstrates value.

- Research Director: decomposes a question and controls the run budget.
- Knowledge Agent: retrieves sources and extracts candidate claims.
- Mathematics Agent: derives equations, assumptions, and symbolic checks.
- Hypothesis Agent: proposes falsifiable hypotheses and alternative explanations.
- Experiment Designer: converts hypotheses into bounded executable plans.
- Simulation Agent: invokes allowlisted scientific tools.
- Analysis Agent: computes observables and uncertainty summaries.
- Scientific Critic: searches for invalid inference, instability, missing controls, and unsupported claims.
- Verification Agent: invokes independent numerical, symbolic, SMT, or formal verification paths.

The default execution model is a state machine rather than unconstrained agent-to-agent conversation.

## 3. Scientific state machine

```text
PLANNED
  -> HYPOTHESIS
  -> DESIGNED
  -> EXECUTED
  -> CRITIQUED
       | accepted
       v
    VERIFIED -> COMPLETED
       |
       | rejected
       v
   REPEATING -> DESIGNED

Any unsafe/invalid execution -> FAILED
```

Every transition becomes an immutable research event. A run has explicit budgets for experiment count, runtime, parameter ranges, and allowed tools.

## 4. Evidence model

AXIOM uses an epistemic ladder:

1. `GENERATED` — model or human proposal.
2. `NUMERICAL_OBSERVATION` — measured computational output.
3. `NUMERICALLY_ROBUST` — output survives declared sensitivity/convergence tests.
4. `INDEPENDENTLY_CHECKED` — an independent computational path agrees within declared tolerance.
5. `SYMBOLICALLY_VERIFIED` — symbolic system validates the relevant transformation/property.
6. `FORMALLY_VERIFIED` — a proof assistant or sound formal checker verifies the claim.

A lower tier may never be silently upgraded to a higher tier.

## 5. Data architecture

PostgreSQL is the intended durable system of record.

Core entities:

- `research_projects`
- `research_runs`
- `research_events`
- `research_questions`
- `hypotheses`
- `experiment_plans`
- `experiments`
- `evidence_records`
- `verification_records`
- `claims`
- `sources`
- `artifacts`
- `agent_runs`

Use JSONB for evolving scientific metadata and normalized relational fields for identities, ownership, status, timestamps, and query-critical attributes. pgvector is an optional retrieval index, not the source of truth.

## 6. Provenance contract

Every evidence record should identify:

```text
question
hypothesis
experiment_id
code_version
code_digest
parameters
initial_conditions
dataset_digest
runtime_environment
software_versions
random_seed
solver
numerical_tolerances
execution_timestamp
artifact_digests
verification_result
evidence_tier
```

The goal is that an independent researcher can reproduce a result without trusting AXIOM's narrative.

## 7. Backend

FastAPI remains the API boundary during the two-month build.

Required API capabilities:

- create/start/resume/cancel research run
- stream run events
- inspect experiment
- retrieve evidence
- retrieve provenance
- download reproducible report
- compare runs
- execute fixed benchmark

Long-running scientific work should move behind a job boundary as soon as persistence is introduced. The HTTP request should not become the execution state.

## 8. Frontend

The primary object is a **Research Run**, not a chat transcript.

The workspace should expose:

- question and assumptions
- hypothesis cards
- experiment timeline
- live execution state
- plots and numerical tables
- critic findings
- verification status
- evidence tier
- provenance inspector
- claim/evidence graph
- reproducibility/export controls

A chat panel can remain as a secondary interaction surface.

## 9. Agent/model providers

Provider neutrality is required.

```text
AXIOM Agent Contract
       |
       +-- local Ollama
       +-- OpenAI Agents SDK
       +-- future providers
```

Changing the model provider must not change scientific tool semantics or evidence rules.

## 10. Observability

Track at least:

- research run duration
- experiments/run
- accepted vs rejected experiments
- critic rejection reasons
- verification pass rate
- reproducibility pass rate
- model latency
- model token/cost usage when applicable
- scientific tool latency
- failure rate
- human intervention rate
- benchmark score

The most important product metric is **verified scientific progress per unit of researcher time**.

## 11. Security

Scientific execution must be treated as untrusted-code execution.

- allowlisted tools
- resource limits
- no arbitrary network access by default
- isolated execution environment
- bounded filesystem access
- explicit human approval for external/irreversible actions
- secret isolation
- audit trail for tool calls

## 12. Evaluation strategy

Every new capability needs a benchmark before it is called an improvement.

For each task record:

- baseline LLM-only result
- AXIOM result
- tool-assisted result
- verification status
- reproducibility status
- failure mode
- human evaluation when relevant

The benchmark should reward correct, reproducible scientific progress rather than fluent prose.

## 13. Build order

1. deterministic scientific runtime
2. evidence/provenance contract
3. bounded research state machine
4. benchmark harness
5. durable run/event storage
6. agent adapters
7. streaming backend
8. evidence-first UI
9. multi-domain scientific tools
10. external expert evaluation

Do not reverse this order by building a polished agent UI before the evidence loop works.
