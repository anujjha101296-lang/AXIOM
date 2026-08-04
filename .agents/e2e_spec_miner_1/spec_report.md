# AXIOM End-to-End Specification Mining Report

**Generated Date**: 2026-08-04  
**Agent**: E2E Spec Miner 1 (`e2e_spec_miner_1`)  
**Target Repository**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`  
**System Architecture**: AXIOM AI Scientific Discovery Platform (Epistemic Graph Store, LaTeX Parsing, Lean 4 / SMT Verification, MCTS Discovery, FastAPI Gateway, Next.js Spatial Canvas)

---

## 1. Overview & Test Invocation Infrastructure

### 1.1 Codebase Structure
The AXIOM platform consists of:
- **Core Engine Packages (`axiom/core/`)**:
  - `knowledge_graph/`: SQLite relational graph database (`db.py`), Pydantic domain schemas (`schema.py`).
  - `parser/`: arXiv LaTeX tarball parser (`arxiv_parser.py`), proof dependency & DAG cycle tracker (`semantic_tracker.py`).
- **Services Gateway (`axiom/services/`)**:
  - `api_gateway/`: FastAPI REST endpoints and authentication middleware (`main.py`, `auth.py`).
  - `model_gateway/`: LLM client wrapper with SQLite response caching (`client.py`).
- **Test Suite (`tests/`)**:
  - `test_epistemic_layer.py`: Tests for Pydantic schema models, SQLite persistence, NetworkX export, arXiv LaTeX parsing, proof citation resolution, circular dependency detection, and critical path analysis.
  - `test_api.py`: Tests for FastAPI health/readiness endpoints, Bearer authentication, and ModelClient SQLite caching.
- **Infrastructure**:
  - `pyproject.toml`: Poetry dependency file specifying dependencies (`fastapi`, `pydantic`, `networkx`, `sympy`, `pylatexenc`, `requests`, `uvicorn`, `pytest`).
  - `Dockerfile` & `docker-compose.yml`: Containerized setup running Uvicorn API gateway on port 8000.

### 1.2 Test Runners & Execution Instructions
Existing tests can be invoked via multiple methods depending on environment setup:

1. **Pytest (Standard Python Environment)**:
   ```bash
   python3 -m pytest -v tests/
   ```
   Or specific test modules:
   ```bash
   python3 -m pytest -v tests/test_epistemic_layer.py
   python3 -m pytest -v tests/test_api.py
   ```

2. **Poetry Runner**:
   ```bash
   poetry run pytest -v
   ```

3. **Docker Execution**:
   ```bash
   docker build -t axiom-api .
   docker run -p 8000:8000 axiom-api
   ```

---

## 2. Comprehensive Feature Specifications

---

### Feature 1: SQLite Graph Relational Storage & Schema
* **Category**: Knowledge Graph Store (EGS - M1)
* **Status**: Implemented (`axiom/core/knowledge_graph/schema.py`, `axiom/core/knowledge_graph/db.py`)
* **Module Entrypoint**: `axiom.core.knowledge_graph.db.EpistemicStore`

#### Data Models & Schemas (`schema.py`)
* **`NodeType` (Enum)**: `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`
* **`EdgeType` (Enum)**: `CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`
* **`EpistemicStatus` (Enum)**: `VERIFIED`, `CONJECTURED`, `REFUTED`, `UNDER_REVIEW`
* **`VerificationTier` (IntEnum)**:
  * `TIER_0_CONJECTURE = 0`
  * `TIER_1_SIMULATED = 1`
  * `TIER_2_PROVEN = 2`
  * `TIER_3_REPLICATED = 3`
* **`NodeBase` (BaseModel)**:
  * `id`: `str` (Unique hash or UUID)
  * `type`: `NodeType`
  * `name`: `str`
  * `metadata`: `Dict[str, Union[str, int, float, bool, List[str], None]]`
* **Specific Nodes**:
  * `AuthorNode`: `orcid` (Optional[str]), `affiliations` (List[str])
  * `PaperNode`: `doi` (Optional[str]), `arxiv_id` (Optional[str]), `abstract` (Optional[str]), `published_date` (Optional[str])
  * `ConceptNode`: `definition` (str), `mathematical_formulation` (Optional[str])
  * `MathematicalClaimNode`: `statement` (str), `formal_specification` (Optional[str]), `status` (EpistemicStatus, default `CONJECTURED`), `tier` (VerificationTier, default `TIER_0_CONJECTURE`)
  * `ExperimentalFactNode`: `fact_description` (str), `confidence_metric` (float, default 1.0), `status` (EpistemicStatus, default `UNDER_REVIEW`), `tier` (VerificationTier)
  * `DatasetNode`: `url` (Optional[str]), `size_bytes` (Optional[int])
* **`ScientificNode`**: Discriminated union of node models on `type`.
* **`Edge` (BaseModel)**:
  * `source_id`: `str`
  * `target_id`: `str`
  * `type`: `EdgeType`
  * `confidence`: `float` (default 1.0)
  * `provenance`: `Dict[str, Any]` (default `{}`)
* **`KnowledgeGraph` (BaseModel)**: `nodes: List[ScientificNode]`, `edges: List[Edge]`

#### Public API Contracts (`db.py`)
* **`EpistemicStore(db_path: str = ":memory:")`**:
  * Initializes SQLite database, executes `PRAGMA foreign_keys = ON;`, creates tables `nodes` (`id`, `type`, `name`, `data`) and `edges` (`source_id`, `target_id`, `type`, `confidence`, `provenance`), creates indexes (`idx_nodes_type`, `idx_edges_source`, `idx_edges_target`).
* **`add_node(node: ScientificNode) -> None`**: Upserts node JSON into SQLite database.
* **`add_edge(edge: Edge) -> None`**: Verifies `source_id` and `target_id` exist. Upserts edge into SQLite database.
* **`node_exists(node_id: str) -> bool`**: Returns boolean indicating node presence.
* **`get_node(node_id: str) -> Optional[ScientificNode]`**: Fetches node and validates via Pydantic `TypeAdapter`.
* **`get_edge(source_id: str, target_id: str, edge_type: str) -> Optional[Edge]`**: Fetches single edge.
* **`get_neighbors(node_id: str, direction: str = "outgoing") -> List[Tuple[Edge, ScientificNode]]`**: Retrieves connected edges and neighbor nodes.
* **`to_networkx() -> nx.DiGraph`**: Exports full graph into NetworkX `DiGraph`.
* **`load_knowledge_graph(kg: KnowledgeGraph) -> None`**: Bulk upserts graph.
* **`export_knowledge_graph() -> KnowledgeGraph`**: Exports database into `KnowledgeGraph` Pydantic model.
* **`close() -> None`**: Closes connection.

#### Invocations & Testing
* **Programmatic**:
  ```python
  from axiom.core.knowledge_graph.db import EpistemicStore
  from axiom.core.knowledge_graph.schema import PaperNode, Edge, EdgeType

  store = EpistemicStore("/tmp/axiom.db")
  paper = PaperNode(id="p1", name="Title", arxiv_id="2301.0001")
  store.add_node(paper)
  ```
* **Pytest**: `pytest tests/test_epistemic_layer.py::test_db_persistence`

#### Error Conditions
* Adding edge with non-existent source or target node raises `ValueError("Cannot create edge ... One or both nodes do not exist.")`.
* Invalid neighbor direction raises `ValueError("Direction must be either 'outgoing' or 'incoming'")`.

---

### Feature 2: Circular Dependency Guard
* **Category**: Graph Validation Guard (EGS - M1)
* **Status**: Implemented (`axiom/core/parser/semantic_tracker.py`)
* **Module Entrypoint**: `axiom.core.parser.semantic_tracker.SemanticTracker`

#### Public API Contracts
* **`SemanticTracker(store: EpistemicStore)`**
* **`detect_circular_dependencies() -> List[List[str]]`**: Converts `EpistemicStore` to NetworkX graph, filters edges matching logical dependency types (`PROVES`, `EXTENDS`, `USES_METHOD`), executes `nx.simple_cycles(dep_graph)`, and returns list of node ID cycle loops.
* **`get_critical_path_claims(limit: int = 5) -> List[Tuple[str, int]]`**: Analyzes dependency out-degrees in `dep_graph` and returns top `limit` critical path claim IDs with their dependent counts.

#### Invocations & Testing
* **Programmatic**:
  ```python
  from axiom.core.parser.semantic_tracker import SemanticTracker
  tracker = SemanticTracker(store)
  cycles = tracker.detect_circular_dependencies()
  critical_claims = tracker.get_critical_path_claims(limit=5)
  ```
* **Pytest**: `pytest tests/test_epistemic_layer.py::test_semantic_tracker`

#### Error Conditions
* Returns empty list `[]` if no cycles exist or if graph processing encounters invalid subgraphs.

---

### Feature 3: LaTeX AST Math & Citation Ingestion
* **Category**: Ingestion Engine (EIE - M1)
* **Status**: Implemented (`axiom/core/parser/arxiv_parser.py`, `axiom/core/parser/semantic_tracker.py`)
* **Module Entrypoint**: `axiom.core.parser.arxiv_parser.ArxivParser`

#### Public API Contracts
* **`ArxivParser(cache_dir: Optional[str] = None)`**: Defaults cache to `tempfile.gettempdir()`.
* **`download_source(arxiv_id: str) -> str`**: Fetches source tarball from `https://arxiv.org/src/{arxiv_id}` and saves to `{cache_dir}/{arxiv_id}.tar.gz`.
* **`extract_source(tar_path: str, extract_dir: str) -> List[str]`**: Unpacks tarball and returns paths to `.tex` files.
* **`parse_paper(arxiv_id: str) -> Tuple[PaperNode, List[MathematicalClaimNode], List[ConceptNode], List[Edge]]`**: Full pipeline from arXiv ID to Pydantic nodes/edges.
* **`parse_tex_content(arxiv_id: str, content: str) -> Tuple[PaperNode, List[MathematicalClaimNode], List[ConceptNode], List[Edge]]`**:
  * Extracts title (`\title{...}`) and abstract (`\begin{abstract}...\end{abstract}`).
  * Parses environments (`theorem`, `lemma`, `definition`, `conjecture`, `proposition`, `corollary`).
  * Generates SHA-256 hashes for node IDs.
  * Maps `conjecture` environments to `CONJECTURED` status; others to `VERIFIED`.
  * Extracts inline/block citation keys (`\cite{...}`).
