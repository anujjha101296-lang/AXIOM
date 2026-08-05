# Analysis: EpistemicStore & Test Strategy for Milestone 1 (EGS Mathematical Ontology & Database Migrations)

**Author:** Explorer 3 (Milestone 1)  
**Target Files:** `axiom/core/knowledge_graph/db.py`, `tests/test_mde_ontology.py`  
**Date:** 2026-08-05  

---

## Executive Summary

This report presents a thorough investigation of `EpistemicStore` in `axiom/core/knowledge_graph/db.py` and establishes the complete architecture and test strategy for `tests/test_mde_ontology.py` under Milestone 1 (EGS Mathematical Ontology & Database Migrations). 

Key findings:
1. `EpistemicStore._init_db()` currently executes hardcoded inline DDL (`nodes` and `edges`) rather than delegating database initialization to `axiom.core.knowledge_graph.migrations.run_migrations()`. Updating `_init_db()` to invoke `run_migrations(self.conn)` guarantees automatic, idempotent execution of all schema versions (v1 through v4).
2. The polymorphic node deserialization mechanism (`scientific_node_adapter = TypeAdapter(ScientificNode)`) in `db.py` relies on Pydantic's discriminated union. Once Explorer 1 adds `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, and `ConjectureNode` to `schema.py`, `EpistemicStore.get_node()` will transparently parse all new node types without structural changes to generic node methods.
3. To fully support Milestone 1 through Milestone 7 requirements (such as theorem retrieval, MCTS failure tactic pruning, equivalent statement tracking, and working memory snapshotting), `EpistemicStore` requires specialized querying and insertion methods for the new v4 tables (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`).
4. A comprehensive unit test suite in `tests/test_mde_ontology.py` with 6 test groups must be created to validate migration execution, foreign key integrity, cascade deletions, polymorphic node/edge serialization, and table-specific CRUD operations.

---

## 1. EpistemicStore Architecture & Mechanism Analysis

### 1.1 Connection & Session Management
- **Driver & Context:** `EpistemicStore` initializes `sqlite3.connect(self.db_path, check_same_thread=False)`.
- **Foreign Key Enforcement:** SQLite does not enable foreign key constraint checking by default. `EpistemicStore._init_db()` executes `PRAGMA foreign_keys = ON;` upon establishing the connection.
- **Transaction Controls:** Transactions are managed via Python's `with self.conn:` context manager blocks in `add_node()`, `add_edge()`, etc. This ensures atomicity: statement execution commits on block exit and rolls back upon uncaught exceptions.
- **In-Memory vs File-Based:** `EpistemicStore` supports both file paths and `:memory:`. In-memory databases exist solely for the lifetime of `self.conn`, making proper connection lifecycle management essential for unit tests.

### 1.2 Migration Execution Mechanism
Currently, `_init_db()` executes:
```python
CREATE TABLE IF NOT EXISTS nodes (...);
CREATE TABLE IF NOT EXISTS edges (...);
```
**Architectural Recommendation:**  
Replace the hardcoded DDL inside `_init_db()` with a call to `run_migrations(self.conn)`. This ensures that:
- Table versioning is tracked in `_schema_migrations`.
- Version 1 (`nodes`, `edges`), Version 2 (`proof_lineage`), Version 3 (`memory_snapshots`), and Version 4 (`mathematical_objects`, `definitions`, `equivalent_statements`, `failed_proof_attempts`) execute in sequential, idempotent order.

### 1.3 Polymorphic Node Serialization Architecture
- Nodes are stored in the SQLite `nodes` table with `id`, `type`, `name`, and `data` (JSON string).
- In `db.py`, `scientific_node_adapter = TypeAdapter(ScientificNode)` handles JSON serialization and deserialization.
- `ScientificNode` is defined in `schema.py` as an `Annotated[Union[...], Field(discriminator='type')]`.
- When `add_node(node)` is called, `node.model_dump_json()` writes the node's fields (including `type`) into `nodes.data`.
- When `get_node(node_id)` is called, `scientific_node_adapter.validate_json(row[0])` inspects the `type` field in the JSON payload and instantiates the correct subclass (`MathematicalClaimNode`, `MathematicalObjectNode`, `DefinitionNode`, etc.).

### 1.4 Foreign Key Integrity & Cascade Dynamics
- `edges`, `proof_lineage`, `mathematical_objects`, `definitions`, `equivalent_statements`, and `failed_proof_attempts` specify `FOREIGN KEY (...) REFERENCES nodes(id) ON DELETE CASCADE`.
- With `PRAGMA foreign_keys = ON;` active, attempts to insert referencing records with non-existent `node_id` values trigger a `sqlite3.IntegrityError`.
- Deleting a parent node from `nodes` automatically cascades to purge all referencing edges and specialized table entries, preventing orphaned records.

---

## 2. Proposed Design & Updates for `axiom/core/knowledge_graph/db.py`

### 2.1 Interface & Method Enhancements
To support MDE features across Milestones 1–7, `EpistemicStore` should be updated with the following methods:

1. **Migration Integration in `_init_db()`**
   ```python
   def _init_db(self):
       self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
       self.conn.execute("PRAGMA foreign_keys = ON;")
       from axiom.core.knowledge_graph.migrations import run_migrations
       run_migrations(self.conn)
   ```

2. **Typed Node & Edge Retrieval**
   - `get_nodes_by_type(node_type: Union[NodeType, str]) -> List[ScientificNode]`: Query nodes filtered by `type`.
   - `get_edges_by_type(edge_type: Union[EdgeType, str]) -> List[Edge]`: Query edges filtered by `type`.

3. **Specialized Table Helper Methods**
   - `add_mathematical_object(...)` & `get_mathematical_object(node_id)`
   - `add_definition(...)` & `get_definition(node_id)`
   - `add_equivalent_statement(...)` & `get_equivalent_statements(node_id)`
   - `save_memory_snapshot(...)` & `get_memory_snapshots(session_id)`
   - `add_failed_proof_attempt(...)` & `get_failed_proof_attempts(claim_id)`

### 2.2 Complete Code Specification for `axiom/core/knowledge_graph/db.py`

```python
import json
import sqlite3
from typing import List, Optional, Tuple, Dict, Any, Union
import networkx as nx
from pydantic import TypeAdapter

from axiom.core.knowledge_graph.schema import (
    ScientificNode,
    Edge,
    NodeType,
    EdgeType,
    KnowledgeGraph,
    MathematicalObjectNode,
    DefinitionNode,
    OpenProblemNode,
    ConjectureNode,
)
from axiom.core.knowledge_graph.migrations import run_migrations

# Type adapter for polymorphic node validation
scientific_node_adapter = TypeAdapter(ScientificNode)


class EpistemicStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        run_migrations(self.conn)

    def add_node(self, node: ScientificNode) -> None:
        """Upsert a scientific node in the database."""
        node_json = node.model_dump_json()
        assert self.conn is not None
        type_val = node.type.value if isinstance(node.type, Enum) else str(node.type)
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO nodes (id, type, name, data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type = excluded.type,
                    name = excluded.name,
                    data = excluded.data;
                """,
                (node.id, type_val, node.name, node_json)
            )

    def add_edge(self, edge: Edge) -> None:
        """Upsert an edge in the database, verifying target/source nodes exist."""
        prov_json = json.dumps(edge.provenance)
        assert self.conn is not None
        
        if not self.node_exists(edge.source_id) or not self.node_exists(edge.target_id):
            raise ValueError(
                f"Cannot create edge {edge.source_id} -> {edge.target_id}. One or both nodes do not exist."
            )

        type_val = edge.type.value if isinstance(edge.type, Enum) else str(edge.type)
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO edges (source_id, target_id, type, confidence, provenance)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, type) DO UPDATE SET
                    confidence = excluded.confidence,
                    provenance = excluded.provenance;
                """,
                (edge.source_id, edge.target_id, type_val, edge.confidence, prov_json)
            )

    def node_exists(self, node_id: str) -> bool:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM nodes WHERE id = ?;", (node_id,))
        return cursor.fetchone() is not None

    def get_node(self, node_id: str) -> Optional[ScientificNode]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM nodes WHERE id = ?;", (node_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return scientific_node_adapter.validate_json(row[0])

    def get_nodes_by_type(self, node_type: Union[NodeType, str]) -> List[ScientificNode]:
        assert self.conn is not None
        type_str = node_type.value if hasattr(node_type, "value") else str(node_type)
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM nodes WHERE type = ?;", (type_str,))
        return [scientific_node_adapter.validate_json(row[0]) for row in cursor.fetchall()]

    def get_edge(self, source_id: str, target_id: str, edge_type: str) -> Optional[Edge]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT source_id, target_id, type, confidence, provenance FROM edges WHERE source_id = ? AND target_id = ? AND type = ?;",
            (source_id, target_id, edge_type)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Edge(
            source_id=row[0],
            target_id=row[1],
            type=EdgeType(row[2]),
            confidence=row[3],
            provenance=json.loads(row[4]) if row[4] else {}
        )

    def get_edges_by_type(self, edge_type: Union[EdgeType, str]) -> List[Edge]:
        assert self.conn is not None
        type_str = edge_type.value if hasattr(edge_type, "value") else str(edge_type)
        cursor = self.conn.cursor()
        cursor.execute("SELECT source_id, target_id, type, confidence, provenance FROM edges WHERE type = ?;", (type_str,))
        results = []
        for row in cursor.fetchall():
            results.append(Edge(
                source_id=row[0],
                target_id=row[1],
                type=EdgeType(row[2]),
                confidence=row[3],
                provenance=json.loads(row[4]) if row[4] else {}
            ))
        return results

    def get_neighbors(self, node_id: str, direction: str = "outgoing") -> List[Tuple[Edge, ScientificNode]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        if direction == "outgoing":
            query = """
                SELECT e.source_id, e.target_id, e.type, e.confidence, e.provenance, n.data
                FROM edges e
                JOIN nodes n ON e.target_id = n.id
                WHERE e.source_id = ?;
            """
        elif direction == "incoming":
            query = """
                SELECT e.source_id, e.target_id, e.type, e.confidence, e.provenance, n.data
                FROM edges e
                JOIN nodes n ON e.source_id = n.id
                WHERE e.target_id = ?;
            """
        else:
            raise ValueError("Direction must be either 'outgoing' or 'incoming'")

        cursor.execute(query, (node_id,))
        results = []
        for row in cursor.fetchall():
            edge = Edge(
                source_id=row[0],
                target_id=row[1],
                type=EdgeType(row[2]),
                confidence=row[3],
                provenance=json.loads(row[4]) if row[4] else {}
            )
            node = scientific_node_adapter.validate_json(row[5])
            results.append((edge, node))
        return results

    # Specialized Table Operations (v4)

    def add_mathematical_object(
        self,
        node: MathematicalObjectNode,
        object_type: str,
        formal_symbol: Optional[str] = None,
        domain: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.add_node(node)
        props_json = json.dumps(properties) if properties else "{}"
        assert self.conn is not None
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO mathematical_objects (id, node_id, object_type, formal_symbol, domain, properties_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    object_type = excluded.object_type,
                    formal_symbol = excluded.formal_symbol,
                    domain = excluded.domain,
                    properties_json = excluded.properties_json;
                """,
                (node.id, node.id, object_type, formal_symbol, domain, props_json)
            )

    def get_mathematical_object(self, node_id: str) -> Optional[Dict[str, Any]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT mo.id, mo.node_id, mo.object_type, mo.formal_symbol, mo.domain, mo.properties_json, n.data
            FROM mathematical_objects mo
            JOIN nodes n ON mo.node_id = n.id
            WHERE mo.node_id = ?;
            """,
            (node_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "node_id": row[1],
            "object_type": row[2],
            "formal_symbol": row[3],
            "domain": row[4],
            "properties": json.loads(row[5]) if row[5] else {},
            "node": scientific_node_adapter.validate_json(row[6]),
        }

    def add_definition(
        self,
        node: DefinitionNode,
        term: str,
        formal_definition: str,
        informal_definition: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> None:
        self.add_node(node)
        assert self.conn is not None
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO definitions (id, node_id, term, formal_definition, informal_definition, domain)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    term = excluded.term,
                    formal_definition = excluded.formal_definition,
                    informal_definition = excluded.informal_definition,
                    domain = excluded.domain;
                """,
                (node.id, node.id, term, formal_definition, informal_definition, domain)
            )

    def get_definition(self, node_id: str) -> Optional[Dict[str, Any]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.node_id, d.term, d.formal_definition, d.informal_definition, d.domain, n.data
            FROM definitions d
            JOIN nodes n ON d.node_id = n.id
            WHERE d.node_id = ?;
            """,
            (node_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "node_id": row[1],
            "term": row[2],
            "formal_definition": row[3],
            "informal_definition": row[4],
            "domain": row[5],
            "node": scientific_node_adapter.validate_json(row[6]),
        }

    def add_equivalent_statement(
        self,
        statement_a_id: str,
        statement_b_id: str,
        proof_reference: Optional[str] = None,
        confidence: float = 1.0,
    ) -> str:
        if not self.node_exists(statement_a_id) or not self.node_exists(statement_b_id):
            raise ValueError(f"Cannot create equivalence between {statement_a_id} and {statement_b_id}. One or both nodes do not exist.")
        eq_id = f"eq_{statement_a_id}_{statement_b_id}"
        assert self.conn is not None
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO equivalent_statements (id, statement_a_id, statement_b_id, proof_reference, confidence)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    proof_reference = excluded.proof_reference,
                    confidence = excluded.confidence;
                """,
                (eq_id, statement_a_id, statement_b_id, proof_reference, confidence)
            )
        # Also maintain graph edge representation
        self.add_edge(Edge(source_id=statement_a_id, target_id=statement_b_id, type=EdgeType.EQUIVALENT_TO, confidence=confidence))
        return eq_id

    def get_equivalent_statements(self, node_id: str) -> List[str]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT statement_b_id FROM equivalent_statements WHERE statement_a_id = ?
            UNION
            SELECT statement_a_id FROM equivalent_statements WHERE statement_b_id = ?;
            """,
            (node_id, node_id)
        )
        return [row[0] for row in cursor.fetchall()]

    def save_memory_snapshot(self, session_id: str, snapshot_data: Dict[str, Any]) -> int:
        assert self.conn is not None
        snap_json = json.dumps(snapshot_data)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO memory_snapshots (session_id, snapshot) VALUES (?, ?);",
                (session_id, snap_json)
            )
            return cursor.lastrowid

    def get_memory_snapshots(self, session_id: str) -> List[Dict[str, Any]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, session_id, snapshot, created_at FROM memory_snapshots WHERE session_id = ? ORDER BY id ASC;",
            (session_id,)
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "session_id": row[1],
                "snapshot": json.loads(row[2]),
                "created_at": row[3],
            })
        return results

    def add_failed_proof_attempt(
        self,
        claim_id: str,
        tactic_sequence: List[str],
        verifier: str,
        error_message: Optional[str] = None,
    ) -> int:
        if not self.node_exists(claim_id):
            raise ValueError(f"Claim node {claim_id} does not exist.")
        assert self.conn is not None
        tactics_json = json.dumps(tactic_sequence)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO failed_proof_attempts (claim_id, tactic_sequence, verifier, error_message)
                VALUES (?, ?, ?, ?);
                """,
                (claim_id, tactics_json, verifier, error_message)
            )
            return cursor.lastrowid

    def get_failed_proof_attempts(self, claim_id: str) -> List[Dict[str, Any]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, claim_id, tactic_sequence, verifier, error_message, created_at
            FROM failed_proof_attempts
            WHERE claim_id = ?
            ORDER BY id ASC;
            """,
            (claim_id,)
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "claim_id": row[1],
                "tactic_sequence": json.loads(row[2]),
                "verifier": row[3],
                "error_message": row[4],
                "created_at": row[5],
            })
        return results

    def to_networkx(self) -> nx.DiGraph:
        assert self.conn is not None
        cursor = self.conn.cursor()
        G = nx.DiGraph()

        cursor.execute("SELECT id, data FROM nodes;")
        for row in cursor.fetchall():
            node_id, data_str = row
            G.add_node(node_id, **json.loads(data_str))

        cursor.execute("SELECT source_id, target_id, type, confidence, provenance FROM edges;")
        for row in cursor.fetchall():
            source_id, target_id, edge_type, confidence, prov_str = row
            G.add_edge(
                source_id, 
                target_id, 
                type=edge_type, 
                confidence=confidence, 
                provenance=json.loads(prov_str) if prov_str else {}
            )
        return G

    def load_knowledge_graph(self, kg: KnowledgeGraph) -> None:
        for node in kg.nodes:
            self.add_node(node)
        for edge in kg.edges:
            self.add_edge(edge)

    def export_knowledge_graph(self) -> KnowledgeGraph:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM nodes;")
        nodes = [scientific_node_adapter.validate_json(row[0]) for row in cursor.fetchall()]
        
        cursor.execute("SELECT source_id, target_id, type, confidence, provenance FROM edges;")
        edges = []
        for row in cursor.fetchall():
            edges.append(Edge(
                source_id=row[0],
                target_id=row[1],
                type=EdgeType(row[2]),
                confidence=row[3],
                provenance=json.loads(row[4]) if row[4] else {}
            ))
        return KnowledgeGraph(nodes=nodes, edges=edges)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
