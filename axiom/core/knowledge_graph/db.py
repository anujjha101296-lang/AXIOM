import json
import sqlite3
from typing import List, Optional, Tuple, Dict, Any
import networkx as nx
from pydantic import TypeAdapter

from axiom.core.knowledge_graph.schema import (
    ScientificNode,
    Edge,
    NodeType,
    EdgeType,
    KnowledgeGraph
)

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
        
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    provenance TEXT,
                    PRIMARY KEY (source_id, target_id, type),
                    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
                );
            """)
            
            # Indexes for efficient graph traversal
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);")

    def add_node(self, node: ScientificNode) -> None:
        """Upsert a scientific node in the database."""
        node_json = node.model_dump_json()
        assert self.conn is not None
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
                (node.id, node.type.value, node.name, node_json)
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
