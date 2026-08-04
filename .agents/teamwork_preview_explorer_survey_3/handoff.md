# Explorer 3 Survey Handoff Report: Data Models, Interface Contracts & Module Dependency Graph

**Agent**: Explorer 3  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/teamwork_preview_explorer_survey_3`  
**Date**: 2026-08-04T21:44:00Z  

---

## 1. Observation

Direct examination of the existing codebase at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` yields the following baseline structures and gaps:

### 1.1 Existing Codebase Data Schema (`axiom/core/knowledge_graph/schema.py`)
- **Node Classification** (`lines 5-11`): `NodeType` enum defines `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`.
- **Edge Types** (`lines 13-20`): `EdgeType` enum defines `CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`.
- **Epistemic Classification** (`lines 22-32`): `EpistemicStatus` (`VERIFIED`, `CONJECTURED`, `REFUTED`, `UNDER_REVIEW`) and `VerificationTier` (`TIER_0_CONJECTURE` (0), `TIER_1_SIMULATED` (1), `TIER_2_PROVEN` (2), `TIER_3_REPLICATED` (3)).
- **Polymorphic Node Union** (`lines 34-87`): `ScientificNode` annotated union with discriminator `'type'`, wrapping `AuthorNode`, `PaperNode`, `ConceptNode`, `MathematicalClaimNode`, `ExperimentalFactNode`, `DatasetNode`.
- **Edge Representation** (`lines 89-98`): `Edge` class containing `source_id: str`, `target_id: str`, `type: EdgeType`, `confidence: float`, `provenance: Dict[str, Any]`.

### 1.2 Existing Database Layer (`axiom/core/knowledge_graph/db.py`)
- **SQLite Initialization** (`lines 29-54`): Creates `nodes` table (`id`, `type`, `name`, `data`) and `edges` table (`source_id`, `target_id`, `type`, `confidence`, `provenance`), with indexes on `type`, `source_id`, and `target_id`.
- **NetworkX Conversion** (`lines 164-188`): `to_networkx()` constructs `nx.DiGraph` from SQLite records for cycle detection and path analysis.

### 1.3 Existing Parser & Tracking (`axiom/core/parser/arxiv_parser.py` & `semantic_tracker.py`)
- **arXiv Regex Extraction** (`arxiv_parser.py`, `lines 107-177`): Extracts `\begin{theorem|lemma|definition|...}` using regex pattern matching and creates basic `MathematicalClaimNode` and `ConceptNode`.
- **Circular Dependency Detection** (`semantic_tracker.py`, `lines 71-90`): Calls `nx.simple_cycles()` on logical edges (`PROVES`, `EXTENDS`, `USES_METHOD`).

### 1.4 Existing API Gateway (`axiom/services/api_gateway/main.py`)
- **Endpoints** (`lines 43-85`): `/health` (liveness), `/ready` (SQLite check), `/ingest` (stub), `/query` (stub).

### 1.5 Missing Data Contracts Across Requirements
- **R1**: Formal LaTeX AST representation model and complete ingested graph serialization interface.
- **R2**: Lean 4 AST model, Lean file generation schema, and compiler interface contracts.
- **R3**: SMT / Z3 solver request/response models, assertion tree representation, and structured counterexample format.
- **R4**: Strict relational schema definitions for SQLite verification logs, MCTS search runs, and trigger-level circular edge constraints.
- **R5**: MCTS search tree node, tactic action, UCB state, and proof search execution request/response models.
- **R6**: Next.js spatial canvas REST API payloads, WebSocket streaming events, and visual node/edge coordinate contracts.

---

## 2. Logic Chain & Interface Contract Specifications

Based on the requirements in `ORIGINAL_REQUEST.md`, step-by-step reasoning drives the design of comprehensive Pydantic and TypeScript interface contracts for each module.

### 2.1 LaTeX AST -> Parsed JSON Graph Structure (R1: EIE)

#### Reasoning
Requirement R1 demands parsing arXiv LaTeX source documents into a structured JSON graph format with >95% extraction rate for math environments and citation keys. Regex alone is insufficient for complex nested LaTeX. We specify a formal LaTeX AST data model that captures tokens, mathematical environments, labels, and citations, along with an `IngestedPaperGraph` payload.