* **`SemanticTracker.resolve_proof_dependencies(paper_id: str, tex_content: str, citation_map: Dict[str, str]) -> List[Edge]`**:
  * Scans proof environments (`\begin{proof}...\end{proof}`) attached to theorem statements.
  * Resolves citation keys via `citation_map` to build `USES_METHOD` edges from claim to target cited paper.

#### Invocations & Testing
* **Programmatic**:
  ```python
  from axiom.core.parser.arxiv_parser import ArxivParser
  parser = ArxivParser()
  paper, claims, concepts, edges = parser.parse_tex_content("2303.1234", tex_string)
  ```
* **Pytest**: `pytest tests/test_epistemic_layer.py::test_latex_parsing`

#### Error Conditions
* HTTP network errors on source download trigger `requests.HTTPError` via `raise_for_status()`.
* Unpack errors on invalid tarballs fall back to raw text parsing.

---

### Feature 4: Epistemic JSON Graph Serializer
* **Category**: Graph Serialization & Exchange (EGS/EIE - M1)
* **Status**: Implemented (`axiom/core/knowledge_graph/schema.py`, `axiom/core/knowledge_graph/db.py`)
* **Module Entrypoint**: `axiom.core.knowledge_graph.schema.KnowledgeGraph`

#### Public API Contracts & Schema
* **`KnowledgeGraph`**: Top-level graph payload containing `nodes: List[ScientificNode]` and `edges: List[Edge]`.
* **`store.export_knowledge_graph() -> KnowledgeGraph`**: Serializes active SQLite database into `KnowledgeGraph` Pydantic instance.
* **`store.load_knowledge_graph(kg: KnowledgeGraph) -> None`**: Ingests JSON/model payload into database.
* Serialization methods: `kg.model_dump_json()`, `KnowledgeGraph.model_validate_json(json_str)`.

