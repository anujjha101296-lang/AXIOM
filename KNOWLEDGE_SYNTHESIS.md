# Knowledge Synthesis

## Synthesis pipeline

1. Reasoning-aware retrieval (by research requirements, not embeddings)
2. Literature coverage estimation
3. Conflict detection
4. Research gap detection
5. Structured synthesis output

## Conflict format

```text
KNOWLEDGE CONFLICT
Claim: X
Position A / Position B
Evidence / Assumptions / Resolution / Current confidence
```

Unresolved conflicts → research tasks in FRCE.

## Gap types

- `unresolved_conflict`
- `open_question`
- `unverified_conjecture`
- `shared_dependency`

Gaps are **opportunities**, not discoveries.

## Synthesis disclaimer

All synthesis outputs include: `"Computational synthesis — not established scientific fact"`