```

---

## 3. Comprehensive Test Strategy for `tests/test_mde_ontology.py`

### 3.1 Test Suite Structure
The test file `tests/test_mde_ontology.py` should be organized into six logical test groups using standard `pytest` fixtures.

#### Group 1: Migration Execution & Idempotency
- `test_v4_migration_creates_all_tables(temp_db)`:
  Queries `sqlite_master` to verify the presence of `_schema_migrations`, `nodes`, `edges`, `proof_lineage`, `memory_snapshots`, `mathematical_objects`, `definitions`, `equivalent_statements`, and `failed_proof_attempts`.
- `test_migrations_idempotent(temp_db)`:
  Runs `run_migrations(temp_db.conn)` multiple times and asserts no exception is raised and migration counts remain unchanged.

#### Group 2: Foreign Key Constraints & Cascade Operations
- `test_fk_constraint_enforcement_on_edges(temp_db)`:
  Attempts to insert an edge referencing an unadded `source_id` or `target_id`, expecting `ValueError` or `sqlite3.IntegrityError`.
- `test_fk_constraint_enforcement_on_specialized_tables(temp_db)`:
  Directly executes SQL INSERT into `mathematical_objects`, `definitions`, or `failed_proof_attempts` with a invalid `node_id`, expecting `sqlite3.IntegrityError`.
- `test_cascade_delete_removes_related_records(temp_db)`:
  Inserts a node and associated records across `edges`, `mathematical_objects`, `definitions`, and `failed_proof_attempts`. Deletes the node from `nodes` and verifies all referencing rows across all tables are automatically removed.

#### Group 3: Schema Model Polymorphism & Serialization
- `test_mathematical_object_node_roundtrip(temp_db)`:
  Instantiates `MathematicalObjectNode`, saves to store via `add_node()`, retrieves via `get_node()`, and verifies exact equality of properties.
- `test_definition_node_roundtrip(temp_db)`:
  Instantiates `DefinitionNode`, validates round-trip JSON serialization.
- `test_open_problem_node_roundtrip(temp_db)`:
  Instantiates `OpenProblemNode`, validates properties and status.
- `test_conjecture_node_roundtrip(temp_db)`:
  Instantiates `ConjectureNode`, validates verification tier and epistemic status.

#### Group 4: Node and Edge Type Queries
- `test_get_nodes_by_type(temp_db)`:
  Stores a mix of node types and verifies `get_nodes_by_type(NodeType.MATHEMATICAL_OBJECT)` returns only `MathematicalObjectNode` instances.
- `test_get_edges_by_type(temp_db)`:
  Stores edges with `EQUIVALENT_TO`, `DEPENDS_ON`, `COUNTEREXAMPLE_FOR` and verifies filtering.

#### Group 5: Specialized Table CRUD Operations
- `test_add_and_get_mathematical_object(temp_db)`:
  Tests `add_mathematical_object()` and `get_mathematical_object()`.
- `test_add_and_get_definition(temp_db)`:
  Tests `add_definition()` and `get_definition()`.
- `test_add_and_get_equivalent_statements(temp_db)`:
  Tests `add_equivalent_statement()` and `get_equivalent_statements()`.
- `test_memory_snapshots(temp_db)`:
  Tests `save_memory_snapshot()` and `get_memory_snapshots()`.
- `test_failed_proof_attempts(temp_db)`:
  Tests `add_failed_proof_attempt()` and `get_failed_proof_attempts()`.

#### Group 6: NetworkX Graph Topology Integration
- `test_to_networkx_with_mde_ontology(temp_db)`:
  Verifies that `to_networkx()` correctly constructs a `nx.DiGraph` containing new node types and edges, preserving metadata.

### 3.2 Implementation Blueprint for `tests/test_mde_ontology.py`

```python
import pytest
import sqlite3
import json
import networkx as nx