#### Invocations & Testing
* **Programmatic**:
  ```python
  kg = store.export_knowledge_graph()
  json_output = kg.model_dump_json(indent=2)
  ```
* **Pytest**: `pytest tests/test_epistemic_layer.py::test_pydantic_schema`

#### Error Conditions
* Missing node discriminator `type` or invalid payload fields raise `pydantic.ValidationError`.

---

### Feature 5: LaTeX-to-Lean 4 AST Exporter
* **Category**: Logical Exporter (LRK - M2)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Modules**: `axiom.core.exporter.lean_ast`, `axiom.core.exporter.lean_exporter`

#### Specification & Contracts
* **Input**: `ParsedMathExpression` (extracted LaTeX math AST, variables, hypotheses).
* **Target AST Class**: `LeanTheoremAST`
  * `name`: `str`
  * `variables`: `Dict[str, str]` (e.g. `{"a": "Nat", "b": "Nat"}`)
  * `hypotheses`: `List[str]`
  * `target_goal`: `str` (e.g. `"a + b = b + a"`)
  * `proof_script`: `Optional[str]`
* **Rendering Contract**: `ast.render() -> str` produces compilable Lean 4 source string:
  ```lean
  theorem thm_add_comm (a b : Nat) : a + b = b + a := by rfl
  ```