#### Interface Contracts (Python / Pydantic)
```python
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

class LaTeXNodeType(str, Enum):
    DOCUMENT = "DOCUMENT"
    SECTION = "SECTION"
    ENVIRONMENT = "ENVIRONMENT"
    MATH_INLINE = "MATH_INLINE"
    MATH_BLOCK = "MATH_BLOCK"
    CITATION = "CITATION"
    CROSS_REFERENCE = "CROSS_REFERENCE"
    TEXT = "TEXT"

class LaTeXASTNode(BaseModel):
    node_id: str = Field(..., description="Unique AST node ID")
    type: LaTeXNodeType
    raw_content: str = Field(..., description="Verbatim LaTeX source string")
    clean_text: Optional[str] = None
    environment_name: Optional[str] = None  # e.g., 'theorem', 'lemma', 'proof', 'align*'
    label: Optional[str] = None
    line_start: int
    line_end: int
    children: List["LaTeXASTNode"] = Field(default_factory=list)

class ParsedMathExpression(BaseModel):
    expression_id: str
    latex_str: str
    normalized_ast: Dict[str, Any]  # Parsed expression tree (operators, operands, variables)
    variables: List[str]
    is_equation: bool = False

class CitationReference(BaseModel):
    citation_key: str
    context_snippet: str
    target_paper_id: Optional[str] = None
    target_doi: Optional[str] = None

class IngestedPaperGraphPayload(BaseModel):
    paper_id: str
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    ast_root: LaTeXASTNode
    claims: List[Dict[str, Any]]  # Serialized MathematicalClaimNode dicts
    concepts: List[Dict[str, Any]] # Serialized ConceptNode dicts
    citations: List[CitationReference]
    edges: List[Dict[str, Any]]    # Serialized Edge dicts
    extraction_stats: Dict[str, Any] = Field(
        ..., 
        description="Stats: math_env_count, citation_count, extraction_rate_percentage"
    )
```

---

### 2.2 SQLite Relational Schema & Circular Reference Checks (R4: EGS)

#### Reasoning
Requirement R4 requires an SQLite-backed database storing entities and logical dependency edges with circular reference checks. Store entities in relational tables with foreign keys and JSON data payloads. To prevent circular reasoning in claim dependencies (`PROVES`, `EXTENDS`, `USES_METHOD`), runtime validation using Tarjan's / NetworkX cycle detection enforces DAG constraints.

#### Relational DDL (SQL)
```sql
-- SQLite Relational Schema for EGS
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'CONJECTURED',
    tier INTEGER DEFAULT 0,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS edges (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0,
    provenance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, target_id, type),
    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS verification_records (
    verification_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    verifier_type TEXT NOT NULL, -- 'LEAN4' or 'Z3_SMT'
    status TEXT NOT NULL,       -- 'VERIFIED', 'REFUTED', 'SYNTAX_ERROR', 'TIMEOUT'
    execution_time_ms INTEGER NOT NULL,
    proof_or_counterexample TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mcts_search_runs (
    run_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    iterations INTEGER NOT NULL,
    nodes_expanded INTEGER NOT NULL,
    is_solved BOOLEAN NOT NULL,
    winning_proof_script TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_nodes_type_tier ON nodes(type, tier);
CREATE INDEX IF NOT EXISTS idx_edges_source_type ON edges(source_id, type);
CREATE INDEX IF NOT EXISTS idx_edges_target_type ON edges(target_id, type);
CREATE INDEX IF NOT EXISTS idx_verification_claim ON verification_records(claim_id);
```

#### Circular Reference Check Contract (Python)
```python
class CycleCheckResult(BaseModel):
    has_cycle: bool
    cycles_detected: List[List[str]]  # Lists of node ID cycles
    violating_edge: Optional[Dict[str, str]] = None
    message: str
```

---

### 2.3 Lean 4 Theorem Declaration AST & File Generation (R2: LRK)

#### Reasoning
Requirement R2 requires translating parsed LaTeX theorem/lemma statements into compilable Lean 4 theorem declarations (0 syntax errors). We construct a Lean 4 AST model representing imports, variables, hypotheses, theorem statements, and proof scripts, with compilation request/response contracts.