from axiom.core.knowledge_graph.schema import (
    NodeType,
    EdgeType,
    EpistemicStatus,
    VerificationTier,
    MathematicalObjectNode,
    DefinitionNode,
    OpenProblemNode,
    ConjectureNode,
    MathematicalClaimNode,
    Edge,
)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status


@pytest.fixture
def temp_db():
    store = EpistemicStore(":memory:")
    yield store
    store.close()


def test_v4_migration_creates_all_tables(temp_db):
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        "_schema_migrations",
        "nodes",
        "edges",
        "proof_lineage",
        "memory_snapshots",
        "mathematical_objects",
        "definitions",
        "equivalent_statements",
        "failed_proof_attempts",
    }
    assert expected_tables.issubset(tables)
    
    status = migration_status(temp_db.conn)
    v4_status = next((m for m in status if m["version"] == 4), None)
    assert v4_status is not None
    assert v4_status["status"] == "applied"


def test_migrations_idempotent(temp_db):
    # Running migrations again should be completely safe
    run_migrations(temp_db.conn)
    run_migrations(temp_db.conn)
    
    status = migration_status(temp_db.conn)
    assert len(status) >= 4
    for m in status:
        assert m["status"] == "applied"


def test_fk_constraint_enforcement(temp_db):
    node_a = MathematicalClaimNode(id="claim_1", name="Claim 1", statement="1+1=2")
    temp_db.add_node(node_a)
    
    # Adding edge to non-existent target raises ValueError in EpistemicStore
    with pytest.raises(ValueError):
        temp_db.add_edge(Edge(source_id="claim_1", target_id="missing_node", type=EdgeType.PROVES))
        
    # Direct DB execution without parent node triggers SQLite FK violation
    with pytest.raises(sqlite3.IntegrityError):
        with temp_db.conn:
            temp_db.conn.execute(
                "INSERT INTO failed_proof_attempts (claim_id, tactic_sequence, verifier) VALUES (?, ?, ?);",
                ("non_existent_claim", "[]", "LEAN")
            )