#### Invocation & Error Conditions
* **Target Pytest Path**: `pytest tests/test_exporter.py`
* **Error Behavior**: Syntax translation failure raises `LeanTranslationError`.

---

### Feature 6: SMT / Z3 Counterexample Gateway
* **Category**: Verification & SMT (AVT - M2)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Module**: `axiom.core.verification.smt_gateway`

#### Specification & Contracts
* **Request Model**: `SMTCheckRequest`
  * `claim_id`: `str`
  * `variables`: `Dict[str, str]`
  * `assumptions`: `List[str]`
  * `conjecture_negation`: `str`
  * `timeout_ms`: `int = 60000` (60s parameter sweep limit)
* **Response Model**: `SMTCheckResponse`
  * `claim_id`: `str`
  * `status`: `EpistemicStatus` (`VERIFIED` if UNSAT, `REFUTED` if SAT counterexample found)
  * `counterexample`: `Optional[Dict[str, Any]]`
  * `execution_time_ms`: `float`
* **Storage Side Effects**: Writes result into SQLite `verification_records` table and updates `MathematicalClaimNode.status` to `REFUTED` or `VERIFIED`.

#### Invocation & Error Conditions
* **Target Pytest Path**: `pytest tests/test_verification.py`
* **Error Behavior**: Solver timeout (>60,000 ms) or unknown Z3 expression returns `status="UNKNOWN"` with timeout error log.

---

### Feature 7: Lean 4 Compiler Proof Checker
* **Category**: Compiler Verification (AVT - M2)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Module**: `axiom.core.verification.lean_checker`

#### Specification & Contracts
* **Request Model**: `LeanCompileRequest`
  * `lean_code`: `str`
  * `timeout_ms`: `int = 30000`
* **Response Model**: `LeanCompileResponse`
  * `is_valid`: `bool`
  * `status_code`: `str`
  * `errors`: `List[LeanCompileError]`
  * `execution_time_ms`: `int`
