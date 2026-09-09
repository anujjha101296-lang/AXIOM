# AXIOM — Two-Month Founder Build Plan

**Horizon:** 2026-09-09 → 2026-11-08  
**Constraint:** local/free first; paid compute or APIs are optional accelerators only.

## North-star demo

A user gives AXIOM a bounded scientific question. AXIOM turns it into a falsifiable hypothesis, selects executable experiments, runs deterministic simulations, records provenance, challenges the result, and produces a report whose claims are explicitly limited by evidence.

## Weeks 1–2 — Scientific runtime
- Freeze the evidence taxonomy: generated / numerical observation / independently checked / formally verified.
- Build experiment registry and immutable run records.
- Finish Lorenz benchmark with parameter sweep, perturbation tests, timestep sensitivity, and convergence checks.
- Add reproducible report generation.
- Acceptance: same inputs reproduce the same experiment record and no numerical observation is labelled proof.

## Weeks 3–4 — Agentic research loop
- Add local Ollama planner.
- Add planner → experiment designer → executor → critic state machine.
- Add structured research plans and falsifiers.
- Add failure/retry policy and budget limits.
- Acceptance: the system can autonomously choose the next bounded experiment from a finite candidate set.

## Weeks 5–6 — Scientific breadth + benchmark
- Double pendulum, Lorenz, Lotka–Volterra, coupled oscillators.
- Add symbolic checks with existing SymPy/Z3 capabilities.
- Add independent numerical verification paths.
- Create AXIOM Scientific Intelligence Benchmark v0.1.
- Acceptance: benchmark reports quantitative scores, failure cases, and reproducibility metadata.

## Weeks 7–8 — Product + founder evidence
- Research workspace integrates question → run → evidence → report.
- Create researcher-facing demo and 5-minute walkthrough.
- Prepare 50 expert discovery conversations.
- Package technical architecture, benchmark, limitations, and non-claims.
- Acceptance: a researcher can reproduce a result without trusting AXIOM's prose.

## Parallel company track

Every week also produces one artifact in each lane:

- **Research:** benchmark/evidence.
- **Product:** researcher workflow improvement.
- **Company:** customer interview, competitive evidence, or grant/accelerator research.

## Hard rules

- No generic chatbot positioning.
- No claim of autonomous scientific discovery without external validation.
- No paid infrastructure dependency.
- No irreversible product or company decision without recorded evidence.
- Human approval remains required for spending, production deployment, external publication/communication, and legal claims.

## Day-60 decision gate

Continue aggressively only if the evidence supports all three:

1. AXIOM executes a genuinely useful scientific workflow end-to-end.
2. Independent users prefer it to their current workflow for at least one bounded task.
3. The benchmark shows measurable capability beyond a plain LLM + scripts baseline.
