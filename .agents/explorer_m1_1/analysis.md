# Architectural Analysis & Implementation Specification: Milestone 1 Knowledge Graph Store (EGS) & Cycle Guard

**Author**: Explorer 1 (Milestone 1)  
**Target Path**: `axiom/core/knowledge_graph/`  
**Date**: 2026-08-04  

---

## 1. Executive Summary

This report delivers a thorough analysis of the existing codebase at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` for Milestone 1, focusing specifically on the **SQLite Relational Store (EGS)**, **Pydantic Schemas**, and the **NetworkX DAG Circular Dependency Guard**.

The existing implementation in `axiom/core/knowledge_graph/db.py` and `schema.py` provides a baseline for node/edge persistence and NetworkX graph exporting. However, several critical requirements from `PROJECT.md` and `sub_orch_m1/SCOPE.md` are missing:
1. `CircularDependencyError` guard inside `add_edge()` to prevent introducing cyclic logical relationships (`PROVES`, `EXTENDS`, `USES_METHOD`).
2. Table definitions and Pydantic models for `verification_records` and `mcts_search_runs`.
3. Complete CRUD operations (filtering, deleting, listing, verification and MCTS record management).

---

## 2. Existing File Structure & Dependency Inventory

### 2.1 Codebase Layout
- `axiom/core/knowledge_graph/schema.py` — Core Pydantic models (`NodeType`, `EdgeType`, `EpistemicStatus`, `VerificationTier`, `NodeBase`, `ScientificNode`, `Edge`, `KnowledgeGraph`).
- `axiom/core/knowledge_graph/db.py` — SQLite relational store manager (`EpistemicStore`).
- `axiom/core/knowledge_graph/__init__.py` — Package initialization file.
- `axiom/core/parser/arxiv_parser.py` — LaTeX document AST parser.
- `axiom/core/parser/semantic_tracker.py` — Proof dependency tracker and post-hoc circular dependency detector.
- `tests/test_epistemic_layer.py` — Integration unit tests for schema, database persistence, LaTeX parsing, and semantic tracking.
- `pyproject.toml` — Project dependencies.

### 2.2 External Dependencies
- `sqlite3` — Standard Python library for relational database storage with ACID compliance and foreign key enforcement.
- `pydantic` (`^2.5.0`) — Data validation and polymorphic discriminator serialization (`TypeAdapter`, `BaseModel`, `Field`, `Annotated`).
- `networkx` (`^3.0`) — Directed graph modeling, traversal, and cycle path checking (`nx.DiGraph`, `nx.has_path`, `nx.simple_cycles`).

---

## 3. Findings & Gap Analysis

### 3.1 Gap 1: Missing Pydantic Schemas (`schema.py`)
- **Missing `VerificationRecord` Model**: Feature 1 & interface contract EGS ↔ AVT require storing SMT/Z3 and Lean 4 verification attempts and counterexamples.
- **Missing `MCTSSearchRun` Model**: Feature 1 requires tracking MCTS proof search executions for DRSP.
- **Missing Custom Exception `CircularDependencyError`**: SCOPE.md explicitly states that inserting cyclic logical edges must raise `CircularDependencyError`.

### 3.2 Gap 2: Incomplete SQLite Database Schema (`db.py`)
- `_init_db()` currently creates only `nodes` and `edges` tables.
- **Missing `verification_records` table**:
  ```sql
  CREATE TABLE IF NOT EXISTS verification_records (
      record_id TEXT PRIMARY KEY,
      claim_id TEXT NOT NULL,
      verifier_type TEXT NOT NULL,
      status TEXT NOT NULL,
      tier INTEGER NOT NULL,
      counterexample TEXT,
      execution_time_ms INTEGER NOT NULL,
      timestamp TEXT NOT NULL,
      details TEXT,
      FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
  );
  CREATE INDEX IF NOT EXISTS idx_verification_claim ON verification_records(claim_id);
  ```
- **Missing `mcts_search_runs` table**:
  ```sql
  CREATE TABLE IF NOT EXISTS mcts_search_runs (
      run_id TEXT PRIMARY KEY,
      claim_id TEXT NOT NULL,
      status TEXT NOT NULL,
      iterations INTEGER NOT NULL,
      proof_script TEXT,
      created_at TEXT NOT NULL,
      completed_at TEXT,
      FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
  );
  CREATE INDEX IF NOT EXISTS idx_mcts_claim ON mcts_search_runs(claim_id);
  ```

### 3.3 Gap 3: Missing In-line Circular Dependency Guard in `add_edge()`
- **Current Behavior**: `EpistemicStore.add_edge()` inserts any edge without cycle checks. Cycle detection in `SemanticTracker` occurs only post-hoc via `detect_circular_dependencies()`.
- **Required Behavior**: `add_edge()` must validate before insertion. If the edge type is a logical derivation (`PROVES`, `EXTENDS`, `USES_METHOD`) and adding the edge creates a cycle in the logical subgraph, it must raise `CircularDependencyError` and abort the SQLite transaction.
- **Cycle Detection Algorithm**:
  When inserting edge $U \to V$ of type $\in \{\text{PROVES}, \text{EXTENDS}, \text{USES\_METHOD}\}$:
  1. Check if $U == V$ (self-loop). If true, raise `CircularDependencyError`.
  2. Query the logical subgraph from SQLite database or construct it via `to_networkx()`.
  3. If `nx.has_path(logical_graph, V, U)` is true, a path already exists from $V$ to $U$. Adding $U \to V$ would complete a cycle $U \to V \dots \to U$.
  4. Raise `CircularDependencyError` and abort transaction.

### 3.4 Gap 4: Incomplete CRUD Operations in `EpistemicStore`
- Need `delete_node(node_id: str) -> bool`
- Need `delete_edge(source_id: str, target_id: str, edge_type: str) -> bool`
- Need `list_nodes(node_type: Optional[NodeType] = None) -> List[ScientificNode]`
- Need `list_edges(edge_type: Optional[EdgeType] = None) -> List[Edge]`
- Need `add_verification_record(record: VerificationRecord) -> None`
- Need `get_verification_records(claim_id: str) -> List[VerificationRecord]`
- Need `add_mcts_search_run(run: MCTSSearchRun) -> None`
- Need `get_mcts_search_runs(claim_id: str) -> List[MCTSSearchRun]`

---

## 4. Detailed Proposed Code Changes

### 4.1 Proposed Schemas for `axiom/core/knowledge_graph/schema.py`
```python
class CircularDependencyError(Exception):
    """Raised when an edge insertion introduces a cycle in logical dependencies."""
    pass

