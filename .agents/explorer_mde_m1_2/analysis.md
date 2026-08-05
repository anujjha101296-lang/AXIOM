# EGS Mathematical Ontology Schema Design & Analysis

**Author**: Explorer 2 (Milestone 1 — EGS Mathematical Ontology & Database Migrations)  
**Date**: 2026-08-05  
**Target File**: `axiom/core/knowledge_graph/schema.py`  
**Project Root**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`

---

## 1. Investigation Overview

The Epistemic Graph Store (EGS) in AXIOM relies on Pydantic v2 schema definitions in `axiom/core/knowledge_graph/schema.py` for structured representation, JSON serialization, and database object mapping. 

The objective of this investigation is to design the schema extensions required for Milestone 1 (EGS Mathematical Ontology & Database Migrations) to support the Mathematical Discovery Engine (MDE), specifically:
1. Four new Pydantic node models: `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`.
2. Three new edge relationship types/models: `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`.
3. Enum additions to `NodeType` and `EdgeType`.
4. Polymorphic discriminator update for `ScientificNode` Union type.

---

## 2. Existing Schema Architecture

In `axiom/core/knowledge_graph/schema.py`:
- `NodeType(str, Enum)`: Enumerates 6 existing node types (`PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`).
- `EdgeType(str, Enum)`: Enumerates 7 existing edge types (`CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`). Notice `PROVES` is already present.
- `EpistemicStatus(str, Enum)`: Enumerates status values (`VERIFIED`, `CONJECTURED`, `REFUTED`, `UNDER_REVIEW`).
- `VerificationTier(IntEnum)`: Enumerates verification levels (0 to 3).
- `NodeBase(BaseModel)`: Common base class providing `id`, `type`, `name`, and `metadata`.
- Node subclasses: `AuthorNode`, `PaperNode`, `ConceptNode`, `MathematicalClaimNode`, `ExperimentalFactNode`, `DatasetNode`.
- `ScientificNode`: Discriminated `Annotated[Union[...], Field(discriminator='type')]`.
- `Edge(BaseModel)`: Generic edge model holding `source_id`, `target_id`, `type`, `confidence`, `provenance`.
- `KnowledgeGraph(BaseModel)`: Container class holding `nodes: List[ScientificNode]` and `edges: List[Edge]`.

In `axiom/core/knowledge_graph/db.py`:
`scientific_node_adapter = TypeAdapter(ScientificNode)` is used to parse polymorphic JSON blobs stored in SQLite's `nodes.data` column.

---

## 3. Proposed Schema Updates

### 3.1. Enum Extensions

#### `NodeType`
Add four new string enum members:
```python
class NodeType(str, Enum):
    PAPER = "PAPER"
    AUTHOR = "AUTHOR"
    CONCEPT = "CONCEPT"
    MATHEMATICAL_CLAIM = "MATHEMATICAL_CLAIM"
    EXPERIMENTAL_FACT = "EXPERIMENTAL_FACT"
    DATASET = "DATASET"
    # New MDE Mathematical Ontology Node Types
    MATHEMATICAL_OBJECT = "MATHEMATICAL_OBJECT"
    DEFINITION = "DEFINITION"
    OPEN_PROBLEM = "OPEN_PROBLEM"
    CONJECTURE = "CONJECTURE"
```

#### `EdgeType`
Add two new string enum members (`PROVES` is already present):
```python
class EdgeType(str, Enum):
    CITES = "CITES"
    PROVES = "PROVES"
    REFUTES = "REFUTES"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    CORROBORATES = "CORROBORATES"
    USES_METHOD = "USES_METHOD"
    # New MDE Edge Types
    EQUIVALENT_TO = "EQUIVALENT_TO"
    DEPENDS_ON = "DEPENDS_ON"
```

---

### 3.2. New Node Models Design

#### 1. `MathematicalObjectNode`
Represents concrete mathematical entities, structures, functions, or operators (e.g. Riemann Zeta Function $\zeta(s)$, Dirichlet Series, Modular Forms, Prime Numbers).
- `type`: `Literal[NodeType.MATHEMATICAL_OBJECT] = NodeType.MATHEMATICAL_OBJECT`
- `domain`: `Optional[str]` (e.g., `"Analytic Number Theory"`, `"Algebraic Geometry"`)
- `symbolic_representation`: `Optional[str]` (LaTeX string or SymPy expression e.g. `r"\zeta(s)"`)
- `formal_type`: `Optional[str]` (Formal Lean 4 / Coq type signature e.g. `"Complex -> Complex"`)
- `properties`: `Dict[str, Union[str, int, float, bool, List[str], None]]` (Key invariants, e.g. `{"is_meromorphic": True, "poles": ["1"]}`)

#### 2. `DefinitionNode`
Represents formal definitions of mathematical terms, axioms, or construct specifications.
- `type`: `Literal[NodeType.DEFINITION] = NodeType.DEFINITION`
- `term`: `str` (Name of defined term e.g. `"Dirichlet L-function"`)
- `formal_definition`: `str` (Lean 4 declaration or SymPy formal definition string)
- `informal_description`: `Optional[str]` (Natural language narrative definition)
- `domain`: `Optional[str]` (Mathematical domain classification)

#### 3. `OpenProblemNode`
Represents open mathematical problems, conjectures, or grand challenges (e.g. Riemann Hypothesis, Birch and Swinnerton-Dyer Conjecture).
- `type`: `Literal[NodeType.OPEN_PROBLEM] = NodeType.OPEN_PROBLEM`
- `statement`: `str` (Formal or natural language statement of the open problem)
- `domain`: `Optional[str]` (Domain classification e.g. `"Analytic Number Theory"`)
- `prize_bounty`: `Optional[str]` (Optional reward e.g. `"$1,000,000 Clay Millennium Prize"`)
- `status`: `EpistemicStatus = EpistemicStatus.CONJECTURED`
- `importance_score`: `float = 1.0` (Priority weight in discovery search [0.0, 1.0])

#### 4. `ConjectureNode`
Represents machine-generated or human-proposed mathematical conjectures (e.g. candidates produced by the Autonomous Conjecture Generator M4).
- `type`: `Literal[NodeType.CONJECTURE] = NodeType.CONJECTURE`
- `statement`: `str` (Claim statement in natural language or LaTeX)
- `formal_specification`: `Optional[str]` (Lean 4, Coq, or SMT logic code)
- `status`: `EpistemicStatus = EpistemicStatus.CONJECTURED`
- `tier`: `VerificationTier = VerificationTier.TIER_0_CONJECTURE`
- `novelty_score`: `Optional[float] = None` (Computed $N(C)$ novelty score)
- `generation_strategy`: `Optional[str] = None` (Generator strategy e.g. `"DUAL"`, `"BOUND"`, `"COMPLEX"`, `"GENERAL"`, `"COMPOSE"`)

---

### 3.3. Edge Models & Relationship Semantics

In EGS, edges are instantiated via the `Edge` Pydantic model:
```python
class Edge(BaseModel):
    source_id: str = Field(..., description="The ID of the source node")
    target_id: str = Field(..., description="The ID of the target node")
    type: EdgeType = Field(..., description="The type of connection")
    confidence: float = Field(default=1.0, description="Confidence score of this relationship [0, 1]")
    provenance: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, 
        description="Lineage indicating how the relationship was discovered or extracted"
    )
