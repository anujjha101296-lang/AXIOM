# Formal Benchmarks

**Last updated:** 2026-08-09  
**Loop:** FMTP

## Levels

| Level | Description | Tasks |
|------:|-------------|-------|
| 0 | Basic formalization | 2 |
| 1 | Elementary theorem proving | 2 |
| 2 | Competition mathematics | 2 |
| 3 | Graduate mathematics | 1 |
| 4 | Published theorem reproduction | 1 |
| 5–7 | Research / open problems | Planned |

## Metrics (planned)

Statement correctness, formalization success, proof success, proof search time, proof length, library reuse, human intervention, verification rate, failure recovery, reproducibility.

## API

```bash
GET /formal/benchmarks
GET /formal/difficulty?statement=...
```

## Policy

Do not skip levels because a model produces plausible text.

## Refresh

```bash
make fmtp-health
```
