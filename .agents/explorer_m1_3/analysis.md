# Milestone 1 Analysis Report: Test Architecture, Ingestion Integration & Edge Case Analysis

**Author**: Explorer 3 (Milestone 1 — Graph Store & Ingestion: EGS & EIE)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_3`  
**Date**: 2026-08-04  

---

## 1. Executive Summary

Milestone 1 implements the core epistemic storage and parser foundation for AXIOM:
- **Feature 1**: SQLite Graph Relational Storage & Schema (`EpistemicStore`)
- **Feature 2**: Circular Dependency Guard (`CircularDependencyError` enforcement on logical DAG edges)
- **Feature 3**: LaTeX AST Math & Citation Ingestion (>95% environment extraction accuracy)
- **Feature 4**: Epistemic JSON Graph Serializer (`IngestedPaperGraphPayload`)

This analysis evaluates the codebase from the perspective of **test architecture, integration verification, and error-handling edge cases**. Key findings include:
1. **Missing Unit Test Files**: The required unit test suites `tests/test_graph_store.py` and `tests/test_parser.py` specified in `SCOPE.md` do not exist yet in the codebase.
2. **Missing Cycle Guard Enforcement**: `EpistemicStore.add_edge()` in `axiom/core/knowledge_graph/db.py` currently permits cyclic edge insertions without raising `CircularDependencyError` or rolling back transactions.
3. **Missing Ingestion Transaction Integration**: The integration bridge between `IngestedPaperGraphPayload` and `EpistemicStore` requires atomic transactional ingestion (`load_paper_payload`) with cycle guard validation.
4. **Test Environment Requirements**: The system test command `pytest` requires virtual environment activation (`python3 -m venv .venv`).

This report provides complete specifications for `tests/test_graph_store.py` and `tests/test_parser.py`, defines the integration contract for paper ingestion into SQLite, and provides a 5-category edge case checklist.

---

## 2. Codebase Audit & Gap Analysis

### 2.1 Inventory of Inspected Files

| File Path | Description | Current Status / Gaps Identified |
|---|---|---|
| `pyproject.toml` | Project configuration & dependencies | Includes `pylatexenc`, `pydantic`, `networkx`, `fastapi`, `pytest`. Requires venv setup to execute `pytest`. |
| `axiom/core/knowledge_graph/schema.py` (102 lines) | Pydantic node/edge schema models | Defines `ScientificNode` union, `Edge`, `KnowledgeGraph`. Missing `CircularDependencyError` exception class. |
| `axiom/core/knowledge_graph/db.py` (222 lines) | SQLite relational store (`EpistemicStore`) | Implements table creation, CRUD, NetworkX export. Missing pre-insertion cycle check and transaction rollback on cycle detection. |
| `axiom/core/parser/arxiv_parser.py` (188 lines) | arXiv LaTeX source parser | Uses basic regex parser. Explorer 2 proposed replacing with 4-pass AST parser (`LatexASTParser`). |
| `axiom/core/parser/semantic_tracker.py` (114 lines) | Proof citation & cycle detection tracker | Computes post-hoc NetworkX cycles. Needs integration with `add_edge` pre-commit validation. |
| `tests/test_epistemic_layer.py` (202 lines) | Existing initial integration tests | Tests basic schema, store persistence, basic regex parsing, and post-hoc cycle detection. |
| `tests/test_api.py` (68 lines) | Service API tests | Tests `/health`, `/ready`, auth protection, and model gateway caching. |
| `tests/test_graph_store.py` | **Target Unit Test File (M1)** | **MISSING**. Must be created to test DB schema, CRUD, indexing, polymorphic nodes, cycle guard, and transactional rollbacks. |
| `tests/test_parser.py` | **Target Unit Test File (M1)** | **MISSING**. Must be created to test LaTeX AST parsing, alias resolution, comment stripping, BibTeX resolution, payload serialization, and >95% accuracy benchmark. |

---

## 3. Test Architecture & Unit Test Specifications

The test suite structure must follow co-location and module isolation principles:

```
tests/
├── test_graph_store.py       # Feature 1 & 2: SQLite DB CRUD, indexing, cycle guard, transaction rollback
├── test_parser.py            # Feature 3 & 4: AST LaTeX parser, >95% extraction accuracy, BibTeX, payload serialization
├── test_epistemic_layer.py   # Full integration: Parser -> Payload -> Store pipeline
└── test_api.py               # Gateway endpoints & authentication
```

### 3.1 Specification for `tests/test_graph_store.py`

`tests/test_graph_store.py` must contain unit tests for all database and cycle guard behaviors:

1. **`test_database_initialization_and_indexes()`**:
   - Verify creation of `nodes` and `edges` tables in an in-memory SQLite database (`:memory:`).
   - Verify presence of indexes (`idx_nodes_type`, `idx_edges_source`, `idx_edges_target`).
   - Verify `PRAGMA foreign_keys` is set to `ON`.

2. **`test_polymorphic_node_crud_and_upsert()`**:
   - Test inserting and retrieving all 6 node types (`PaperNode`, `AuthorNode`, `ConceptNode`, `MathematicalClaimNode`, `ExperimentalFactNode`, `DatasetNode`).
   - Verify field preservation and Pydantic schema validation on retrieval (`store.get_node(id)`).
   - Verify upsert behavior: updating existing node ID updates name and data payload without duplicating rows.

3. **`test_edge_foreign_key_enforcement()`**:
   - Test inserting an edge referencing non-existent `source_id` or `target_id`.
   - Verify `ValueError` (or `sqlite3.IntegrityError`) is raised.

4. **`test_edge_crud_and_neighbor_queries()`**:
   - Test `add_edge`, `get_edge`, and `get_neighbors(node_id, direction="outgoing"/"incoming")`.
   - Verify edge types (`PROVES`, `EXTENDS`, `CITES`, `USES_METHOD`) and metadata provenance dictionary preservation.

5. **`test_circular_dependency_guard_logical_edges()`**:
   - Insert nodes `A`, `B`, `C`.
   - Add edge `A -> B` (`PROVES`) and `B -> C` (`EXTENDS`).
   - Attempt to add edge `C -> A` (`USES_METHOD`).
   - Assert `CircularDependencyError` is raised.
   - Verify edge `C -> A` was **NOT** written to the database.

6. **`test_cycle_guard_allows_non_logical_edges()`**:
   - Insert nodes `P1`, `P2`.
   - Add edge `P1 -> P2` (`CITES`).
   - Add edge `P2 -> P1` (`CITES`).
   - Verify cross-citations between papers are permitted without error.

7. **`test_transaction_rollback_on_failed_ingestion()`**:
   - Test bulk load of a `KnowledgeGraph` containing a cyclic logical edge.
   - Assert `CircularDependencyError` is raised.
   - Verify database state remains completely unchanged (atomic transaction rollback).

8. **`test_on_delete_cascade()`**:
   - Add node `N1` and `N2`, plus edge `N1 -> N2`.
   - Delete node `N1` directly via SQL query.
   - Verify edge `N1 -> N2` is automatically removed by SQLite foreign key cascade.

---

### 3.2 Specification for `tests/test_parser.py`

`tests/test_parser.py` must test LaTeX AST parsing, BibTeX resolution, payload serialization, and math environment extraction:

1. **`test_ast_math_environment_extraction()`**:
   - Input LaTeX text with `theorem`, `lemma`, `definition`, `claim`, `proposition`, `corollary`, `conjecture`, and `proof`.
   - Assert all environments are extracted as `MathematicalClaimNode` or `ConceptNode`.

2. **`test_newtheorem_alias_resolution()`**:
   - Input LaTeX text defining custom macros: `\newtheorem{thm}{Theorem}` and `\newtheorem{lem}[thm]{Lemma}`.
   - Parse statements under `\begin{thm} ... \end{thm}` and `\begin{lem} ... \end{lem}`.
   - Assert correct identification as `theorem` and `lemma` claim nodes.

3. **`test_comment_and_nested_environment_handling()`**:
   - Input LaTeX text containing commented blocks (`% \begin{theorem} fake \end{theorem}`) and nested environments (`\begin{proof} ... \begin{lemma} ... \end{lemma} ... \end{proof}`).
   - Assert commented code is ignored and nested environments parse cleanly.

4. **`test_bibtex_and_thebibliography_parsing()`**:
   - Input LaTeX text and `.bib` file containing `@article{Babai2016, ...}` and `\bibitem{Gödel31}`.
   - Verify creation of `PaperNode` objects with DOI, authors, title, and citation keys.

5. **`test_proof_citation_uses_method_resolution()`**:
   - Input LaTeX text with `\begin{proof}` containing `\cite{Babai2016}`.
   - Assert generation of `Edge(source_id=claim_id, target_id=babai_paper_id, type=EdgeType.USES_METHOD)`.

6. **`test_ingested_paper_graph_payload_serialization()`**:
   - Construct `IngestedPaperGraphPayload`.
   - Execute `json_str = payload.to_json()` and `restored = IngestedPaperGraphPayload.from_json(json_str)`.
   - Assert equality of paper node, claims, concepts, cited papers, and edges.
   - Execute `kg = payload.to_knowledge_graph()` and verify `KnowledgeGraph` structure.

7. **`test_math_environment_accuracy_benchmark()`**:
   - Benchmark test with a mock arXiv paper containing 20 math environments (standard environments, custom `\newtheorem` aliases, commented environments, optional titles).
   - Assert extracted environments / total true environments >= 0.95 (>= 95% accuracy).

---

## 4. System Integration Design: Graph Store ↔ Parser

### 4.1 Ingestion Architecture Flow

```
                      arXiv Source Archive / Raw LaTeX
                                    │
                                    ▼
                          ArxivParser / LatexASTParser
                                    │
                                    ▼
                       IngestedPaperGraphPayload
                                    │
                                    ▼
                payload.to_knowledge_graph() -> KnowledgeGraph
                                    │
                                    ▼
                       EpistemicStore.load_paper_payload()
                                    │
                  ┌─────────────────┴─────────────────┐
                  │   sqlite3 Transaction Context     │
                  │   1. INSERT/UPSERT All Nodes      │
                  │   2. Validate DAG (No Cycles)     │
                  │   3. INSERT/UPSERT All Edges      │
                  └─────────────────┬─────────────────┘
                                    │
                         COMMIT / ROLLBACK
