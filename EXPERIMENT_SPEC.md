# Experiment Specification

**Last updated:** 2026-08-09  
**Loop:** SEC

## Required fields

- `research_question`
- `hypothesis`
- `objective`
- `resource_budget` (timeout, memory, disk, network policy)

## Optional fields

- `variables`, `inputs`, `procedure`
- `expected_observation`
- `code`, `random_seed`, `tools`
- `evaluation_metrics`, `stopping_conditions`
- `reproduction_instructions`

## Validation

Invalid specs are rejected before execution with explicit errors.

## Refresh

```bash
make sec-health
```