def test_cascade_delete_removes_related_records(temp_db):
    claim_id = "claim_cascade_test"
    claim_node = MathematicalClaimNode(id=claim_id, name="Cascade Test", statement="Test")
    temp_db.add_node(claim_node)
    
    target_node = MathematicalClaimNode(id="target_claim", name="Target Claim", statement="Target")
    temp_db.add_node(target_node)
    
    # Add edge and failed proof attempt
    temp_db.add_edge(Edge(source_id=claim_id, target_id="target_claim", type=EdgeType.PROVES))
    temp_db.add_failed_proof_attempt(claim_id, ["simp", "ring"], "LEAN")
    
    # Verify records exist before delete
    assert len(temp_db.get_failed_proof_attempts(claim_id)) == 1
    assert temp_db.get_edge(claim_id, "target_claim", "PROVES") is not None
    
    # Delete parent claim node directly
    with temp_db.conn:
        temp_db.conn.execute("DELETE FROM nodes WHERE id = ?;", (claim_id,))
        
    # Verify child records were cascade deleted
    assert len(temp_db.get_failed_proof_attempts(claim_id)) == 0
    assert temp_db.get_edge(claim_id, "target_claim", "PROVES") is None


def test_mathematical_object_node_roundtrip(temp_db):
    obj_node = MathematicalObjectNode(
        id="obj_riemann_zeta",
        name="Riemann Zeta Function",
        domain="ANALYTIC_NUMBER_THEORY",
        formal_symbol="\\zeta(s)",
        properties={"analytic_continuation": True, "euler_product": True}
    )
    temp_db.add_node(obj_node)
    
    retrieved = temp_db.get_node("obj_riemann_zeta")
    assert retrieved is not None
    assert isinstance(retrieved, MathematicalObjectNode)
    assert retrieved.name == "Riemann Zeta Function"
    assert retrieved.domain == "ANALYTIC_NUMBER_THEORY"
    assert retrieved.properties["analytic_continuation"] is True