```

### 4.2 Integration Interface Contract

In `axiom/core/knowledge_graph/schema.py`:
```python
class CircularDependencyError(Exception):
    """Raised when adding a logical edge would create a cycle in the knowledge graph."""
    pass
```

In `axiom/core/knowledge_graph/db.py`:
```python
    def add_edge(self, edge: Edge, check_cycle: bool = True) -> None:
        """
        Upsert an edge in the database.
        If check_cycle is True and edge is a logical dependency (PROVES, EXTENDS, USES_METHOD),
        verify that inserting the edge does not violate DAG acyclicity.
        """
        if not self.node_exists(edge.source_id) or not self.node_exists(edge.target_id):
            raise ValueError(
                f"Cannot create edge {edge.source_id} -> {edge.target_id}. One or both nodes do not exist."
            )

        LOGICAL_EDGE_TYPES = {EdgeType.PROVES.value, EdgeType.EXTENDS.value, EdgeType.USES_METHOD.value}

        if check_cycle and edge.type.value in LOGICAL_EDGE_TYPES:
            # Build current logical graph from DB + proposed edge
            G = self.to_networkx_logical_subgraph()
            G.add_edge(edge.source_id, edge.target_id)
            if not nx.is_directed_acyclic_graph(G):
                try:
                    cycle = nx.find_cycle(G, orientation="original")
                    cycle_str = " -> ".join([f"{u}" for u, v, _ in cycle] + [f"{cycle[0][0]}"])
                except Exception:
                    cycle_str = f"{edge.source_id} -> {edge.target_id}"
                raise CircularDependencyError(
                    f"Inserting edge {edge.source_id} -> {edge.target_id} ({edge.type.value}) "
                    f"creates a circular dependency: {cycle_str}"
                )

        prov_json = json.dumps(edge.provenance)
        assert self.conn is not None
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO edges (source_id, target_id, type, confidence, provenance)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, type) DO UPDATE SET
                    confidence = excluded.confidence,
                    provenance = excluded.provenance;
                """,
                (edge.source_id, edge.target_id, edge.type.value, edge.confidence, prov_json)
            )

    def load_paper_payload(self, payload: "IngestedPaperGraphPayload") -> None:
        """
        Atomically load an IngestedPaperGraphPayload into the SQLite store.
        If any edge violates DAG constraints, the entire transaction is rolled back.
        """
        assert self.conn is not None
        kg = payload.to_knowledge_graph()
        
        try:
            # Begin explicit transaction
            self.conn.execute("BEGIN TRANSACTION;")
            for node in kg.nodes:
                self.add_node(node)
            for edge in kg.edges:
                self.add_edge(edge, check_cycle=True)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
```

---

## 5. Comprehensive Edge Case Checklist & Error Handling Matrix

| # | Edge Case Scenario | Category | Expected Behavior / System Handling | Verification Method |
|---|---|---|---|---|
| **E1** | Foreign key violation: Edge connects to non-existent node ID | Graph Store | Raises `ValueError` with clear message before DB execute; transaction aborts | `test_edge_foreign_key_enforcement()` |
| **E2** | Logical cycle creation: Edge `C -> A` forms cycle in `PROVES`/`EXTENDS`/`USES_METHOD` | Graph Store | `add_edge()` raises `CircularDependencyError`; transaction rolls back; 0 edges added | `test_circular_dependency_guard_logical_edges()` |
| **E3** | Non-logical cycle: Edge `P1 -> P2 -> P1` with `CITES` type | Graph Store | Permitted without error; non-logical edges exempt from DAG cycle guard | `test_cycle_guard_allows_non_logical_edges()` |
| **E4** | SQLite database lock / concurrent write | Graph Store | `check_same_thread=False`, SQLite `WAL` journal mode enabled; busy timeout set to 5000ms | SQLite concurrency stress test |
| **E5** | Corrupted JSON in `nodes.data` or `edges.provenance` | Graph Store | `get_node()` raises `pydantic.ValidationError`; does not crash DB connection | `test_corrupted_data_deserialization()` |
| **E6** | LaTeX custom aliases (`\newtheorem{clm}{Claim}`) | Parser | `LatexASTParser` Pass 1 registers macro; maps `clm` -> `claim` claim node | `test_newtheorem_alias_resolution()` |
| **E7** | LaTeX comments (`% \begin{theorem} fake \end{theorem}`) | Parser | `pylatexenc` AST skips `LatexCommentNode`; 0 fake claims created | `test_comment_and_nested_environment_handling()` |
| **E8** | Nested environments (`\begin{proof} ... \begin{lemma} ... \end{lemma} ... \end{proof}`) | Parser | Recursive AST traversal isolates inner environment correctly | `test_comment_and_nested_environment_handling()` |
| **E9** | Malformed TeX syntax (unclosed `\begin{theorem}`) | Parser | AST parser isolates unclosed node gracefully without process crash | `test_malformed_tex_graceful_recovery()` |
| **E10** | Missing BibTeX entry for `\cite{unknown_key}` | BibTeX | Creates placeholder `PaperNode(id="placeholder:unknown_key")` with `metadata["status"]="unresolved"` | `test_missing_bibtex_key_resolution()` |
| **E11** | Multiple citation keys in single macro (`\cite{k1, k2}`) | BibTeX | Splits keys on comma; creates `USES_METHOD` edge for each valid key | `test_multi_key_citation_parsing()` |
| **E12** | Non-UTF8 TeX file encoding (Latin-1 / ISO-8859-1) | Parser | `open(file, encoding="utf-8", errors="ignore")` fallback handles decoding safely | `test_latin1_encoding_handling()` |
| **E13** | Multi-file TeX archive (`\input{sec1.tex}`, `\include{proofs.tex}`) | Parser | Concatenates `.tex` files in extract directory before AST parsing | `test_multi_file_tex_concatenation()` |
| **E14** | Paper payload ingestion partial failure | Integration | `load_paper_payload` executes in `BEGIN TRANSACTION ... ROLLBACK`; DB remains clean | `test_transaction_rollback_on_failed_ingestion()` |
| **E15** | Idempotent paper re-ingestion | Integration | Upserts nodes and edges (`ON CONFLICT DO UPDATE`); no duplicate row errors | `test_idempotent_payload_reingestion()` |

---

## 6. Implementation & Test Strategy Roadmap

To guide the Worker agent in implementing Milestone 1:

1. **Step 1: Exception & Schema Definition (`axiom/core/knowledge_graph/schema.py`)**:
   - Define `CircularDependencyError(Exception)`.
2. **Step 2: Database Cycle Guard & Atomic Ingestion (`axiom/core/knowledge_graph/db.py`)**:
   - Implement `to_networkx_logical_subgraph()`.
   - Update `add_edge()` with pre-insertion cycle check raising `CircularDependencyError`.
   - Implement `load_paper_payload(payload)` with transaction rollback.
3. **Step 3: AST Parser & Serializer Implementation (`axiom/core/parser/latex_ast_parser.py`)**:
   - Implement `IngestedPaperGraphPayload` Pydantic model.
   - Implement `LatexASTParser` with 4-pass AST processing (`pylatexenc.latexwalker`).
4. **Step 4: Unit Test Suite Creation (`tests/test_graph_store.py` & `tests/test_parser.py`)**:
   - Implement all 8 test cases in `test_graph_store.py`.
   - Implement all 7 test cases in `test_parser.py`.
5. **Step 5: Test Execution & Verification**:
   - Run `python3 -m pytest tests/test_graph_store.py tests/test_parser.py tests/test_epistemic_layer.py -v`.

---

## 7. Conclusion

This investigation completes the test architecture, integration design, and edge case formulation for Milestone 1. Implementing the cycle guard inside `EpistemicStore.add_edge()`, wrapping `IngestedPaperGraphPayload` loading in SQLite transactions, and populating `tests/test_graph_store.py` and `tests/test_parser.py` ensures 100% test coverage and robust error handling for AXIOM's epistemic ingestion engine.
