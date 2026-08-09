# Reproduction Guide

**Last updated:** 2026-08-09  
**Loop:** SEC

## Reproduction statuses

| Status | Meaning |
|--------|---------|
| `EXACT_REPRODUCTION` | Environment and outputs match |
| `APPROXIMATE_REPRODUCTION` | Minor differences |
| `PARTIAL_REPRODUCTION` | Some outputs match |
| `FAILED_REPRODUCTION` | Material differences |
| `UNABLE_TO_REPRODUCE` | Missing artifacts or config |

## API

```bash
POST /experiments/reproduce?original_id=...&reproduction_id=...
```

## Requirements

Record: random seed, code version, environment fingerprint, dataset version, tool versions.

When exact reproduction is impossible, document the source of nondeterminism.

## Refresh

```bash
make sec-health
```
