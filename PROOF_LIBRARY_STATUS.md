# Proof Library Status

**Last updated:** 2026-08-09  
**Loop:** FMTP

## Current library

Builtin seed entries: `add_comm`, `mul_comm`, `lagrange_theorem`, `prime_divisor`

## Search dimensions

Theorem statement, mathematical structure, types, definitions, dependencies, goal shape, relevant concepts.

## Integration

- MIP knowledge store (`mip_objects`)
- Epistemic knowledge graph (`nodes`, `proof_lineage`)
- Mathlib (when Lean4 installed)

## API

```bash
GET /formal/library/search?q=commutativity
```

## Refresh

```bash
make fmtp-health
```