* **Verification Rule**: Proof is designated `is_valid = True` ONLY if `lean` subprocess exits 0, returns 0 syntax/type errors, and contains NO `sorry` axioms. Updates node tier to `TIER_2_PROVEN`.

#### Invocation & Error Conditions
* **Target Pytest Path**: `pytest tests/test_verification.py`
* **Error Behavior**: Lean compiler missing from system PATH, process timeout, or presence of `sorry` axiom sets `is_valid = False`.

---

### Feature 8: MCTS Proof Search Engine
* **Category**: Proof Discovery (DRSP - M3)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Module**: `axiom.core.discovery.mcts_engine`

#### Specification & Contracts
* **Data Structure**: `MCTSNode`
  * `state`: Lean proof goal state
  * `parent`: Optional[`MCTSNode`]
  * `children`: List[`MCTSNode`]
  * `visits`: `int`
  * `value`: `float`
* **Algorithm**: Upper Confidence Bound for Trees (UCT) tactic selection:
  $$UCT = \frac{Q_i}{N_i} + c \sqrt{\frac{\ln N}{N_i}}$$
  Explores Lean tactics (`rw`, `simp`, `rfl`, `induction`), evaluates candidates via Lean Compiler Runner, and backpropagates rewards.

#### Invocation & Error Conditions
* **Target Pytest Path**: `pytest tests/test_mcts.py`
* **Error Behavior**: Max search depth / iteration limit reached returns unverified state.

---

### Feature 9: Autonomous Discovery Loop
* **Category**: Discovery Orchestration (DRSP - M3)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Module**: `axiom.core.discovery.discovery_loop`

#### Specification & Contracts
* Continuous background loop querying `EpistemicStore` for `CONJECTURED` claims.
* Dispatches concurrent SMT parameter sweeps (Feature 6) and MCTS tactic search workers (Feature 8).
* Updates SQLite store with newly verified theorems or refuted counterexamples.

#### Invocation & Error Conditions
* **Target Pytest Path**: `pytest tests/test_discovery.py`
* **Error Behavior**: DB lock timeouts handled gracefully with retry backoff.

---

### Feature 10: Spatial Canvas Next.js Frontend
* **Category**: UI Spatial Dashboard (UI - M4)
* **Status**: Planned Specification (`PROJECT.md` Architecture & Interface Contracts)
* **Planned Target Path**: `ui/` (Next.js 14 App Router, `src/components/SpatialCanvas.tsx`)

#### Specification & Contracts
* React Flow / HTML5 Spatial Canvas node-link visualizer.
* Endpoint Consumption: `GET /api/v1/graph/spatial` -> `SpatialGraphDataResponse(nodes: SpatialNode[], edges: SpatialEdge[])`.
* **Color Schemes**:
  * Green (`#22c55e`): `VERIFIED`
  * Amber (`#f59e0b`): `CONJECTURED`
  * Red (`#ef4444`): `REFUTED`
  * Slate (`#64748b`): `UNDER_REVIEW` / Default

#### Invocation & CLI
* Dev Server: `cd ui && npm run dev` (Port 3000)

---

### Feature 11: FastAPI Graph & Proof API Gateway
* **Category**: API Gateway (API - M4)
* **Status**: Implemented (`axiom/services/api_gateway/main.py`, `auth.py`, `axiom/services/model_gateway/client.py`)
* **Module Entrypoint**: `axiom.services.api_gateway.main.app`

#### Implemented REST Endpoints & Authentication
* **Auth Scheme**: Bearer Token Dependency (`verify_token` in `auth.py`). Validates `Authorization: Bearer <AXIOM_API_TOKEN>` (default `test_token`).
* **`GET /health`**: Liveness probe (Unprotected).
  * Returns: `{"status": "healthy", "timestamp": 1722800000.0}` (HTTP 200)
