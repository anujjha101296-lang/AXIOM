# Experiment Engine

**Last updated:** 2026-08-09  
**Loop:** SEC (Scientific Experimentation & Compute)

## Status

| Component | Status |
|-----------|--------|
| Experiment kernel | ✅ New |
| Lifecycle management | ✅ DRAFT → VALIDATED → QUEUED → RUNNING → COMPLETED/FAILED |
| Versioned artifacts | ✅ `sec_experiment_versions` |
| Hypothesis linking | ✅ claim_id, hypothesis_id, campaign_id |
| Dashboard | ✅ `GET /experiments/dashboard/summary` |

## API

```bash
POST /experiments/
POST /experiments/{id}/run
GET  /experiments/{id}/integrity
```

## Refresh

```bash
make sec-health
```
