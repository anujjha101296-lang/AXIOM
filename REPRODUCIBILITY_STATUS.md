# Reproducibility Status

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Run provenance (H1-OBS) | ✅ | SCEP/RVP envelopes in `run_provenance` |
| Reproduction comparison | ✅ New | `compare_provenance_runs()` + API |
| Experiment registry | ✅ New | `er_experiments` table |
| Determinism control | ⚠️ Partial | Environment fingerprint captured; seeds pending |
| Independent re-run | ⚠️ Partial | Compare API exists; automated re-run pending |

## Reproduction classifications

| Status | Meaning |
|--------|---------|
| `REPRODUCED` | Inputs, scores, and environment match within tolerance |
| `PARTIALLY_REPRODUCED` | Minor differences (≤2 fields) |
| `NOT_REPRODUCED` | Material differences detected |
| `UNABLE_TO_REPRODUCE` | Missing provenance or inputs |

## API

```bash
POST /evidence/reproduction/compare
{
  "run_type": "scep",
  "original_run_id": "...",
  "reproduction_run_id": "..."
}
```

## Known limitations

- Nondeterministic LLM outputs are explicitly not claimed as exactly reproducible
- Full environment reconstruction (dependency lockfiles, container images) is not yet automated
- Random seed recording depends on experiment configuration being supplied

## Refresh

```bash
make erl-health
```
