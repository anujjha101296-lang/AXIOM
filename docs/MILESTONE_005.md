# Milestone 005 — Autonomous Research Loop v1

**Status:** Complete  
**Version:** 0.3.0-research-loop  
**Tests:** 182/182 core pass (includes 16 research-loop tests)

## Summary

AXIOM's first closed-loop autonomous research system. Given a bounded research problem, the system decomposes, retrieves evidence, generates and ranks hypotheses, criticizes, verifies, records failures, replans across iterations, and produces an evidence-classified report.

**This is not a claim of autonomous scientific discovery.** The workflow executes with explicit `ClaimStatus` classification on every important output.

## Architecture Reused

| Component | Path | Role in loop |
|-----------|------|--------------|
| WorkflowEngine | `axiom/workflow/engine.py` | Workflow persistence, events, artifacts |
| ResearchStore | `axiom/research/store.py` | Literature evidence retrieval |
| SmtGateway | `axiom/core/verification/smt_gateway.py` | Bounded verification |
| truthfulness | `axiom/core/verification/truthfulness.py` | Evidence mode contract |
| HypothesisEngine | `axiom/core/reasoning/hypothesis_engine.py` | Available via registry (future wire) |
| Eval platform | `axiom/evaluation/*` | Benchmark scoring after runs |

## New Package: `axiom/research_loop/`

- `schema.py` — ResearchState, ClaimStatus, FailedAttemptRecord, BenchmarkScore
- `failure_memory.py` — Persistent failure fingerprints
- `benchmarks.py` — 4 historical problems with hidden solutions
- `roles.py` — 8 role specs with distinct responsibilities
- `engine.py` — ResearchLoopEngine orchestrator
- `workers/*` — 8 specialized role workers
- `store.py` — SQLite persistence

## API (`/research-loop/*`)

- `POST /research-loop/runs` — Create run
- `POST /research-loop/benchmarks/run` — Run historical benchmark
- `POST /research-loop/runs/{id}/start|pause|resume|cancel`
- `POST /research-loop/runs/{id}/approve` — Human approval gate
- `POST /research-loop/runs/{id}/hypotheses/{id}/reject`
- `POST /research-loop/runs/{id}/evidence` — Add human evidence
- `PUT /research-loop/runs/{id}/objective` — Change objective
- `GET /research-loop/runs/{id}` — Full inspectable state

Workflow router also mounted at `/workflows/*`.

## UI

`/research/runs` — Visual research run interface: objective, phase, workers, research tree, hypotheses, failures, timeline, final report.

## Historical Benchmarks

| ID | Problem | Hidden solution |
|----|---------|-----------------|
| `bench_sum_formula` | Sum 1+2+...+n | n(n+1)/2 |
| `bench_pythagorean_345` | 3²+4²=5² | Pythagorean triple |
| `bench_prime_infinitude` | Infinitely many primes | Euclid's proof |
| `bench_euler_polyhedra` | V, E, F relation | V-E+F=2 |

Solutions are hidden during execution; scoring compares final report against keywords after completion.

## Demo

```bash
bash scripts/demo_research_loop.sh
```

## Known Limitations

1. Workers use deterministic/heuristic logic, not full LLM reasoning (ModelClient not yet wired to loop workers)
2. Literature retrieval falls back to problem structure when no project documents exist
3. Semantic search not integrated — FTS only via ResearchStore when project_id provided
4. No WebSocket streaming — UI polls every 3s
5. Workflow router lacks auth dependency (research-loop routes are auth-protected)
6. Long-running loops (>20 iterations) not load-tested
7. Benchmark scoring is keyword-based, not formal proof checking

## Next Recommended Milestone

**H1-OBS** — Reproducible run/provenance records linking research loop inputs, config, evidence tier, and SCEP benchmark results.
