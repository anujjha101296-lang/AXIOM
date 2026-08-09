# Routing Policy

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Selection criteria

Routing optimizes across (not solely cost):

1. **Accuracy** — capability benchmark scores
2. **Reliability** — model reliability score minus failure memory penalties
3. **Scientific capability** — match to required EPIC-002 dimensions
4. **Verification quality** — verification-aware routing (SIMR §14)
5. **Cost** — budget constraints when specified
6. **Latency** — secondary factor

## Rules

| Rule | Enforcement |
|------|-------------|
| No silent model changes | Fallback recorded in routing decision |
| Formal verification required | Prefer `lean_exporter`, `smt_gateway` |
| High uncertainty | Select multiple strategies |
| Frontier problems | Trigger human expert review |
| Repeated model failures | Deprioritize via failure memory |
| Model agreement ≠ proof | Multi-model consensus increases confidence only with independence |

## Fallback chain

`gpt-4o` → `gpt-4o-mini` → `mock-model`  
`gemini-pro` → `gemini-1.5-flash` → `mock-model`

## API

```bash
POST /routing/select
POST /routing/compile
```

## Refresh

```bash
make simr-health
```
