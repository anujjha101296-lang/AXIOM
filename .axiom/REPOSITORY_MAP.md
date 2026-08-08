# Repository Map

Conceptual organization for the AXIOM Continuous Evolution Loop, mapped to actual repository paths. This is a **navigation guide**, not a mandate to relocate code.

## Conceptual Structure → Repository Paths

| Concept | Purpose | Repository location |
|---------|---------|---------------------|
| **/product** | User-facing workflows and UI | `ui/`, `axiom/research/`, `axiom/services/api_gateway/` |
| **/research** | Scientific method, campaigns, reasoning | `axiom/grand_challenge/`, `axiom/core/reasoning/`, `axiom/mip/`, `axiom/research/` |
| **/benchmarks** | Capability measurement | `axiom/evaluation/`, `scripts/run_*_benchmark.py`, `*_benchmark_results.json` |
| **/campaigns** | Long-term research programs | `axiom/grand_challenge/`, `GRAND_CHALLENGE_PROGRAM.md`, `CHALLENGE_REGISTRY.md` |
| **/experiments** | Bounded research units | GCP `ExperimentRecord`, SME sessions (when merged), `axiom/workflow/demos/` |
| **/reports** | Research and capability outputs | `docs/`, `*_HEALTH.md`, `RESEARCH_VALIDATION.md`, campaign journals |
| **/knowledge** | Epistemic graph and ontology | `axiom/core/knowledge_graph/`, `axiom/mip/knowledge/` |
| **/memory** | Organizational learning | `.axiom/MEMORY.md`, `axiom/core/memory/`, `axiom/mip/memory/` |
| **/reasoning** | Hypothesis, MCTS, symbolic | `axiom/core/reasoning/`, `axiom/core/symbolic/`, `axiom/mip/conjecture/` |
| **/verifier** | Formal and heuristic verification | `axiom/core/verification/`, `axiom/mip/formal/` |
| **/runtime** | Execution engines | `axiom/workflow/`, `axiom/grand_challenge/engine.py`, `axiom/research_kernel/` (when merged) |
| **/docs** | Architecture and contracts | `.axiom/`, root `*.md`, `docs/` |
| **/tests** | Regression and truthfulness gates | `tests/` |
| **/releases** | Versioned artifacts | `CHANGELOG` (when present), git tags, PRs |

## Operating System Documents

| Path | Layer |
|------|-------|
| `.axiom/CONSTITUTION.md` | All layers — authority |
| `.axiom/OPERATING_SYSTEM.md` | Master loop |
| `.axiom/CURRENT_STATE.md` | Layer 2 entry point |
| `.axiom/TASK_QUEUE.md` | Layer 2 task selection |
| `.axiom/ROADMAP.md` | Layer 1 long-term direction |
| `.axiom/CAPABILITIES.md` | Layer 5 capability inventory |
| `.axiom/NORTH_STAR_METRICS.md` | Layer 5 measurement |
| `.axiom/MEMORY.md` | Layer 6 organizational memory |
| `.axiom/KNOWLEDGE_GRAPH.md` | Layer 6 evidence graph |
| `GRAND_CHALLENGE_PROGRAM.md` | Layer 7 campaigns |
| `READINESS_GATES.md` | Layer 7 tier gates |

## Governance Stack (Feature Branches → Future Main)

When merged, the execution stack layers as:

```text
Grand Challenge Program     (what campaigns to run)
        ↓
Research Kernel             (how to execute research)
        ↓
Scientific Method Engine    (how to research scientifically)
        ↓
Cognitive Architecture    (how to reason)
        ↓
Workflow Engine             (how to coordinate agents)
        ↓
H1-OBS Provenance           (what happened — audit trail)
```

On current `main`: GCP, SCEP, workflow, and research workspace are active. Kernel, SME, ACA, and H1-OBS exist on feature branches.

## Data Directories

| Path | Contents |
|------|----------|
| `data/research_uploads/` | User-uploaded PDFs |
| `axiom.db` / configured `DB_PATH` | SQLite stores (campaigns, eval, graph, research) |
| `docs/capability_delta_*.md` | SCEP run deltas (milestone commits only) |

## Entry Points for Workers

| Role | Start here |
|------|------------|
| Cursor agent | `AGENTS.md` → `.axiom/OPERATING_SYSTEM.md` |
| Engineer | `.axiom/ENGINEERING.md` |
| Researcher | `.axiom/RESEARCH.md` + `GRAND_CHALLENGE_PROGRAM.md` |
| PMO | `.axiom/PMO.md` |
| Strategist | `.axiom/templates/MONTHLY_STRATEGIC_REVIEW.md` |
