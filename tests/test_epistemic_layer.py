import pytest
import sqlite3
import tempfile
import os
import networkx as nx

from axiom.core.knowledge_graph.schema import (
    PaperNode,
    AuthorNode,
    MathematicalClaimNode,
    ConceptNode,
    Edge,
    EdgeType,
    EpistemicStatus,
    VerificationTier
)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.parser.arxiv_parser import ArxivParser
from axiom.core.parser.semantic_tracker import SemanticTracker

@pytest.fixture
def temp_db():
    # Use in-memory database for testing
    store = EpistemicStore(":memory:")
    yield store
    store.close()

def test_pydantic_schema():
    # Test valid Node definitions
    paper = PaperNode(
        id="hash_paper_1",
        name="A New Kind of Science",
        arxiv_id="2301.0001",
        abstract="We discuss computation in nature."
    )
    assert paper.type == "PAPER"
    assert paper.name == "A New Kind of Science"

    claim = MathematicalClaimNode(
        id="hash_claim_1",
        name="Theorem 1",
        statement="P != NP",
        status=EpistemicStatus.CONJECTURED,
        tier=VerificationTier.TIER_0_CONJECTURE
    )
    assert claim.type == "MATHEMATICAL_CLAIM"
    assert claim.status == EpistemicStatus.CONJECTURED
    assert claim.tier == VerificationTier.TIER_0_CONJECTURE

def test_db_persistence(temp_db):
    store = temp_db
    
    # Save a paper and author node
    author = AuthorNode(id="auth_1", name="Alonzo Church", orcid="0000-0002-1825-0097")
    paper = PaperNode(id="paper_1", name="An Unsolvable Problem of Elementary Number Theory", doi="10.2307/2371045")
    
    store.add_node(author)
    store.add_node(paper)
    
    # Verify nodes are saved
    retrieved_author = store.get_node("auth_1")
    assert retrieved_author is not None
    assert retrieved_author.name == "Alonzo Church"
    assert isinstance(retrieved_author, AuthorNode)

    # Save an edge linking author to paper
    edge = Edge(source_id="auth_1", target_id="paper_1", type=EdgeType.EXTENDS, confidence=1.0)
    store.add_edge(edge)
    
    retrieved_edge = store.get_edge("auth_1", "paper_1", "EXTENDS")
    assert retrieved_edge is not None
    assert retrieved_edge.confidence == 1.0

    # Ensure edge checks foreign key constraint on missing target
    with pytest.raises(ValueError):
        invalid_edge = Edge(source_id="auth_1", target_id="missing_paper", type=EdgeType.CITES)
        store.add_edge(invalid_edge)

def test_db_networkx_export(temp_db):
    store = temp_db
    
    node_a = ConceptNode(id="A", name="Concept A", definition="Base")
    node_b = ConceptNode(id="B", name="Concept B", definition="Derived")
    store.add_node(node_a)
    store.add_node(node_b)
    
    edge = Edge(source_id="A", target_id="B", type=EdgeType.EXTENDS)
    store.add_edge(edge)
    
    G = store.to_networkx()
    assert isinstance(G, nx.DiGraph)
    assert G.has_node("A")
    assert G.has_node("B")
    assert G.has_edge("A", "B")
    assert G.edges["A", "B"]["type"] == "EXTENDS"

def test_latex_parsing():
    parser = ArxivParser()
    sample_latex = r"""
    \title{On the Solvability of Graph Isomorphism}
    \author{Jane Doe}
    \begin{document}
    \begin{abstract}
    We prove that graph isomorphism is solvable in polynomial time.
    \end{abstract}
    
    \begin{definition}[Graph Isomorphism]
    \label{def:gi}
    Two graphs $G$ and $H$ are isomorphic if there exists a bijection...
    \end{definition}
    
    \begin{theorem}
    \label{thm:main}
    Graph Isomorphism can be decided in $O(n^{\log n})$ steps.
    \end{theorem}
    
    \begin{proof}
    The proof follows from applying the group theoretic techniques of \cite{Babai2016}.
    \end{proof}
    \end{document}
    """
    paper, claims, concepts, edges = parser.parse_tex_content("2303.1234", sample_latex)
    
    assert paper.name == "On the Solvability of Graph Isomorphism"
    assert "Babai2016" in paper.metadata["citation_keys"]
    
    assert len(claims) == 1
    assert claims[0].name == "Theorem thm:main"
    assert "Graph Isomorphism can be decided" in claims[0].statement
    
    assert len(concepts) == 1
    assert concepts[0].name == "Definition def:gi"
    
    assert len(edges) == 2  # paper -> theorem (PROVES), paper -> definition (EXTENDS)
    assert {e.type for e in edges} == {EdgeType.PROVES, EdgeType.EXTENDS}

def test_semantic_tracker(temp_db):
    store = temp_db
    tracker = SemanticTracker(store)
    
    # Set up nodes
    paper_a = PaperNode(id="paper_a", name="Paper A")
    paper_b = PaperNode(id="paper_b", name="Paper B")
    store.add_node(paper_a)
    store.add_node(paper_b)
    
    # Establish a reference connection: Paper A cites Paper B
    store.add_edge(Edge(source_id="paper_a", target_id="paper_b", type=EdgeType.CITES))
    
    # LaTeX content of Paper A containing a theorem and a proof citing Paper B
    latex_content = r"""
    \begin{theorem}
    For any finite group $G$, the order of any subgroup divides the order of $G$.
    \end{theorem}
    \begin{proof}
    This is Lagrange's theorem, proven using partition techniques outlined in \cite{Lagrange1771}.
    \end{proof}
    """
    
    # Map bibitem key to target paper ID
    citation_map = {"Lagrange1771": "paper_b"}
    
    # Resolve proof dependencies
    new_edges = tracker.resolve_proof_dependencies("paper_a", latex_content, citation_map)
    assert len(new_edges) == 1
    assert new_edges[0].type == EdgeType.USES_METHOD
    assert new_edges[0].target_id == "paper_b"

    # Add the claim and resolved edge to the DB
    import hashlib
    claim_hash = hashlib.sha256(
        b"theorem:\nFor any finite group $G$, the order of any subgroup divides the order of $G$."
    ).hexdigest()
    
    claim_node = MathematicalClaimNode(
        id=claim_hash, 
        name="Theorem 1", 
        statement="Lagrange's Theorem", 
        status=EpistemicStatus.VERIFIED
    )
    store.add_node(claim_node)
    
    # Fix source ID and write edge to store
    new_edges[0].source_id = claim_hash
    store.add_edge(new_edges[0])
    
    # Test circular dependency detection
    assert len(tracker.detect_circular_dependencies()) == 0
    
    # Artificially create a logical circular dependency
    # Let paper_b depend on claim_node (circular reasoning!)
    store.add_edge(Edge(source_id="paper_b", target_id=claim_hash, type=EdgeType.PROVES))
    cycles = tracker.detect_circular_dependencies()
    assert len(cycles) > 0
    assert claim_hash in cycles[0]
    
    # Test critical path analyzer
    critical = tracker.get_critical_path_claims()
    assert len(critical) > 0
    # The claim node or paper_b should have high reliance
    assert critical[0][0] in (claim_hash, "paper_b")