#### Interface Contracts (Python / Pydantic)
```python
class LeanVariable(BaseModel):
    name: str
    type_expr: str  # e.g. "Type*", "ℝ", "ℕ", "Group G"
    is_implicit: bool = False

class LeanHypothesis(BaseModel):
    label: str      # e.g. "h1", "h_pos"
    type_expr: str  # e.g. "x > 0"

class LeanTheoremAST(BaseModel):
    name: str                           # e.g. "algebra_lemma_1"
    variables: List[LeanVariable] = Field(default_factory=list)
    hypotheses: List[LeanHypothesis] = Field(default_factory=list)
    target_goal: str                    # e.g. "x + y = y + x"
    proof_script: str = "by sorry"       # Tactic block or 'sorry'

class LeanDefinitionAST(BaseModel):
    name: str
    variables: List[LeanVariable] = Field(default_factory=list)
    return_type: str
    value_expr: str

class LeanFileAST(BaseModel):
    imports: List[str] = Field(default_factory=lambda: ["Mathlib.Algebra.Group.Defs"])
    namespace: Optional[str] = "AxiomAuto"
    definitions: List[LeanDefinitionAST] = Field(default_factory=list)
    theorems: List[LeanTheoremAST] = Field(default_factory=list)

    def render(self) -> str:
        """Renders compilable Lean 4 source code text."""
        lines = [f"import {imp}" for imp in self.imports] + [""]
        if self.namespace:
            lines.append(f"namespace {self.namespace}\n")
        
        for d in self.definitions:
            vars_str = " ".join([f"({v.name} : {v.type_expr})" for v in d.variables])
            lines.append(f"def {d.name} {vars_str} : {d.return_type} := {d.value_expr}\n")
            
        for t in self.theorems:
            vars_str = " ".join([f"({v.name} : {v.type_expr})" for v in t.variables])
            hyps_str = " ".join([f"({h.label} : {h.type_expr})" for h in t.hypotheses])
            lines.append(f"theorem {t.name} {vars_str} {hyps_str} : {t.target_goal} := {t.proof_script}\n")
            
        if self.namespace:
            lines.append(f"end {self.namespace}")
        return "\n".join(lines)

class LeanCompileRequest(BaseModel):
    claim_id: str
    lean_code: str
    timeout_seconds: int = 30

class LeanCompileError(BaseModel):
    line: int
    column: int
    severity: str  # 'error', 'warning', 'information'
    message: str

class LeanCompileResponse(BaseModel):
    claim_id: str
    is_valid: bool
    status_code: str  # 'SUCCESS', 'SYNTAX_ERROR', 'TYPE_ERROR', 'TIMEOUT'
    errors: List[LeanCompileError] = Field(default_factory=list)
    execution_time_ms: int
```

---

### 2.4 SMT / Z3 Request/Response Models & Counterexample Format (R3: AVT)

#### Reasoning
Requirement R3 mandates integrating with Z3/SMT solvers to run parameter sweeps seeking counterexamples for conjectures (<60s detection). We define SMT variables, parameter bound ranges, solver assertions, and counterexample responses.

#### Interface Contracts (Python / Pydantic)
```python
class SMTSort(str, Enum):
    INT = "Int"
    REAL = "Real"
    BOOL = "Bool"

class SMTVariable(BaseModel):
    name: str
    sort: SMTSort
    min_bound: Optional[Union[int, float]] = None
    max_bound: Optional[Union[int, float]] = None

class SMTCheckRequest(BaseModel):
    claim_id: str
    variables: List[SMTVariable]
    assumptions: List[str]          # SMT-LIB2 assertion strings (hypotheses)
    conjecture_negation: str       # Negated conjecture statement to test for SAT
    timeout_ms: int = 60000          # 60 second execution limit per R3 requirement

class SMTCounterexample(BaseModel):
    model_assignments: Dict[str, Union[int, float, bool, str]]
    violated_boundary: Optional[str] = None
    explanation: str

class SMTCheckResponse(BaseModel):
    claim_id: str
    result: str                     # 'SAT' (counterexample found), 'UNSAT' (no counterexample in bounds), 'UNKNOWN', 'TIMEOUT'
    has_counterexample: bool
    counterexample: Optional[SMTCounterexample] = None
    execution_time_ms: int
    solver_output: Optional[str] = None
```

---

### 2.5 MCTS Search Tree Node/Tactic Structure (R5: DRSP)

#### Reasoning
Requirement R5 mandates Monte Carlo Tree Search (MCTS) exploring Lean proof tactics to discover valid proofs for algebra lemmas. We define MCTS tree nodes, tactic actions, UCB search state, and execution contracts.

#### Interface Contracts (Python / Pydantic)
```python
class MCTSTacticAction(BaseModel):
    tactic_str: str                # e.g., "ring", "simp", "linarith", "induction n"
    prior_score: float             # Policy network prior probability P(a|s)

class MCTSNodeState(BaseModel):
    node_id: str
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    open_goals: List[str]          # Current Lean proof state goals
    tactic_applied: Optional[str]  # Action that led to this node
    visit_count: int = 0           # N
    total_value: float = 0.0       # W
    mean_value: float = 0.0        # Q = W / N
    prior: float = 1.0             # P
    depth: int = 0
    is_terminal: bool = False
    is_solved: bool = False

class MCTSProofSearchRequest(BaseModel):
    claim_id: str
    lean_theorem_code: str
    max_iterations: int = 1000
    max_depth: int = 20
    c_puct: float = 1.414
    timeout_seconds: int = 120

class MCTSProofSearchResponse(BaseModel):
    claim_id: str
    is_solved: bool
    generated_proof_script: Optional[str] = None  # Full 'by tactic1; tactic2'
    iterations_executed: int
    total_nodes_expanded: int
    execution_time_ms: int
    winning_path_tactics: List[str] = Field(default_factory=list)
```

