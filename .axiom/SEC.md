# Scientific Experimentation & Compute Loop (SEC)

AXIOM treats computation as an instrument of research — not as mathematical proof or established scientific fact.

## Mission

Build a secure, reproducible, scalable experimentation system for investigating scientific hypotheses through computation.

## Continuous loop

```text
RESEARCH QUESTION → HYPOTHESIS → EXPERIMENT DESIGN → RESOURCE ESTIMATION
  → SANDBOXED EXECUTION → RESULT → REPRODUCTION → ANALYSIS
  → EVIDENCE UPDATE → KNOWLEDGE UPDATE → HYPOTHESIS UPDATE → NEXT EXPERIMENT
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `EXPERIMENT_ENGINE.md` | Experiment kernel status |
| `COMPUTE_RUNTIME.md` | Runtime and environments |
| `EXPERIMENT_SPEC.md` | Declarative experiment spec |
| `REPRODUCTION_GUIDE.md` | Reproduction procedures |
| `EXPERIMENT_SECURITY.md` | Sandbox and security |
| `COMPUTE_BENCHMARKS.md` | Benchmark categories |
| `scripts/sec_health_check.py` | Automated SEC gate |

## Code modules

- `axiom/experiment/models.py` — lifecycle, specs, budgets
- `axiom/experiment/store.py` — versioned experiment store
- `axiom/experiment/sandbox.py` — isolated code execution
- `axiom/experiment/executor.py` — full lifecycle execution
- `axiom/experiment/integrity_gate.py` — scientific integrity gate
- `axiom/experiment/reproduction.py` — reproduction comparison
- `axiom/experiment/plugins.py` — domain plugins (VLSI stub)
- `axiom/services/api_gateway/routes/experiment_api.py` — `/experiments/*` API

## Evidence classification

Computational evidence is explicitly labeled:
- `computational_evidence` — NOT mathematical proof
- `not_scientific_fact` — requires verification for claims

## Constraints

- Never execute generated code with unrestricted privileges
- Never allow experiments to silently disappear
- Never confuse computation with proof
- Budget exceeded → STOP, PRESERVE STATE, REPORT

## Production requirements

```bash
REQUIRE_AUTH_FOR_EXPERIMENT_ROUTES=true
```

## Integration

- **E&R** — experiment records, counterexample triggers
- **SIMR** — compute tool routing
- **TSS** — sandbox security
- **H1-OBS** — run provenance
- **FMTP** — computational vs formal separation
