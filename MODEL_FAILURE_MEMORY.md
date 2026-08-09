# Model Failure Memory

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Tracked failure types

- Hallucinations
- Reasoning errors
- Citation errors
- Mathematical mistakes
- Tool misuse
- Prompt sensitivity
- Long-context degradation

## Storage

SQLite table `simr_failures` — per-model failure records with capability and domain context.

## Adaptive routing

Models with ≥2 failures in a capability are deprioritized (not removed) for that capability.

## API

```bash
POST /routing/failures
GET /routing/failures?model_id=gpt-4o-mini
```

## Knowledge conflicts

Conflicting sources are recorded in `simr_conflicts` — never auto-resolved.

```bash
POST /routing/conflicts
```

## Refresh

```bash
make simr-health
```
