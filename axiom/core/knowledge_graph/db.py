import json
import sqlite3
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any, Union
try:
    import networkx as nx
except ImportError:
    nx = None
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
# Migrations now handled by alembic

# Set up type adapter for polymorphic nodes list parsing
scientific_node_adapter = TypeAdapter(ScientificNode)

class EpistemicStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        # Migrations now handled by alembic

    def add_node(self, node: ScientificNode) -> None:
        """Upsert a scientific node in the database."""
        node_json = node.model_dump_json()
        assert self.conn is not None
        type_val = node.type.value if hasattr(node.type, "value") else str(node.type)
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
        
        # Verify source and target exist first (to give a clean python error if violated)
        if not self.node_exists(edge.source_id) or not self.node_exists(edge.target_id):
            raise ValueError(
                f"Cannot create edge {edge.source_id} -> {edge.target_id}. One or both nodes do not exist."
            )

        type_val = edge.type.value if hasattr(edge.type, "value") else str(edge.type)
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
        """Get connected edges and nodes for a given node."""
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
        domain_val = domain or node.domain or ""
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
                (node.id, node.id, object_type, formal_symbol, domain_val, props_json)
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
        informal_description: Optional[str] = None,
        domain: Optional[str] = None,
        informal_definition: Optional[str] = None,
    ) -> None:
        self.add_node(node)
        assert self.conn is not None
        domain_val = domain or node.domain
        inf_desc = (
            informal_description
            if informal_description is not None
            else (informal_definition if informal_definition is not None else getattr(node, "informal_description", None))
        )
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
                (node.id, node.id, term, formal_definition, inf_desc, domain_val)
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
            "informal_description": row[4],
            "domain": row[5],
            "node": scientific_node_adapter.validate_json(row[6]),
        }

    def add_equivalent_statement(
        self,
        statement_a_id: str,
        statement_b_id: str,
        equivalence_type: str = "LOGICAL",
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
                INSERT INTO equivalent_statements (id, statement_a_id, statement_b_id, equivalence_type, proof_reference, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    proof_reference = excluded.proof_reference,
                    confidence = excluded.confidence;
                """,
                (eq_id, statement_a_id, statement_b_id, equivalence_type, proof_reference, confidence)
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

    def save_memory_snapshot(self, session_id: str, snapshot_data: Dict[str, Any], domain: Optional[str] = None) -> int:
        assert self.conn is not None
        snap_json = json.dumps(snapshot_data)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO memory_snapshots (session_id, snapshot, domain) VALUES (?, ?, ?);",
                (session_id, snap_json, domain)
            )
            return cursor.lastrowid

    def get_memory_snapshots(self, session_id: str) -> List[Dict[str, Any]]:
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, session_id, snapshot, domain, created_at FROM memory_snapshots WHERE session_id = ? ORDER BY id ASC;",
            (session_id,)
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "session_id": row[1],
                "snapshot": json.loads(row[2]),
                "domain": row[3],
                "created_at": row[4],
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
        """Construct a NetworkX directed graph from the database contents."""
        assert self.conn is not None
        cursor = self.conn.cursor()
        G = nx.DiGraph()

        # Add nodes
        cursor.execute("SELECT id, data FROM nodes;")
        for row in cursor.fetchall():
            node_id, data_str = row
            G.add_node(node_id, **json.loads(data_str))

        # Add edges
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
        """Bulk load a KnowledgeGraph schema object into SQLite."""
        for node in kg.nodes:
            self.add_node(node)
        for edge in kg.edges:
            self.add_edge(edge)

    def export_knowledge_graph(self) -> KnowledgeGraph:
        """Export the entire SQLite graph as a KnowledgeGraph schema object."""
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