* **`GET /ready`**: Readiness probe (Unprotected). Checks SQLite database connection (`SELECT 1;`).
  * Returns: `{"status": "ready", "database": "connected"}` (HTTP 200)
  * Error: `HTTPException(503, "Database connection unhealthy")`
* **`POST /ingest`**: Triggers paper ingestion (Protected).
  * Request Body: `IngestionRequest(arxiv_id: str)`
  * Returns: `{"status": "triggered", "arxiv_id": "2303.1234", "task_id": "ingest_2303.1234_1722800000"}` (HTTP 200)
* **`POST /query`**: Knowledge graph search (Protected).
  * Request Body: `QueryRequest(query_string: str)`
  * Returns: `{"status": "success", "query": "...", "results": []}` (HTTP 200)

#### Model Gateway Client (`client.py`)
* **`ModelClient(cache_path: str = "/tmp/axiom_model_cache.db")`**
* **`generate(prompt: str, model: str = "mock-model", temperature: float = 0.7) -> str`**: Calculates SHA-256 hash of prompt parameters. Checks local SQLite cache `model_cache`. If missing, calls OpenAI (if `OPENAI_API_KEY`), Gemini (if `GEMINI_API_KEY`), or local mock generator `_generate_mock()`.

#### Invocations & Testing
* **Uvicorn Gateway Command**:
  ```bash
  uvicorn axiom.services.api_gateway.main:app --host 0.0.0.0 --port 8000
  ```
* **Pytest**: `pytest tests/test_api.py`
* **HTTP Requests**:
  ```bash
  curl http://localhost:8000/health
  curl -H "Authorization: Bearer test_token" -H "Content-Type: application/json" -X POST http://localhost:8000/ingest -d '{"arxiv_id": "2303.1234"}'
  ```

---

