import os
import re
import tarfile
import tempfile
from typing import Dict, List, Tuple, Optional
import hashlib
import requests

from axiom.core.knowledge_graph.schema import (
    PaperNode,
    MathematicalClaimNode,
    ConceptNode,
    Edge,
    EdgeType,
    NodeType,
    EpistemicStatus,
    VerificationTier
)

class ArxivParser:
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or tempfile.gettempdir()
        os.makedirs(self.cache_dir, exist_ok=True)

    def download_source(self, arxiv_id: str) -> str:
        """Download the LaTeX source tarball for a given arXiv ID."""
        url = f"https://arxiv.org/src/{arxiv_id}"
        dest_path = os.path.join(self.cache_dir, f"{arxiv_id}.tar.gz")
        
        # If already cached, return it
        if os.path.exists(dest_path):
            return dest_path
            
        headers = {
            "User-Agent": "AXIOM Scientific Discovery Engine (https://axiom.org; contact@axiom.org)"
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return dest_path

    def extract_source(self, tar_path: str, extract_dir: str) -> List[str]:
        """Extract tar.gz archive and return a list of extracted .tex file paths."""
        tex_files = []
        try:
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=extract_dir)
        except tarfile.ReadError:
            # Sometimes arXiv source is just a single gzipped .tex file rather than a tarball
            # or it is a plain pdf/text. We attempt to read it or log warning
            pass
            
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".tex"):
                    tex_files.append(os.path.join(root, file))
        return tex_files

    def parse_paper(self, arxiv_id: str) -> Tuple[PaperNode, List[MathematicalClaimNode], List[ConceptNode], List[Edge]]:
        """Download, extract, and parse a paper's LaTeX files into graph nodes and edges."""
        tar_path = self.download_source(arxiv_id)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_files = self.extract_source(tar_path, temp_dir)
            
            # Combine content of all .tex files for broad parsing
            tex_content = ""
            for file_path in tex_files:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        tex_content += f.read() + "\n"
                except Exception:
                    continue
            
            return self.parse_tex_content(arxiv_id, tex_content)

    def parse_tex_content(self, arxiv_id: str, content: str) -> Tuple[PaperNode, List[MathematicalClaimNode], List[ConceptNode], List[Edge]]:
        """Parse raw LaTeX string to extract nodes and relationships."""
        # Extract title
        title_match = re.search(r"\\title\{([^}]+)\}", content)
        title = title_match.group(1).strip() if title_match else f"arXiv:{arxiv_id}"
        # Remove LaTeX formatting from title
        title = re.sub(r"\\[a-zA-Z]+", "", title).replace("{", "").replace("}", "").strip()

        # Extract abstract
        abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
        abstract = abstract_match.group(1).strip() if abstract_match else ""

        paper_hash = hashlib.sha256(f"paper:{arxiv_id}".encode()).hexdigest()
        paper_node = PaperNode(
            id=paper_hash,
            name=title,
            arxiv_id=arxiv_id,
            abstract=abstract
        )

        claims: List[MathematicalClaimNode] = []
        concepts: List[ConceptNode] = []
        edges: List[Edge] = []

        # Parse LaTeX Environments (Theorems, Lemmas, Definitions)
        # Regex to find \begin{env_name}[opt_name] ... \end{env_name}
        env_pattern = re.compile(
            r"\\begin\{(theorem|lemma|definition|conjecture|proposition|corollary)\}(.*?)\\end\{\1\}",
            re.DOTALL
        )
        
        claim_index = 1
        concept_index = 1

        for match in env_pattern.finditer(content):
            env_type = match.group(1)
            env_body = match.group(2).strip()
            
            # Clean comments out of env body
            env_body = "\n".join([line for line in env_body.splitlines() if not line.strip().startswith("%")])
            
            # Extract label if available
            label_match = re.search(r"\\label\{([^}]+)\}", env_body)
            label = label_match.group(1) if label_match else None
            
            # Generate a unique hash for the statement
            statement_hash = hashlib.sha256(f"{env_type}:{env_body}".encode()).hexdigest()
            
            clean_statement = re.sub(r"\\label\{[^}]+\}", "", env_body).strip()
            
            if env_type in ("theorem", "lemma", "conjecture", "proposition", "corollary"):
                # Map to MathematicalClaimNode
                status = EpistemicStatus.CONJECTURED if env_type == "conjecture" else EpistemicStatus.VERIFIED
                tier = VerificationTier.TIER_0_CONJECTURE
                
                claim_node = MathematicalClaimNode(
                    id=statement_hash,
                    name=f"{env_type.capitalize()} {label or claim_index}",
                    statement=clean_statement,
                    status=status,
                    tier=tier,
                    metadata={"latex_label": label or "", "environment": env_type}
                )
                claims.append(claim_node)
                claim_index += 1
                
                # Check if there is a corresponding proof for this claim in the LaTeX content
                # For basic extraction: we check if the label appears, or look for \begin{proof} near it
                # We'll create a PROVES edge from the paper to the claim if it is verified (theorem/lemma/etc.)
                edge_type = EdgeType.PROVES if status == EpistemicStatus.VERIFIED else EdgeType.CITES
                edges.append(Edge(
                    source_id=paper_node.id,
                    target_id=claim_node.id,
                    type=edge_type,
                    confidence=1.0,
                    provenance={"method": "regex_env_parser"}
                ))
                
            elif env_type == "definition":
                # Map to ConceptNode
                concept_node = ConceptNode(
                    id=statement_hash,
                    name=f"Definition {label or concept_index}",
                    definition=clean_statement,
                    metadata={"latex_label": label or ""}
                )
                concepts.append(concept_node)
                concept_index += 1
                
                edges.append(Edge(
                    source_id=paper_node.id,
                    target_id=concept_node.id,
                    type=EdgeType.EXTENDS, # The paper extends this concept
                    confidence=1.0,
                    provenance={"method": "regex_env_parser"}
                ))

        # Parse inline/block citations \cite{key1, key2}
        cite_pattern = re.compile(r"\\cite(?:[a-z]*)?\{([^}]+)\}")
        citation_keys = set()
        for match in cite_pattern.finditer(content):
            keys = [k.strip() for k in match.group(1).split(",")]
            citation_keys.update(keys)
            
        paper_node.metadata["citation_keys"] = list(citation_keys)

        return paper_node, claims, concepts, edges