```

To support strong typing and convenience instantiation, typed edge models (or factory subclasses) can also be provided:
- `EquivalentToEdge`: Subclass of `Edge` with `type: Literal[EdgeType.EQUIVALENT_TO] = EdgeType.EQUIVALENT_TO`. Indicates bi-directional logical equivalence ($A \iff B$) between two claims, definitions, or conjectures.
- `DependsOnEdge`: Subclass of `Edge` with `type: Literal[EdgeType.DEPENDS_ON] = EdgeType.DEPENDS_ON`. Indicates proof or conceptual prerequisite ($A \implies B$ or $A$ relies on $B$).
- `ProvesEdge`: Subclass of `Edge` with `type: Literal[EdgeType.PROVES] = EdgeType.PROVES`. Indicates direct verification/proof lineage from a proof/paper to a claim or conjecture.

---

### 3.4. Polymorphic `ScientificNode` Union Update

The `ScientificNode` discriminated union must be updated to include all 4 new node classes:

```python
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
```

Because each node class specifies `type: Literal[NodeType.<ENUM>] = NodeType.<ENUM>`, Pydantic's `discriminator='type'` matches the `"type"` string in JSON payloads and deserializes into the appropriate model type cleanly.

---

## 4. Complete Reference Implementation for `axiom/core/knowledge_graph/schema.py`

Below is the complete, proposed updated content for `schema.py`:

```python
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field

class NodeType(str, Enum):
    PAPER = "PAPER"
    AUTHOR = "AUTHOR"
    CONCEPT = "CONCEPT"
    MATHEMATICAL_CLAIM = "MATHEMATICAL_CLAIM"
    EXPERIMENTAL_FACT = "EXPERIMENTAL_FACT"
    DATASET = "DATASET"
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
    metadata: Dict[str, Union[str, int, float, bool, List[str], None]] = Field(
        default_factory=dict, description="Arbitrary attributes"
    )

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
    provenance: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict, 
        description="Lineage indicating how the relationship was discovered or extracted"
    )

class KnowledgeGraph(BaseModel):
    nodes: List[ScientificNode] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
```

---

## 5. Compatibility & Integration Analysis

1. **`EpistemicStore` (`db.py`)**:
   - `TypeAdapter(ScientificNode)` automatically validates all 10 node types without requiring any changes to deserialization logic.
   - `add_node()` and `add_edge()` operate directly on `ScientificNode` and `Edge` objects.
   - `to_networkx()` exports graph nodes and edge types to `nx.DiGraph` seamlessly.

2. **Downstream MDE Microservices**:
   - **Retrieval Engine (M2)**: Queries `DefinitionNode`, `MathematicalObjectNode`, and traverses `EQUIVALENT_TO` and `DEPENDS_ON` edges.
   - **Formal Proof Architecture (M3)**: Consumes `formal_specification` and `formal_definition` from `ConjectureNode` and `DefinitionNode`.
   - **Conjecture Generator (M4)**: Emits `ConjectureNode` with `novelty_score` and `generation_strategy`.
   - **Counterexample Search Gateway (M5)**: Updates `status` of `ConjectureNode` / `MathematicalClaimNode` to `REFUTED`.
   - **Research Strategy & Memory (M6)**: Uses `OpenProblemNode` and `DEPENDS_ON` edges for tree decomposition.

---

## 6. Recommended Test Suite (`tests/test_mde_ontology.py`)

The implementer should include unit tests verifying:
1. `test_new_node_instantiation`: Instantiates each of the 4 new node types and verifies default field values and type literals.
2. `test_polymorphic_node_serialization`: Dump nodes to JSON via `model_dump_json()` and reload using `TypeAdapter(ScientificNode).validate_json()` to confirm discriminator matching.
3. `test_new_edge_types`: Validates `Edge` creation with `EQUIVALENT_TO`, `DEPENDS_ON`, and `PROVES`.
4. `test_epistemic_store_integration`: Saves all new node and edge types into an in-memory `EpistemicStore`, retrieves them, and asserts equality.
