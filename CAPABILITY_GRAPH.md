# Capability Graph

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Structure

```text
Research Problem
    ↓
Required Capabilities (EPIC-002 dimensions)
    ↓
Available Models / Tools
    ↓
Possible Strategies
    ↓
Verification Methods
```

## EPIC-002 dimensions

- `mathematical_reasoning`
- `proof_verification`
- `conjecture_generation`
- `knowledge_quality`
- `counterexample_search`
- `research_planning`
- `literature_synthesis`
- `research_productivity`

## Resolution

`axiom/routing/capability_graph.py` maps problem profiles to capability nodes with recommended models, tools, and verifiers.

## Integration

GCP challenges declare `required_capabilities` and `required_tools` — SIMR uses the same vocabulary.

## Refresh

```bash
make simr-health
```
