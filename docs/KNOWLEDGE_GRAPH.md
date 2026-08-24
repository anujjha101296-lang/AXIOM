# AXIOM Phase 13 — Scientific Knowledge Graph & Claim Graph Architecture

## 1. Overview
AXIOM Phase 13 introduces a persistent, provenance-backed Scientific Knowledge Graph and Claim Graph representation. Instead of treating LLM extractions as unverified facts, Phase 13 models claims and entities as evidence-backed assertions with explicit epistemic status and strict project isolation.

---

## 2. Canonical Domain Model

### Entities & Aliases (`graph_entities`, `graph_entity_aliases`)
- **`GraphEntity`**: Uniquely identified entity (`id`, `project_id`, `name`, `entity_type`, `domain`, `description`, `metadata`). Controlled entity taxonomy: `person`, `organization`, `method`, `algorithm`, `theorem`, `mathematical_object`, `physical_object`, `dataset`, `software`, `concept`, `paper`, `research_field`.
- **`GraphEntityAlias`**: Maps alternative names/acronyms (e.g. `"SMT"` to `"Satisfiability Modulo Theories"`).

### Claims & Evidence Links (`graph_claims`, `graph_claim_evidences`)
- **`GraphClaim`**: Structured assertion (`id`, `project_id`, `claim_text`, `claim_type`, `epistemic_status`, `confidence_score`). Claim types: `FACTUAL`, `DEFINITIONAL`, `QUANTITATIVE`, `CAUSAL`, `COMPARATIVE`, `METHODOLOGICAL`, `OTHER`. Epistemic status: `EXTRACTED`, `INFERRED`, `HYPOTHESIS`, `VERIFIED`, `CONTRADICTED`, `REJECTED`, `UNRESOLVED`.
- **`GraphClaimEvidence`**: Connects claim to underlying document chunk/source (`claim_id`, `chunk_id`, `source_id`, `document_id`, `supports`, `snippet`).

### Typed Relationships & Evidence (`graph_relationships`, `graph_relationship_evidences`)
- **`GraphRelationship`**: Directed edge (`subject_entity_id`, `object_entity_id`, `predicate`, `status`). Predicates: `USES`, `PART_OF`, `DEPENDS_ON`, `IMPROVES`, `CAUSES`, `MEASURES`, `APPLIES_TO`, `RELATED_TO`, `PROPOSES`, `CONTRADICTS`, `SUPPORTS`.

### Contradictions & Disagreements (`graph_contradictions`)
- **`GraphContradiction`**: Represents explicit logical or quantitative disagreements (`claim_a_id`, `claim_b_id`, `contradiction_type`, `reasoning`, `resolved`). Contradictions are NEVER deleted to make the graph cleaner.

### Research Gap Identification (`graph_research_gaps`)
- **`GraphResearchGap`**: Identifies areas of missing, weak, or conflicting evidence (`gap_type`, `description`, `severity`). Gap types: `NO_EVIDENCE`, `WEAK_EVIDENCE`, `CONFLICTING_EVIDENCE`, `INFERRED_ONLY`, `MISSING_RELATIONSHIP`, `UNRESOLVED_QUESTION`.

---

## 3. Provenance Chain & Safety
Every claim must maintain a complete provenance chain:
$$\text{CLAIM} \longrightarrow \text{EVIDENCE} \longrightarrow \text{CHUNK} \longrightarrow \text{SOURCE} \longrightarrow \text{DOCUMENT/URL}$$

Unbacked claims or prompt injection text found in evidence are kept strictly as data strings and never promoted to verified facts or executable instructions.

---

## 4. Conservative Entity Resolution
To prevent accidental merging of distinct concepts:
$$\text{NEW ENTITY} \longrightarrow \text{NORMALIZE} \longrightarrow \text{EXACT MATCH} \longrightarrow \text{ALIAS MATCH} \longrightarrow \text{HIGH-CONFIDENCE MATCH} \longrightarrow \text{AMBIGUOUS?} \longrightarrow \begin{cases} \text{KEEP SEPARATE} \\ \text{LINK / ALIAS} \end{cases}$$

---

## 5. REST API Endpoints
- `POST /api/v1/knowledge-graph/extract`: Extract & persist claims and entities from text for a project.
- `GET /api/v1/knowledge-graph/summary/{project_id}`: Retrieve graph nodes, claims, relationships, contradictions, and gaps.
- `GET /api/v1/knowledge-graph/claims/{claim_id}/provenance`: Retrieve provenance chain for a claim.

---

## 6. Database Schema & Migration
- Alembic Migration: `d3e46185a740_add_phase13_knowledge_graph_tables.py`
- Relational tables with foreign key cascades on `projects.id`, indexed by `project_id`.
