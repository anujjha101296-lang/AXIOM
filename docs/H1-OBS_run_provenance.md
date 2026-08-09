# H1-OBS — Evaluation Provenance Records

**Status:** Implemented  
**Task ID:** H1-OBS  
**Depends on:** S0-E4 evidence gate

## Purpose

Every SCEP (EPIC-002) evaluation run records an auditable provenance envelope: inputs, runtime, configuration, environment fingerprint, and evidence tier. Provenance is stored in a unified `run_provenance` table without duplicating score payloads in `eval_runs`.

## Architecture

```
POST /eval/run ──► trigger_benchmark()
                        │
                        ▼
                  record_scep_run() ──► run_provenance (type=scep)
```

**Module:** `axiom/observability/run_provenance.py`  
**API:** `axiom/services/api_gateway/routes/provenance_api.py`

## Provenance envelope fields

| Field | Description |
|-------|-------------|
| `run_id` | Matches `eval_runs.run_id` |
| `run_type` | `scep` (RVP hook reserved for future) |
| `started_at` / `finished_at` | ISO-8601 UTC timestamps |
| `duration_ms` | Wall-clock duration |
| `config_hash` | Reserved for RVP (null for SCEP) |
| `inputs` | db_path, trigger, benchmark_case_count, composite_score |
| `environment` | python_version, git_sha, app_version, platform |
| `evidence_tier` | From S0-E4 snapshot rollup |
| `runtime` | Benchmark timing details |

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /provenance/runs` | List provenance records (`?run_type=scep`) |
| `GET /provenance/runs/{run_type}/{run_id}` | Full provenance envelope |
| `GET /eval/runs/{run_id}` | SCEP snapshot + provenance |
| `GET /eval/history` | Enriched with `duration_ms`, `evidence_tier` |

## Usage

```bash
curl -X POST http://localhost:8000/eval/run
curl http://localhost:8000/provenance/runs/scep/{run_id}
python3 -m axiom.evaluation.run_benchmarks --db axiom.db
```

## Tests

```bash
pytest tests/test_run_provenance.py -v
```

## Acceptance criteria

- [x] Inputs — stored in `inputs` dict
- [x] Runtime — `duration_ms`, `started_at`, `finished_at`
- [x] Configuration — trigger, db_path (SCEP); config_hash reserved for RVP
- [x] Evidence tier — `evidence_tier.aggregate` from S0-E4 rollup

## Limitations

- RVP integration deferred until Research Validation Program merges to main.
- SCEP runs do not have a config hash (deterministic inputs assumed).
- Environment capture requires git for `git_sha`; fails gracefully if unavailable.
