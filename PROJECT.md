# Project: AXIOM (AI Scientific Discovery Platform)

## Architecture
AXIOM is an AI Scientific Discovery Platform structured into modular Python core packages, FastAPI service gateway, and Next.js React spatial canvas UI.
- `axiom/core/knowledge_graph`: SQLite Relational Store, NetworkX cycle detection DAG guard, Pydantic node/edge schema models (R4 - EGS).
- `axiom/core/parser`: LaTeX AST parser, math environment extraction (>95%), BibTeX citation resolution (R1 - EIE).
- `axiom/core/exporter`: Lean 4 AST exporter, formal expression translator, Lean source code renderer (R2 - LRK).
- `axiom/core/verification`: SMT / Z3 solver gateway (<60s parameter sweep counterexample detection) & Lean 4 compiler proof checker (R3 - AVT).
- `axiom/core/discovery`: MCTS proof search engine (UCT selection, tactic expansion) & autonomous discovery loop (R5 - DRSP).
- `axiom/services/api_gateway`: FastAPI REST endpoints and WebSocket live streaming server (R1-R6).
- `ui/`: Next.js 14 Spatial Canvas frontend application with interactive React Flow graph visualizer (R6 - UI).

## Feature Inventory
Every requirement feature mapped to its assigned milestone and source:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | SQLite Graph Relational Storage & Schema | Relational SQLite database (`nodes`, `edges`, `verification_records`), indexes, CRUD operations | M1 | survey |
| 2 | Circular Dependency Guard | NetworkX DAG validation preventing cycles in logical edges (`PROVES`, `EXTENDS`, `USES_METHOD`) | M1 | survey |
| 3 | LaTeX AST Math & Citation Ingestion | LaTeX AST parser extracting >95% math environments (`theorem`, `lemma`, etc.) and citation keys | M1 | survey |
| 4 | Epistemic JSON Graph Serializer | Transform parsed papers into structured epistemic node-edge JSON payload (`IngestedPaperGraphPayload`) | M1 | survey |
| 5 | LaTeX-to-Lean 4 AST Exporter | Convert parsed math claims to compilable Lean 4 theorem declarations (0 syntax errors) | M2 | survey |
| 6 | SMT / Z3 Counterexample Gateway | Parameter sweeps seeking counterexamples for invalid claims within <60s | M2 | survey |
| 7 | Lean 4 Compiler Proof Checker | Subprocess compiler runner verifying 0 error proofs without `sorry` | M2 | survey |
| 8 | MCTS Proof Search Engine | UCT tactic exploration for simple algebra lemmas (e.g., `a + b = b + a`) | M3 | survey |
| 9 | Autonomous Discovery Loop | Background cycle evaluating candidate claims & registering verified proofs | M3 | survey |
| 10 | Spatial Canvas Next.js Frontend | Next.js/React node-link UI visualizing knowledge graph, proof lineage, and status colors | M4 | survey |
| 11 | FastAPI Graph & Proof API Gateway | REST & WebSocket streaming endpoints linking UI canvas to Python core services | M4 | survey |

## Code Layout
- `axiom/core/knowledge_graph/`: `db.py`, `schema.py`
- `axiom/core/parser/`: `latex_ast_parser.py`, `arxiv_parser.py`, `semantic_tracker.py`
- `axiom/core/exporter/`: `lean_ast.py`, `lean_exporter.py`
- `axiom/core/verification/`: `smt_gateway.py`, `lean_checker.py`, `verification_orchestrator.py`
- `axiom/core/discovery/`: `mcts_engine.py`, `tactics.py`, `discovery_loop.py`
- `axiom/services/api_gateway/`: `main.py`, `auth.py`, `routes.py`
- `ui/`: Next.js App Router application (`package.json`, `src/app/page.tsx`, `src/components/SpatialCanvas.tsx`)
- `tests/`: `test_parser.py`, `test_exporter.py`, `test_verification.py`, `test_graph_store.py`, `test_mcts.py`, `test_api.py`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Graph Store & Ingestion (EGS & EIE) | SQLite store, cycle detection, LaTeX AST parser, ingestion API | none | PLANNED |
| 2 | M2: Logical Exporter & Verification (LRK & AVT) | Lean 4 AST exporter, SMT/Z3 counterexample gateway, Lean checker | M1 | PLANNED |
| 3 | M3: MCTS Proof Search & Discovery (DRSP) | MCTS tactic search engine, autonomous discovery loop | M2 | PLANNED |
| 4 | M4: Spatial Canvas UI & API Integration (UI) | Next.js spatial canvas, REST & WebSocket streaming endpoints | M3 | PLANNED |

## Interface Contracts

### EIE ↔ LRK
- `ParsedMathExpression` -> `LeanTheoremAST`
- Input: Parsed LaTeX AST expressions and variables
- Output: `LeanTheoremAST(name, variables, hypotheses, target_goal, proof_script)`

### LRK ↔ AVT
- `LeanTheoremAST.render()` -> `LeanCompileRequest` -> `LeanCompileResponse`
- Output: `{ is_valid: bool, status_code: str, errors: List[LeanCompileError], execution_time_ms: int }`

### EGS ↔ AVT
- `SMTCheckRequest(claim_id, variables, assumptions, conjecture_negation, timeout_ms=60000)` -> `SMTCheckResponse`
- Saves result into `verification_records` table in SQLite DB. Updates node `status` to `VERIFIED` or `REFUTED`.

### DRSP ↔ AVT
- MCTS search node goal state -> Lean compiler invocation -> score reward update $Q(s, a)$.

### EGS ↔ UI
- `GET /api/v1/graph/spatial` -> `SpatialGraphDataResponse(nodes: SpatialNode[], edges: SpatialEdge[])`
- Node status colors: Green (`#22c55e`) for `VERIFIED`, Amber (`#f59e0b`) for `CONJECTURED`, Red (`#ef4444`) for `REFUTED`.
