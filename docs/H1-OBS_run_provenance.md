# H1-OBS — Evaluation Provenance Records

**Status:** Implemented  
**Task ID:** H1-OBS  
**Depends on:** S0-E4 evidence gate

## Purpose

Every SCEP (EPIC-002) and RVP evaluation run now records an auditable provenance envelope: inputs, runtime, configuration, environment fingerprint, and evidence tier. Provenance is stored in a unified `run_provenance` table without duplicating score payloads in `eval_runs` or `rvp_runs`.

## Architecture

```
POST /eval/run ──► run_all_capability_benchmarks()
                        │
                        ▼
                  record_scep_run() ──► run_provenance (type=scep)

POST /rvp/runs ──► ResearchValidationEngine._run_single()
                        │
                        ▼
                  record_rvp_run() ──► run_provenance (type=rvp)
```

**Module:** `axiom/observability/run_provenance.py`  
**API:** `axiom/services/api_gateway/routes/provenance_api.py`

## Provenance envelope fields

| Field | Description |
|-------|-------------|
| `run_id` | Matches `eval_runs.run_id` or `rvp_runs.run_id` |
| `run_type` | `scep` or `rvp` |
| `started_at` / `finished_at` | ISO-8601 UTC timestamps |
| `duration_ms` | Wall-clock duration |
| `config_hash` | RVP config hash (null for SCEP) |
| `inputs` | Run inputs (db_path, stage, problem_id, benchmark counts) |
| `environment` | python_version, git_sha, app_version, platform |
| `evidence_tier` | Aggregate and per-dimension evidence states |
| `runtime` | Benchmark timing details |

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /provenance/runs` | List provenance records (`?run_type=scep\|rvp`) |
| `GET /provenance/runs/{run_type}/{run_id}` | Full provenance envelope |
| `GET /eval/runs/{run_id}` | SCEP snapshot + provenance |
| `GET /eval/history` | Enriched with `duration_ms`, `evidence_tier` |

## Usage

```bash
# Trigger SCEP benchmark (records provenance automatically)
curl -X POST http://localhost:8000/eval/run

# Fetch provenance for a run
curl http://localhost:8000/provenance/runs/scep/{run_id}

# List all RVP provenance records
curl "http://localhost:8000/provenance/runs?run_type=rvp"
```

CLI benchmark runner also records provenance:

```bash
python3 -m axiom.evaluation.run_benchmarks --db axiom.db
```

## Tests

```bash
pytest tests/test_run_provenance.py -v
```

13 tests cover helpers, store persistence, API integration, and RVP engine hooks.

## Acceptance criteria (from TASK_QUEUE)

- [x] A result can identify **inputs** — stored in `inputs` dict
- [x] A result can identify **runtime** — `duration_ms`, `started_at`, `finished_at`
- [x] A result can identify **configuration** — `config_hash` (RVP), trigger/db_path (SCEP)
- [x] A result can identify **evidence tier** — `evidence_tier.aggregate` with per-dimension rollup

## Limitations

- SCEP runs do not yet have a config hash (deterministic inputs assumed).
- Environment capture requires git for `git_sha`; fails gracefully if unavailable.
- Provenance store uses per-path singleton cache for `:memory:` test databases.
