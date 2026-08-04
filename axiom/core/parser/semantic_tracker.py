import re
import networkx as nx
from typing import List, Dict, Set, Tuple
from axiom.core.knowledge_graph.schema import Edge, EdgeType, MathematicalClaimNode
from axiom.core.knowledge_graph.db import EpistemicStore

class SemanticTracker:
    def __init__(self, store: EpistemicStore):
        self.store = store

    def resolve_proof_dependencies(self, paper_id: str, tex_content: str, citation_map: Dict[str, str]) -> List[Edge]:
        """
        Analyze proof blocks to detect where mathematical claims reference specific cited papers.
        
        Args:
            paper_id: The ID of the paper containing the proofs.
            tex_content: The full LaTeX source text.
            citation_map: A dictionary mapping LaTeX bibitem keys (e.g., "Gödel31") to target Paper IDs/DOIs.
            
        Returns:
            A list of dependency edges (e.g., Claim X -> USES_METHOD -> Paper Y).
        """
        edges: List[Edge] = []
        
        # Regex to locate proofs and their body
        # Typically \begin{proof} ... \end{proof}
        proof_pattern = re.compile(r"\\begin\{proof\}(.*?)\\end\{proof\}", re.DOTALL)
        
        # We also need to map which theorem the proof belongs to.
        # Simple heuristic: find the proof that immediately follows a theorem/lemma environment,
        # or find proofs that contain \label or refer to the theorem label.
        # Let's search for theorems and see if they are followed by proof blocks.
        combined_pattern = re.compile(
            r"\\begin\{(theorem|lemma|proposition|corollary)\}(.*?)\\end\{\1\}(.*?)\\begin\{proof\}(.*?)\\end\{proof\}",
            re.DOTALL
        )

        for match in combined_pattern.finditer(tex_content):
            env_type = match.group(1)
            env_body = match.group(2)
            proof_body = match.group(4)
            
            # Recreate the hash for the claim to locate it in the DB
            import hashlib
            # Clean comments
            clean_env = "\n".join([line for line in env_body.splitlines() if not line.strip().startswith("%")])
            claim_id = hashlib.sha256(f"{env_type}:{clean_env}".encode()).hexdigest()
            
            # Find all \cite{...} within the proof body
            cite_pattern = re.compile(r"\\cite(?:[a-z]*)?\{([^}]+)\}")
            for cite_match in cite_pattern.finditer(proof_body):
                keys = [k.strip() for k in cite_match.group(1).split(",")]
                for key in keys:
                    if key in citation_map:
                        target_paper_id = citation_map[key]
                        
                        # Add a logical dependency link
                        edges.append(Edge(
                            source_id=claim_id,
                            target_id=target_paper_id,
                            type=EdgeType.USES_METHOD,
                            confidence=0.9,
                            provenance={
                                "method": "proof_citation_resolution",
                                "context": f"Found cite '{key}' inside proof body"
                            }
                        ))
                        
        return edges

    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Check the knowledge graph for circular reasoning.
        Returns a list of cycles (lists of node IDs forming cycles).
        """
        G = self.store.to_networkx()
        
        # We only care about logical dependencies: PROVES, EXTENDS, USES_METHOD
        dependency_edges = [
            (u, v) for u, v, d in G.edges(data=True) 
            if d.get("type") in (EdgeType.PROVES.value, EdgeType.EXTENDS.value, EdgeType.USES_METHOD.value)
        ]
        
        dep_graph = nx.DiGraph(dependency_edges)
        
        try:
            cycles = list(nx.simple_cycles(dep_graph))
            return cycles
        except Exception:
            return []

    def get_critical_path_claims(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Find mathematical claims that are most heavily relied upon (high out-degree in the dependency graph).
        Returns list of tuples: (claim_id, dependency_count)
        """
        G = self.store.to_networkx()
        
        # Build logical dependency graph where Edges represent: Claim -> depends on -> Claim/Paper
        # For simplicity, reverse the direction: target depends on source.
        dependency_edges = [
            (u, v) for u, v, d in G.edges(data=True) 
            if d.get("type") in (EdgeType.PROVES.value, EdgeType.EXTENDS.value, EdgeType.USES_METHOD.value)
        ]
        
        dep_graph = nx.DiGraph(dependency_edges)
        
        # Out-degree in the dependency graph represents how many elements depend on this node
        out_degrees = dep_graph.out_degree()
        
        # Sort by out-degree descending
        sorted_claims = sorted(out_degrees, key=lambda x: x[1], reverse=True)
        return sorted_claims[:limit]