class VerificationRecord(BaseModel):
    record_id: str = Field(..., description="Unique record identifier")
    claim_id: str = Field(..., description="ID of the mathematical claim verified")
    verifier_type: str = Field(..., description="Verifier system name (e.g. SMT_Z3, LEAN4_CHECKER)")
    status: EpistemicStatus = Field(..., description="Resulting epistemic status")
    tier: VerificationTier = Field(..., description="Verification tier achieved")
    counterexample: Optional[Dict[str, Any]] = Field(default=None, description="Counterexample payload if refuted")
    execution_time_ms: int = Field(default=0, description="Verification latency in milliseconds")
    timestamp: str = Field(..., description="ISO 8601 timestamp of execution")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional verification metadata")

class MCTSSearchRun(BaseModel):
    run_id: str = Field(..., description="Unique search run identifier")
    claim_id: str = Field(..., description="Target claim ID being searched")
    status: str = Field(..., description="Status of the MCTS run (RUNNING, SUCCESS, FAILED, EXHAUSTED)")
    iterations: int = Field(default=0, description="Number of MCTS iterations completed")
    proof_script: Optional[str] = Field(default=None, description="Discovered formal proof script if successful")
    created_at: str = Field(..., description="ISO 8601 start timestamp")
    completed_at: Optional[str] = Field(default=None, description="ISO 8601 completion timestamp")
