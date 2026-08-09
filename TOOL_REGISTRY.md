# Tool Registry

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Categories

| Category | Tools |
|----------|-------|
| Literature | `literature_search`, `vector_retrieval` |
| Knowledge | `knowledge_graph` |
| Computation | `python_exec`, `sympy_engine` |
| Verification | `smt_gateway`, `lean_exporter` |
| Benchmark | `scep_benchmarks`, `eval_api` |
| Reasoning | `hypothesis_engine` |
| Orchestration | `workflow_engine`, `worker_*` |
| Observability | `provenance_records` |

## Tracked attributes

Capabilities, inputs, outputs, risk class (TSS), cost estimate, latency, reliability, verification level, security level.

## API

```bash
GET /routing/tools
GET /routing/tools/{tool_id}
```

## Refresh

```bash
make simr-health
```
