# Scientific Knowledge Acquisition & Intelligence Loop (SKAI)

AXIOM's system for building and maintaining a model of scientific knowledge — much more than RAG.

## Mission

Go from "I need to understand everything relevant to this problem" to "here is the current state of knowledge, what has been proven, what has failed, what remains unknown, and where opportunity appears."

## Continuous loop

```text
RESEARCH QUESTION → KNOWLEDGE REQUIREMENTS → SOURCE DISCOVERY → QUALITY ASSESSMENT
  → ACQUISITION → STRUCTURE EXTRACTION → KNOWLEDGE GRAPH → EVIDENCE/PROVENANCE
  → CONFLICT DETECTION → SYNTHESIS → GAP DETECTION → HYPOTHESES → CAMPAIGN ENGINE
  → NEW RESULTS → KNOWLEDGE UPDATE ↺
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `KNOWLEDGE_ACQUISITION.md` | Acquisition pipeline status |
| `KNOWLEDGE_GRAPH_SPEC.md` | Scientific knowledge graph spec |
| `SOURCE_QUALITY.md` | Source quality tiers |
| `KNOWLEDGE_SYNTHESIS.md` | Synthesis and gap detection |
| `KNOWLEDGE_BENCHMARKS.md` | Benchmark categories |
| `scripts/skai_health_check.py` | Automated SKAI gate |

## Code modules

- `axiom/skai/orchestrator.py` — main acquisition loop
- `axiom/skai/store.py` — sources, entities, relations, conflicts, gaps
- `axiom/skai/extractor.py` — paper structure extraction
- `axiom/skai/bridge.py` — EGS ↔ E&R ↔ SKAI bridge
- `axiom/skai/conflicts.py` — knowledge conflict detection
- `axiom/skai/gaps.py` — research gap detector
- `axiom/skai/retrieval.py` — reasoning-aware retrieval
- `axiom/skai/saturation.py` — literature coverage estimation
- `axiom/services/api_gateway/routes/skai_api.py` — `/skai/*` API

## Principles

- Never store paragraphs without full provenance
- Source quality is explicit metadata
- Unresolved conflicts become research tasks
- Never silently rewrite historical knowledge
- Weak claims never become trusted through repetition
- Scope isolation: global / organization / campaign / private

## Integration

- **EGS** — Epistemic Graph Store nodes and edges
- **E&R** — claims, sources, quotation evidence
- **FRCE** — literature track in campaign cycles
- **Research Workspace** — PDF/text acquisition path

## Production requirements

```bash
REQUIRE_AUTH_FOR_SKAI_ROUTES=true
```