```

### 4.2 Proposed Cycle Guard Logic for `axiom/core/knowledge_graph/db.py`
```python
LOGICAL_EDGE_TYPES = {
    EdgeType.PROVES,
    EdgeType.EXTENDS,
    EdgeType.USES_METHOD,
    "PROVES",
    "EXTENDS",
    "USES_METHOD"
}

def add_edge(self, edge: Edge, check_cycles: bool = True) -> None:
    """Upsert an edge in the database with foreign key and cycle prevention checks."""
    if not self.node_exists(edge.source_id) or not self.node_exists(edge.target_id):
        raise ValueError(
            f"Cannot create edge {edge.source_id} -> {edge.target_id}. One or both nodes do not exist."
        )

    edge_type_str = edge.type.value if isinstance(edge.type, EdgeType) else str(edge.type)

    if check_cycles and edge_type_str in LOGICAL_EDGE_TYPES:
        if edge.source_id == edge.target_id:
            raise CircularDependencyError(
                f"Self-loop detected: cannot add edge {edge.source_id} -> {edge.target_id} of type '{edge_type_str}'."
            )
        
        # Build logical graph from current database state
        G = self.to_networkx()
        logical_edges = [
            (u, v) for u, v, d in G.edges(data=True)
            if d.get("type") in LOGICAL_EDGE_TYPES
        ]
        logical_G = nx.DiGraph(logical_edges)
        
        if logical_G.has_node(edge.target_id) and logical_G.has_node(edge.source_id):
            if nx.has_path(logical_G, edge.target_id, edge.source_id):
                raise CircularDependencyError(
                    f"Circular dependency detected: adding edge {edge.source_id} -> {edge.target_id} "
                    f"of type '{edge_type_str}' introduces a cycle in logical dependencies."
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
            (edge.source_id, edge.target_id, edge_type_str, edge.confidence, prov_json)
        )
```

---

## 5. Test Strategy & Test Plan

### 5.1 Test Coverage Goals
- **Target File**: `tests/test_graph_store.py` (and existing `tests/test_epistemic_layer.py`).
- **Target Line Coverage**: 100% of `axiom/core/knowledge_graph/db.py` and `schema.py`.

### 5.2 Test Cases
1. `test_schema_models()`: Validates Pydantic serialization/deserialization for `VerificationRecord`, `MCTSSearchRun`, and polymorphic nodes.
2. `test_db_initialization()`: Verifies that tables `nodes`, `edges`, `verification_records`, and `mcts_search_runs` along with their indexes are created.
3. `test_node_edge_crud()`: Tests upserting, getting, listing (filtered by type), and deleting nodes and edges.
4. `test_verification_and_mcts_records()`: Tests adding and querying `VerificationRecord` and `MCTSSearchRun` entries tied to mathematical claims.
5. `test_circular_dependency_direct()`: Tests that $A \to B$ followed by $B \to A$ with `PROVES` raises `CircularDependencyError`.
6. `test_circular_dependency_indirect()`: Tests that $A \to B \to C$ followed by $C \to A$ with `EXTENDS`/`USES_METHOD` raises `CircularDependencyError`.
7. `test_non_logical_edges_allow_cycles()`: Tests that non-logical edges (e.g. `CITES`) permit cycles ($A \to B$ and $B \to A$) without raising exceptions.
8. `test_self_loop_rejection()`: Tests that $A \to A$ logical edges raise `CircularDependencyError`.

---

## 6. Implementation Sequence Recommendation
1. Update `axiom/core/knowledge_graph/schema.py` to add `CircularDependencyError`, `VerificationRecord`, and `MCTSSearchRun`.
2. Update `axiom/core/knowledge_graph/db.py` to include new DDL tables, cycle detection guard in `add_edge()`, and full CRUD methods.
3. Export new symbols in `axiom/core/knowledge_graph/__init__.py`.
4. Create/update `tests/test_graph_store.py` to execute all 8 test cases.
