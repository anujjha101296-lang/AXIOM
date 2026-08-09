# Theorem Proving Status

**Last updated:** 2026-08-09  
**Loop:** FMTP

## Capabilities

| Capability | Status |
|------------|--------|
| Proof strategy generation | ✅ |
| Proof decomposition | ✅ |
| Proof repair suggestions | ✅ |
| Independent proof paths | ⚠️ Planned |
| Proof artifact versioning | ✅ |
| Dependency graph | ✅ |
| Formal compilation check | ✅ (simulation when Lean absent) |

## Compilation states

`COMPILES`, `DOES_NOT_COMPILE`, `PARTIALLY_FORMALIZED`, `DEPENDENCY_FAILURE`, `TIMEOUT`, `RESOURCE_LIMIT`, `UNKNOWN`, `FORMALLY_VERIFIED`

`FORMALLY_VERIFIED` requires actual prover acceptance — never from LLM assertion alone.

## API

```bash
POST /formal/proof/search
POST /formal/proof/compile
GET /formal/proof/strategies?statement=...
```

## Refresh

```bash
make fmtp-health
```