def test_definition_node_roundtrip(temp_db):
    def_node = DefinitionNode(
        id="def_zeta_zero",
        name="Non-trivial Zero",
        term="Zeta Zero",
        definition="A zero s of zeta(s) lying in the critical strip 0 < Re(s) < 1.",
        formal_definition="\\zeta(s) = 0 \\land 0 < \\text{Re}(s) < 1",
        domain="ANALYTIC_NUMBER_THEORY"
    )
    temp_db.add_node(def_node)
    
    retrieved = temp_db.get_node("def_zeta_zero")
    assert retrieved is not None
    assert isinstance(retrieved, DefinitionNode)
    assert retrieved.term == "Zeta Zero"


def test_open_problem_node_roundtrip(temp_db):
    problem_node = OpenProblemNode(
        id="prob_riemann_hypothesis",
        name="Riemann Hypothesis",
        description="All non-trivial zeros of the Riemann zeta function have real part 1/2.",
        formal_statement="\\forall s \\in \\mathbb{C}, (\\zeta(s) = 0 \\land 0 < \\text{Re}(s) < 1) \\implies \\text{Re}(s) = 1/2",
        prize_amount="$1,000,000"
    )
    temp_db.add_node(problem_node)
    
    retrieved = temp_db.get_node("prob_riemann_hypothesis")
    assert retrieved is not None
    assert isinstance(retrieved, OpenProblemNode)
    assert retrieved.prize_amount == "$1,000,000"


