# Frontier Research Campaign Engine (FRCE)

AXIOM's orchestration layer that turns individual research loops into a **research organization capable of pursuing problems for days, weeks, or months**.

## Mission

Connect Research Kernel, SIMR, FMTP, SEC, E&R, GCP, Security, and Memory into a unified long-running research mission system. AXIOM continuously decides whether the plan is still worth pursuing.

## Continuous loop

```text
RESEARCH OBJECTIVE → DEFINE & SCOPE → BUILD KNOWLEDGE → DECOMPOSE PROBLEM
  → GENERATE STRATEGIES → PARALLEL RESEARCH (Literature / Compute / Formal)
  → COLLECT EVIDENCE → ATTACK RESULTS → UPDATE KNOWLEDGE → DECIDE NEXT ACTION
  → CHECKPOINT → HUMAN REVIEW → NEXT CYCLE
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `FRONTIER_CAMPAIGN_ENGINE.md` | Engine status and capabilities |
| `CAMPAIGN_ORCHESTRATION.md` | Loop integration architecture |
| `RESEARCH_CAMPAIGN_SPEC.md` | Campaign object specification |
| `RESEARCH_MEMORY.md` | Institutional memory contract |
| `CAMPAIGN_BENCHMARKS.md` | Benchmark categories |
| `scripts/frce_health_check.py` | Automated FRCE gate |

## Code modules

- `axiom/campaign/models.py` — campaign state machine, research graph, budgets
- `axiom/campaign/orchestrator.py` — main engine connecting all loops
- `axiom/campaign/graph.py` — problem decomposition and bottleneck detection
- `axiom/campaign/planner.py` — SIMR-integrated strategy generation
- `axiom/campaign/allocator.py` — exploit/explore resource allocation
- `axiom/campaign/pivot.py` — pivot mechanism after each cycle
- `axiom/campaign/gates.py` — human review gates
- `axiom/campaign/memory.py` — campaign and global memory compounding
- `axiom/campaign/ladder.py` — challenge ladder levels 0–9
- `axiom/services/api_gateway/routes/frce_api.py` — `/frce/*` API

## Integrated loops

| Loop | Role in campaigns |
|------|-------------------|
| **SIMR** | Strategy generation and model/tool routing |
| **SEC** | Sandboxed computational experiments |
| **FMTP** | Formalization and proof attempts |
| **E&R** | Claims, evidence, provenance |
| **GCP** | Challenge ladder and tier gates |
| **TSS** | Security constraints on execution |

## Principles

- **ABANDONED is not failure** — preserve everything learned
- **Earn ladder advancement through evidence** — levels 0–9
- **Computation ≠ proof** — computational evidence explicitly labeled
- **Human gates** for novel claims, counterexamples, formal proofs, major pivots
- **Controlled parallelism** — never unbounded agent spawning

## Production requirements

```bash
REQUIRE_AUTH_FOR_FRCE_ROUTES=true
```

## Next step

Select AXIOM's first real research campaign with benchmark, success criteria, and difficulty gate (GCP-2).