---

### 2.6 Next.js Spatial Canvas Dashboard API Endpoints & Visual Graph State (R6: UI)

#### Reasoning
Requirement R6 requires a Next.js spatial canvas frontend displaying the scientific knowledge graph, nodes, citation lineages, and verification statuses. We define REST and WebSocket payloads with 2D coordinates $(x, y)$, visual node styling, and real-time streaming contracts.

#### Visual Data Contracts (TypeScript Interfaces for Next.js)
```typescript
// Spatial Canvas Node & Edge TypeScript Interfaces
export type EpistemicStatus = 'VERIFIED' | 'CONJECTURED' | 'REFUTED' | 'UNDER_REVIEW';
export type VerificationTier = 0 | 1 | 2 | 3;
export type NodeType = 'PAPER' | 'AUTHOR' | 'CONCEPT' | 'MATHEMATICAL_CLAIM' | 'EXPERIMENTAL_FACT' | 'DATASET';
export type EdgeType = 'CITES' | 'PROVES' | 'REFUTES' | 'CONTRADICTS' | 'EXTENDS' | 'CORROBORATES' | 'USES_METHOD';

export interface SpatialPosition {
  x: number;
  y: number;
  z?: number;
}

export interface VisualNodeStyle {
  color: string;           // Green (#22c55e) for VERIFIED, Amber (#f59e0b) for CONJECTURED, Red (#ef4444) for REFUTED
  icon: string;
  size: number;
  borderWidth: number;
}

export interface SpatialNode {
  id: string;
  type: NodeType;
  name: string;
  epistemicStatus: EpistemicStatus;
  verificationTier: VerificationTier;
  position: SpatialPosition;
  style: VisualNodeStyle;
  metadata: Record<string, any>;
}

export interface VisualEdgeStyle {
  strokeColor: string;
  strokeDasharray?: string; // Dashed for CITES, Solid for PROVES/EXTENDS
  strokeWidth: number;
  animated?: boolean;
}

export interface SpatialEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  confidence: number;
  style: VisualEdgeStyle;
}

export interface SpatialGraphDataResponse {
  nodes: SpatialNode[];
  edges: SpatialEdge[];
  summary: {
    totalNodes: number;
    totalEdges: number;
    verifiedClaimsCount: number;
    refutedClaimsCount: number;
  };
}

export interface MCTSProgressWebSocketEvent {
  eventType: 'MCTS_NODE_EXPANDED' | 'MCTS_PROOF_FOUND' | 'SMT_COUNTEREXAMPLE_DETECTED';
  claimId: string;
  iteration: number;
  currentGoal: string;
  tacticApplied: string;
  isSolved: boolean;
  timestamp: number;
}
```

#### API Endpoint Specifications (FastAPI / REST & WS)
1. `GET /api/v1/graph/spatial`
   - Response: `SpatialGraphDataResponse`
   - Returns full graph with 2D spatial positions, verification colors, and edge styles.
2. `GET /api/v1/graph/nodes/{node_id}`
   - Response: Detailed `ScientificNode` JSON + proof lineage + verification history.
3. `POST /api/v1/graph/layout/recompute`
   - Request: `{ algorithm: "force_directed" | "dag_hierarchical" }`
   - Response: Updated node position coordinates `{ [node_id: string]: SpatialPosition }`.
4. `POST /api/v1/ingest/paper`
   - Request: `{ arxiv_id: string }`
   - Response: `IngestedPaperGraphPayload`.
5. `POST /api/v1/proof/verify/smt`
   - Request: `SMTCheckRequest`
   - Response: `SMTCheckResponse`.
6. `POST /api/v1/proof/mcts/search`
   - Request: `MCTSProofSearchRequest`
   - Response: `MCTSProofSearchResponse`.
7. `WS /api/v1/ws/live-stream`
   - Real-time WebSocket connection streaming `MCTSProgressWebSocketEvent` and graph update notifications.

---

### 2.7 System Module Dependency Graph & Milestone Execution Ordering