## 3. Discovered Features & Edge Cases

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | EGS | SQLite Relational Graph Store | Core relational database for nodes, edges, foreign key enforcement, and indexes | Pydantic node/edge objects | Saved SQLite records | `ValueError` on missing target/source node | `axiom/core/knowledge_graph/db.py` |
| 2 | EGS | NetworkX Export & Graph Conversion | Converts SQLite tables to `networkx.DiGraph` for analysis | None | `nx.DiGraph` | Empty graph if DB is empty | `EpistemicStore.to_networkx()` |
| 3 | EGS | Circular Dependency Guard | Detects circular reasoning loops in `PROVES`, `EXTENDS`, `USES_METHOD` edges | None | `List[List[str]]` (node cycles) | Returns `[]` if graph is acyclic | `SemanticTracker.detect_circular_dependencies()` |
| 4 | EGS | Critical Path Claim Analyzer | Identifies most heavily relied-upon mathematical claims by out-degree | `limit: int = 5` | `List[Tuple[str, int]]` | Returns `[]` if no dependency edges exist | `SemanticTracker.get_critical_path_claims()` |
| 5 | EIE | arXiv LaTeX Source Downloader | Downloads source tarball from `https://arxiv.org/src/{arxiv_id}` to cache | `arxiv_id: str` | Tarball file path | `requests.HTTPError` on missing ID | `ArxivParser.download_source()` |
| 6 | EIE | LaTeX AST Environment Parser | Regex environment parser extracting claims, concepts, abstracts, and title | LaTeX source string | `(PaperNode, List[MathematicalClaimNode], List[ConceptNode], List[Edge])` | Falls back to default arXiv title if missing | `ArxivParser.parse_tex_content()` |
| 7 | EIE | Proof Citation Resolver | Links theorem statements to cited paper nodes inside proof bodies | `paper_id`, `tex_content`, `citation_map` | `List[Edge]` (`USES_METHOD`) | Returns `[]` if no citations match map | `SemanticTracker.resolve_proof_dependencies()` |
| 8 | EGS | Epistemic JSON Graph Serializer | Bulk load & export of full knowledge graph to Pydantic payload | `KnowledgeGraph` instance / SQLite state | `KnowledgeGraph` model | `pydantic.ValidationError` on bad schema | `EpistemicStore.export_knowledge_graph()` |
| 9 | LRK | LaTeX-to-Lean 4 AST Exporter | Translates LaTeX math expressions to Lean 4 theorem declarations | `ParsedMathExpression` | `LeanTheoremAST` code string | `LeanTranslationError` on unparseable math | `PROJECT.md` Architecture |
| 10 | AVT | SMT / Z3 Counterexample Gateway | Parameter sweep checking conjectures for counterexamples within <60s | `SMTCheckRequest` | `SMTCheckResponse` | Timeout / `UNKNOWN` response on complex formulas | `PROJECT.md` Architecture |
| 11 | AVT | Lean 4 Compiler Proof Checker | Subprocess runner compiling Lean source code and verifying absence of `sorry` | `LeanCompileRequest` | `LeanCompileResponse` | `is_valid=False` on syntax error or `sorry` | `PROJECT.md` Architecture |
| 12 | DRSP | MCTS Proof Search Engine | UCT tactic exploration searching for valid Lean proof steps | `goal_state` | Proof script | Returns unverified state on iteration cap | `PROJECT.md` Architecture |
| 13 | DRSP | Autonomous Discovery Loop | Background cycle managing claim selection, verification workers, and state updates | None | Verified/Refuted DB updates | DB lock retries | `PROJECT.md` Architecture |
| 14 | UI | Spatial Canvas Next.js Frontend | Next.js/React Flow UI visualizer displaying graph nodes with status colors | REST graph API | Rendered spatial canvas | Network disconnect overlay | `PROJECT.md` Architecture |
| 15 | API | FastAPI Gateway & Auth Middleware | Bearer token protected REST endpoints (`/health`, `/ready`, `/ingest`, `/query`) | HTTP Request + Bearer header | JSON response | `401 Unauthorized` / `503 Service Unavailable` | `axiom/services/api_gateway/main.py` |
| 16 | API | Model Gateway Client with SQLite Cache | LLM provider abstraction (OpenAI, Gemini, Mock) with local SQLite caching | `prompt`, `model`, `temperature` | Response text string | Fallback to mock generation if no API keys | `axiom/services/model_gateway/client.py` |

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | SQLite Graph Store | Edge creation where `source_id` or `target_id` is missing in `nodes` table | `EpistemicStore.add_edge` raises `ValueError("Cannot create edge X -> Y. One or both nodes do not exist.")` |
| 2 | SQLite Graph Store | Neighbor query with invalid direction string (e.g. `direction="both"`) | `EpistemicStore.get_neighbors` raises `ValueError("Direction must be either 'outgoing' or 'incoming'")` |
| 3 | arXiv Parser | arXiv ID returning single `.tex` or uncompressed file instead of `.tar.gz` | `extract_source` catches `tarfile.ReadError` gracefully and continues parsing any extracted `.tex` files |
| 4 | arXiv Parser | LaTeX title containing formatting commands like `\title{\textbf{Theorem A}}` | Regex strips macros `\\[a-zA-Z]+` and braces, returning clean title string `"Theorem A"` |
| 5 | Circular Dependency Guard | Graph containing informational `CITES` cycle between papers | `detect_circular_dependencies` filters only `PROVES`, `EXTENDS`, and `USES_METHOD` edges, ignoring pure citation cycles |
| 6 | API Gateway | Client request without `Authorization` header to `/ingest` or `/query` | FastAPI returns `401 Unauthorized` with detail `"Authorization header missing"` |
| 7 | API Gateway | Client request with non-Bearer auth scheme (e.g. `Basic token123`) | FastAPI returns `401 Unauthorized` with detail `"Authorization header must follow Bearer token format"` |
| 8 | Model Client | Calling `ModelClient.generate()` multiple times with identical prompt parameters | Computes SHA-256 hash `f"{model}:{prompt}:{temperature}"`, fetches response from SQLite `model_cache` on second call without hitting model/mock provider |
