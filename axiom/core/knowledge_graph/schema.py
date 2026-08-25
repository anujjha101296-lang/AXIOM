from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union, Annotated, Literal, Any
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    PAPER = "PAPER"
    AUTHOR = "AUTHOR"
    CONCEPT = "CONCEPT"
    MATHEMATICAL_CLAIM = "MATHEMATICAL_CLAIM"
    EXPERIMENTAL_FACT = "EXPERIMENTAL_FACT"
    DATASET = "DATASET"
    # MDE Mathematical Ontology Node Types
    MATHEMATICAL_OBJECT = "MATHEMATICAL_OBJECT"
    DEFINITION = "DEFINITION"
    OPEN_PROBLEM = "OPEN_PROBLEM"
    CONJECTURE = "CONJECTURE"

class EdgeType(str, Enum):
    CITES = "CITES"
    PROVES = "PROVES"
    REFUTES = "REFUTES"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    CORROBORATES = "CORROBORATES"
    USES_METHOD = "USES_METHOD"
    # MDE Edge Types
    EQUIVALENT_TO = "EQUIVALENT_TO"
    DEPENDS_ON = "DEPENDS_ON"

class EpistemicStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONJECTURED = "CONJECTURED"
    REFUTED = "REFUTED"
    UNDER_REVIEW = "UNDER_REVIEW"

class VerificationTier(IntEnum):
    TIER_0_CONJECTURE = 0
    TIER_1_SIMULATED = 1
    TIER_2_PROVEN = 2
    TIER_3_REPLICATED = 3

class NodeBase(BaseModel):
    id: str = Field(..., description="Unique identifier, usually a content hash or UUID")
    type: NodeType = Field(..., description="The classification of the node")
    name: str = Field(..., description="Human-readable title or label")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary attributes")

class AuthorNode(NodeBase):
    type: Literal[NodeType.AUTHOR] = NodeType.AUTHOR
    orcid: Optional[str] = None
    affiliations: List[str] = Field(default_factory=list)

class PaperNode(NodeBase):
    type: Literal[NodeType.PAPER] = NodeType.PAPER
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    abstract: Optional[str] = None
    published_date: Optional[str] = None

class ConceptNode(NodeBase):
    type: Literal[NodeType.CONCEPT] = NodeType.CONCEPT
    definition: str
    mathematical_formulation: Optional[str] = None

class MathematicalClaimNode(NodeBase):
    type: Literal[NodeType.MATHEMATICAL_CLAIM] = NodeType.MATHEMATICAL_CLAIM
    statement: str
    formal_specification: Optional[str] = None  # E.g., Lean 4 statement
    status: EpistemicStatus = EpistemicStatus.CONJECTURED
    tier: VerificationTier = VerificationTier.TIER_0_CONJECTURE

class ExperimentalFactNode(NodeBase):
    type: Literal[NodeType.EXPERIMENTAL_FACT] = NodeType.EXPERIMENTAL_FACT
    fact_description: str
    confidence_metric: float = 1.0  # Statistical confidence, p-value mapping, etc.
    status: EpistemicStatus = EpistemicStatus.UNDER_REVIEW
    tier: VerificationTier = VerificationTier.TIER_0_CONJECTURE

class DatasetNode(NodeBase):
    type: Literal[NodeType.DATASET] = NodeType.DATASET
    url: Optional[str] = None
    size_bytes: Optional[int] = None

class MathematicalObjectNode(NodeBase):
    type: Literal[NodeType.MATHEMATICAL_OBJECT] = NodeType.MATHEMATICAL_OBJECT
    domain: Optional[str] = Field(default=None, description="Mathematical domain classification")
    symbolic_representation: Optional[str] = Field(default=None, description="LaTeX or SymPy exact expression string")
    formal_type: Optional[str] = Field(default=None, description="Formal type signature e.g., 'Complex -> Complex'")
    properties: Dict[str, Union[str, int, float, bool, List[str], None]] = Field(
        default_factory=dict, description="Key mathematical attributes or invariants"
    )

class DefinitionNode(NodeBase):
    type: Literal[NodeType.DEFINITION] = NodeType.DEFINITION
    term: str = Field(..., description="The mathematical term being defined")
    formal_definition: str = Field(..., description="Formal logic formulation in Lean 4, Coq, or SymPy")
    informal_description: Optional[str] = Field(default=None, description="Human-readable description")
    domain: Optional[str] = Field(default=None, description="Mathematical domain classification")

class OpenProblemNode(NodeBase):
    type: Literal[NodeType.OPEN_PROBLEM] = NodeType.OPEN_PROBLEM
    statement: str = Field(..., description="Statement of the open problem")
    domain: Optional[str] = Field(default=None, description="Mathematical domain classification")
    prize_bounty: Optional[str] = Field(default=None, description="Prize money or award e.g. '$1M Clay Millennium Prize'")
    status: EpistemicStatus = Field(default=EpistemicStatus.CONJECTURED, description="Epistemic status")
    importance_score: float = Field(default=1.0, description="Priority / importance score")

class ConjectureNode(NodeBase):
    type: Literal[NodeType.CONJECTURE] = NodeType.CONJECTURE
    statement: str = Field(..., description="Conjecture statement")
    formal_specification: Optional[str] = Field(default=None, description="Lean 4 / Coq / SMT formal code")
    status: EpistemicStatus = Field(default=EpistemicStatus.CONJECTURED, description="Epistemic status")
    tier: VerificationTier = Field(default=VerificationTier.TIER_0_CONJECTURE, description="Verification tier")
    novelty_score: Optional[float] = Field(default=None, description="Novelty score N(C)")
    generation_strategy: Optional[str] = Field(default=None, description="Strategy used to generate conjecture")

# Annotated union type for polymorphism in Pydantic serialization
ScientificNode = Annotated[
    Union[
        AuthorNode,
        PaperNode,
        ConceptNode,
        MathematicalClaimNode,
        ExperimentalFactNode,
        DatasetNode,
        MathematicalObjectNode,
        DefinitionNode,
        OpenProblemNode,
        ConjectureNode
    ],
    Field(discriminator='type')
]

class Edge(BaseModel):
    source_id: str = Field(..., description="The ID of the source node")
    target_id: str = Field(..., description="The ID of the target node")
    type: EdgeType = Field(..., description="The type of connection")
    confidence: float = Field(default=1.0, description="Confidence score of this relationship [0, 1]")
    provenance: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Lineage indicating how the relationship was discovered or extracted"
    )

class KnowledgeGraph(BaseModel):
    nodes: List[ScientificNode] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)

