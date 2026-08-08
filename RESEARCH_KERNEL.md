# AXIOM Research Kernel

The Research Kernel is the permanent execution engine for every research workflow in AXIOM. It orchestrates goal decomposition, planning, evidence acquisition, multi-agent execution, verification, memory, reflection, learning, benchmarking, and report generation through a stable 10-stage pipeline.

## Architecture Position

```
Domain Plugins (math, CS, VLSI)
        ↓
Research Kernel (10-stage pipeline)
        ↓
┌───────┴───────┬───────────┬──────────┐
│     ACA       │    SME    │ Workflow │
│ (reasoning)   │ (method)  │ (agents) │
└───────┬───────┴───────────┴──────────┘
        ↓
   H1-OBS Provenance
```

The kernel does not reimplement cognitive, scientific, or workflow logic. Each stage delegates to existing subsystems via thin adapters (see `KERNEL_ARCHITECTURE.md`).

## Ten Kernel Stages

| # | Stage | Primary Delegation |
|---|-------|-------------------|
| 1 | Goal Decomposition | Domain plugin + ACA perception |
| 2 | Research Planning | Domain plugin + SME session + ACA planning |
| 3 | Evidence Acquisition | Domain plugin + EGS |
| 4 | Multi-Agent Orchestration | Workflow scheduler |
| 5 | Verification Pipeline | Domain plugin + SMT + truthfulness |
| 6 | Memory Integration | Working memory + SME memory |
| 7 | Reflection | ACA reflection layer |
| 8 | Learning | Self-improvement loop |
| 9 | Benchmark Execution | Domain plugin benchmarks |
| 10 | Report Generation | Kernel reports + domain plugin |

## Domain Demonstrations

Three built-in plugins demonstrate the kernel without architectural changes:

| Plugin | Domain | Example Objective |
|--------|--------|-------------------|
| `mathematics` | Mathematics | Prove sum(1..n) = n(n+1)/2 |
| `computer_science` | Computer Science | Design O(n log n) sorting with proof |
| `vlsi_hardware` | VLSI / Hardware | 4-bit adder at 500 MHz, 28nm |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kernel/manifest` | GET | Full kernel manifest |
| `/kernel/stages` | GET | List 10 stages |
| `/kernel/plugins` | GET | List registered plugins |
| `/kernel/plugins/{id}` | GET | Plugin detail + benchmarks |
| `/kernel/runs` | POST | Create research run |
| `/kernel/runs/{id}/run` | POST | Execute full 10-stage cycle |
| `/kernel/runs/{id}/report` | GET | Generated research report |

## Usage

```python
from axiom.research_kernel import ResearchKernel

engine = ResearchKernel("axiom.db")
run = engine.create_run(
    objective="Prove sum(1..n) = n(n+1)/2",
    plugin_id="mathematics",
)
completed = engine.run_full_cycle(run.run_id)
print(completed.report)
```

## Benchmark

```bash
make kernel-benchmark
```

Runs all three domain plugins through the full 10-stage pipeline. Results written to `kernel_benchmark_results.json`.

## Package Layout

```
axiom/research_kernel/
  engine.py          # ResearchKernel orchestrator
  pipeline.py        # Stage executor (delegates to subsystems)
  plugin.py          # ResearchDomainPlugin protocol
  registry.py        # Plugin registry + manifest
  models.py          # KernelRun, KernelStage
  store.py           # SQLite persistence
  reports.py         # Report generation
  plugins/           # Built-in domain plugins
```

## Recommended Kernel Improvements

1. **Async stage execution** — Run independent stages (evidence + orchestration planning) concurrently when dependencies allow.
2. **Plugin hot-reload** — Load domain plugins from entry points without restart.
3. **RVP integration** — Wire benchmark stage to Research Validation Program known-answer dataset for cross-domain scoring.
4. **SME full-cycle coupling** — Optionally run full SME 10-phase cycle in parallel with kernel stages for deeper scientific rigor.
5. **Workflow worker binding** — Execute scheduled tasks via real workflow workers instead of schedule-only planning.
6. **Cross-run learning** — Persist kernel learning records and feed into self-improvement prioritization.
7. **Evidence tier enforcement** — Gate report publication on minimum evidence tier per domain contract.
8. **Human-in-the-loop gates** — Integrate SME human_review phase as optional kernel stage checkpoint.
