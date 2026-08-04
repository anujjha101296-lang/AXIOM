# AXIOM — System Architecture

## Overview

AXIOM (Autonomous eXploration of Ideas, Observations & Models) is a self-improving AI Scientific Discovery Platform structured as a Python monorepo with a Next.js frontend.

```
┌──────────────────────────────────────────────────────────────┐
│                      API Gateway (:8000)                      │
│            FastAPI  •  JWT Auth  •  RBAC  •  Metrics         │
└───────────┬──────────────────────────────────────────────────┘
            │
    ┌───────┴────────┐         ┌───────────────────┐
    │  Event Bus     │         │  Working Memory    │
    │  (async pub/   │         │  (session-scoped   │
    │   sub)         │         │   in-process)      │
    └───────┬────────┘         └───────────────────┘
            │
  ┌─────────┼──────────────────────────────────────────┐
  │         │                                          │
  ▼         ▼                                          ▼
EIE       MCTS/HYP                                   EGS
arXiv     Reasoning                             SQLite Graph
Parser    Engine                                    Store
  │         │                                          │
  │    ┌────┴───────┐                                  │
  │    │  SMT (Z3)  │                                  │
  │    │  Lean 4    │                                  │
  │    └────────────┘                                  │
  └───────────────────────────────────────────────────►│
                                                        │
                                                  NetworkX
                                                  Export
```

## Module Reference

| Module | Path | Purpose |
|:-------|:-----|:--------|
| **EGS** | `axiom/core/knowledge_graph/` | SQLite epistemic graph store |
| **EIE** | `axiom/core/parser/` | arXiv LaTeX ingestion |
| **MCTS** | `axiom/core/reasoning/mcts.py` | Monte Carlo Tree Search proof solver |
| **HYP** | `axiom/core/reasoning/hypothesis_engine.py` | Conjecture generation |
| **SIL** | `axiom/core/reasoning/self_improvement.py` | Autonomous sprint-review loop |
| **MEM** | `axiom/core/memory/working_memory.py` | Session working memory |
| **SMT** | `axiom/core/verification/smt_gateway.py` | Z3 SMT counterexample sweeps |
| **LRK** | `axiom/core/verification/lean_exporter.py` | Lean 4 proof exporter |
| **PRS** | `axiom/evaluation/prize_readiness.py` | Millennium Prize readiness scorer |
| **CFG** | `axiom/config/settings.py` | Pydantic settings (12-factor) |
| **OBS** | `axiom/observability/` | Structured logging + Prometheus metrics |
| **EVT** | `axiom/core/events/bus.py` | In-process async event bus |
| **API** | `axiom/services/api_gateway/main.py` | FastAPI REST gateway |
| **UI** | `ui/` | Next.js spatial canvas dashboard |

## Data Flow

### Ingest
```
POST /ingest → ArxivParser.parse_paper()
             → store.add_node(paper, claims, concepts)
             → event_bus.publish(Topics.PAPER_INGESTED)
```

### Verification
```
POST /verify/conjecture → SmtGateway.verify_modular_conjecture()
                        → store.add_node(claim, status=VERIFIED|REFUTED)

POST /verify/proof      → MctsSolver.solve()
                        → LeanExporter.export_theorem()
                        → store.add_node(claim, tier=TIER_2_PROVEN)
```

### Discovery
```
POST /hypothesize       → HypothesisEngine.generate()
                        → store.add_node(conjecture, status=CONJECTURED)
                        → working_memory.add_hypothesis()

POST /self-improve      → SelfImprovementLoop.run()
                        → roadmap.md (written to workspace)
```

## Configuration

All configuration is environment-variable driven (12-factor). See `.env.example`.

## Security

- **Authentication**: `Authorization: Bearer <token>` on all protected endpoints
- **RBAC**: Three roles — `ADMIN`, `RESEARCHER`, `READONLY`
- **Secrets**: Never committed — loaded from `.env` via Pydantic `BaseSettings`
- **Container**: Runs as non-root user `axiom`

## Database

SQLite with three tables (versioned migrations):
- `nodes` — all epistemic entities (polymorphic via JSON blob)
- `edges` — directed relationships between nodes
- `proof_lineage` — verification attempt history (v2)
- `memory_snapshots` — working memory persistence (v3)
- `_schema_migrations` — migration version tracking

## Monitoring

- **Metrics endpoint**: `GET /metrics` — Prometheus text format
- **Event log**: `GET /events` — recent event bus history
- **Prometheus**: scrapes `api:8000/metrics` every 15s
- **Grafana**: dashboards at `:3001` (admin/axiom-admin)