def test_conjecture_node_roundtrip(temp_db):
    conj_node = ConjectureNode(
        id="conj_dirichlet_l",
        name="Generalized Riemann Hypothesis",
        statement="All non-trivial zeros of Dirichlet L-functions have real part 1/2.",
        status=EpistemicStatus.CONJECTURED,
        tier=VerificationTier.TIER_0_CONJECTURE
    )
    temp_db.add_node(conj_node)
    
    retrieved = temp_db.get_node("conj_dirichlet_l")
    assert retrieved is not None
    assert isinstance(retrieved, ConjectureNode)
    assert retrieved.status == EpistemicStatus.CONJECTURED


def test_get_nodes_by_type(temp_db):
    obj = MathematicalObjectNode(id="obj_1", name="Group", domain="ALGEBRA", formal_symbol="G")
    def_node = DefinitionNode(id="def_1", name="Ring Def", term="Ring", definition="Ring def")
    temp_db.add_node(obj)
    temp_db.add_node(def_node)
    
    objects = temp_db.get_nodes_by_type(NodeType.MATHEMATICAL_OBJECT)
    assert len(objects) == 1
    assert objects[0].id == "obj_1"
    
    definitions = temp_db.get_nodes_by_type(NodeType.DEFINITION)
    assert len(definitions) == 1
    assert definitions[0].id == "def_1"