```
+-----------------------------------------------------------------------------------+
|                                  AXIOM PLATFORM                                   |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                     R4: Graph Store & Database (EGS)                        |  |
|  |             SQLite Relational Store, Schema, Node/Edge Storage              |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                 R1: Epistemic Ingest & LaTeX Parser (EIE)                   |  |
|  |            LaTeX AST Parsing, Citation Graph, Math Environment              |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |              R2: Logical Reasoning & Proof Exporter (LRK)                   |  |
|  |           LaTeX-to-Lean 4 AST Exporter & Lean Compiler Gateway              |  |
|  +-------------------+-------------------------------------+-------------------+  |
|                      |                                     |                      |
|                      v                                     v                      |
|  +---------------------------------------+   +---------------------------------+  |
|  |   R3: Verification & SMT Gateway (AVT)|   | R5: MCTS Proof Search (DRSP)    |  |
|  |   Z3 Counterexamples (<60s sweeps)    |   | MCTS Tactics & Proof Discovery  |  |
|  +-------------------+-------------------+   +-----------------+---------------+  |
|                      |                                     |                      |
|                      +------------------+------------------+                      |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                 R6: Spatial Canvas Dashboard Frontend (UI)                  |  |
|  |          FastAPI REST/WS Endpoints + Next.js Node-Link Spatial UI           |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

#### Milestone Dependency Sequence
1. **Milestone 1: EGS & EIE (Data Foundation & Ingestion)**
   - Build SQLite relational tables, Pydantic node/edge models, NetworkX cycle detection.
   - Implement LaTeX AST parser for arXiv source archives (`IngestedPaperGraphPayload`).
2. **Milestone 2: LRK & AVT (Formalization & Verification)**
   - Implement Lean 4 AST generator and Lean compilation checker.
   - Implement Z3 SMT gateway for parameter bound sweeps (<60s counterexample detection).
3. **Milestone 3: DRSP (Autonomous Discovery & Proof Search)**
   - Implement MCTS proof search algorithm exploring Lean tactics to solve algebra lemmas.
   - Update SQLite database nodes with `VERIFIED` / `TIER_2_PROVEN` status upon success.
4. **Milestone 4: UI & API Gateway (Interactive Spatial Canvas)**
   - Build FastAPI REST and WebSocket streaming endpoints.
   - Implement Next.js React frontend spatial canvas visualizing knowledge graph, proof lineage, and MCTS tree progression.

---

## 3. Caveats

1. **SQLite Concurrency**: SQLite is used for local storage (`EpistemicStore`). Simultaneous write operations across multi-threaded MCTS runs or background ingestion tasks must use WAL (Write-Ahead Logging) mode (`PRAGMA journal_mode=WAL;`) to avoid database lock errors.
2. **Lean 4 Environment Dependency**: Translating LaTeX claims into compilable Lean 4 declarations requires an installed `elan`/`lean4` executable or a local Lean 4 server process. In environments without Lean 4 CLI installed, mock/fallback compilation stubs should be configured for testing.
3. **Z3 / SMT Parameter Sweeps**: SMT solver parameter sweeps are bounded to a specified timeout (60,000 ms). Complex non-linear real arithmetic (QF_NRA) might return `UNKNOWN` or timeout if parameter ranges are overly broad.

---

## 4. Conclusion

- Explorer 3 has completed the full survey of data models, shared types, interface contracts, and module dependency graphs across R1-R6.
- Complete Pydantic schemas and TypeScript interfaces have been designed for LaTeX AST ingestion (R1), SQLite relational storage & circular reference prevention (R4), Lean 4 AST declaration generation (R2), SMT / Z3 counterexample checking (R3), MCTS proof search tree state (R5), and Next.js spatial canvas API endpoints (R6).
- Clear 4-phase milestone dependency ordering is established: EGS & EIE -> LRK & AVT -> DRSP -> UI & API Gateway.

---

## 5. Verification Method

To independently verify the schema models and interface definitions proposed in this report:

1. **Schema File Verification**:
   Inspect existing Pydantic models in `axiom/core/knowledge_graph/schema.py` and `db.py`:
   ```bash
   python3 -c "from axiom.core.knowledge_graph.schema import KnowledgeGraph, MathematicalClaimNode; print(MathematicalClaimNode.__fields__.keys())"
   ```

2. **Cycle Detection Method Verification**:
   Verify NetworkX graph cycle detection logic on SQLite store:
   ```bash
   python3 -c "from axiom.core.knowledge_graph.db import EpistemicStore; from axiom.core.parser.semantic_tracker import SemanticTracker; store = EpistemicStore(); tracker = SemanticTracker(store); print(tracker.detect_circular_dependencies())"
   ```

3. **API & Test Suite Execution**:
   Run the existing API test suite to verify current endpoint baseline:
   ```bash
   pytest tests/test_api.py
   ```