def test_specialized_mathematical_object_operations(temp_db):
    obj_node = MathematicalObjectNode(
        id="obj_field",
        name="Galois Field",
        domain="ALGEBRA",
        formal_symbol="GF(p^n)"
    )
    temp_db.add_mathematical_object(
        node=obj_node,
        object_type="FIELD",
        formal_symbol="GF(p^n)",
        domain="ALGEBRA",
        properties={"characteristic": "p", "finite": True}
    )
    
    mo_record = temp_db.get_mathematical_object("obj_field")
    assert mo_record is not None
    assert mo_record["object_type"] == "FIELD"
    assert mo_record["properties"]["finite"] is True
    assert mo_record["node"].name == "Galois Field"


def test_specialized_definition_operations(temp_db):
    def_node = DefinitionNode(
        id="def_prime",
        name="Prime Number",
        term="Prime",
        definition="An integer greater than 1 divisible only by 1 and itself."
    )
    temp_db.add_definition(
        node=def_node,
        term="Prime",
        formal_definition="p > 1 \\land (d | p \\implies d = 1 \\lor d = p)",
        informal_definition="A prime number",
        domain="NUMBER_THEORY"
    )
    
    def_record = temp_db.get_definition("def_prime")
    assert def_record is not None
    assert def_record["term"] == "Prime"
    assert def_record["domain"] == "NUMBER_THEORY"


def test_equivalent_statements_operations(temp_db):
    stmt1 = MathematicalClaimNode(id="stmt_1", name="RH Form 1", statement="Zeta zero real part is 1/2")
    stmt2 = MathematicalClaimNode(id="stmt_2", name="RH Form 2", statement="Prime number theorem error bound")
    temp_db.add_node(stmt1)
    temp_db.add_node(stmt2)
    
    eq_id = temp_db.add_equivalent_statement("stmt_1", "stmt_2", proof_reference="Koch (1901)")
    assert eq_id == "eq_stmt_1_stmt_2"
    
    eq_from_1 = temp_db.get_equivalent_statements("stmt_1")
    assert "stmt_2" in eq_from_1
    
    eq_from_2 = temp_db.get_equivalent_statements("stmt_2")
    assert "stmt_1" in eq_from_2
    
    edge = temp_db.get_edge("stmt_1", "stmt_2", "EQUIVALENT_TO")
    assert edge is not None


def test_memory_snapshots_operations(temp_db):
    snap_id = temp_db.save_memory_snapshot("session_123", {"searched_tactics": ["ring", "linarith"], "score": 0.95})
    assert snap_id > 0
    
    snapshots = temp_db.get_memory_snapshots("session_123")
    assert len(snapshots) == 1
    assert snapshots[0]["snapshot"]["score"] == 0.95


def test_failed_proof_attempts_operations(temp_db):
    claim = MathematicalClaimNode(id="claim_failed_test", name="Failed Test Claim", statement="False claim")
    temp_db.add_node(claim)
    
    attempt_id = temp_db.add_failed_proof_attempt(
        claim_id="claim_failed_test",
        tactic_sequence=["intro h", "induction h", "contradiction"],
        verifier="LEAN",
        error_message="tactic failed"
    )
    assert attempt_id > 0
    
    attempts = temp_db.get_failed_proof_attempts("claim_failed_test")
    assert len(attempts) == 1
    assert attempts[0]["tactic_sequence"] == ["intro h", "induction h", "contradiction"]
    assert attempts[0]["verifier"] == "LEAN"


def test_to_networkx_with_mde_nodes(temp_db):
    obj = MathematicalObjectNode(id="node_obj", name="Group G", domain="ALGEBRA")
    conj = ConjectureNode(id="node_conj", name="Conjecture C", statement="G is abelian")
    temp_db.add_node(obj)
    temp_db.add_node(conj)
    
    temp_db.add_edge(Edge(source_id="node_conj", target_id="node_obj", type=EdgeType.DEPENDS_ON))
    
    G = temp_db.to_networkx()
    assert isinstance(G, nx.DiGraph)
    assert G.has_node("node_obj")
    assert G.has_node("node_conj")
    assert G.has_edge("node_conj", "node_obj")
    assert G.edges["node_conj", "node_obj"]["type"] == "DEPENDS_ON"
```

---

## 4. Risk Analysis & Recommendations for Implementers

1. **Import Ordering & Circular Dependencies:**  
   `db.py` imports `run_migrations` from `migrations.py`. `migrations.py` does not import `EpistemicStore`. To avoid potential circular import issues, `run_migrations` can be imported inside `_init_db()` or at module top-level after confirming clean module execution.
2. **Enum vs String Normalization:**  
   In `add_node()`, `add_edge()`, `get_nodes_by_type()`, and `get_edges_by_type()`, `NodeType` and `EdgeType` inputs should accept both standard strings and Enum instances via `getattr(val, "value", str(val))` normalization.
3. **Foreign Key Error Handling:**  
   `add_edge()`, `add_equivalent_statement()`, and `add_failed_proof_attempt()` check node existence via `node_exists()` before database insertion. This provides clear Python `ValueError` diagnostics rather than unhandled SQLite internal driver exceptions.
