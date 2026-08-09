# Research Benchmark Arena Status

**Updated:** 2026-08-09  
**Package:** `axiom/evaluation/arena/`  
**Datasets:** `arena_v1` (60, immutable) + `arena_ext_sec_lh_v1` (13)

## Cycle results

| Suite | Passed | Tier unlocked | Notes |
|-------|--------|---------------|-------|
| arena_v1 baseline | 59/60 → 60/60 | 7 | Soft-capped LH |
| arena_v1 + sec/LH | **73/73** | **9** (<10) | Measured LH; Millennium blocked |

**Bug found by Arena:** pilot experiment IDs were wiped on status transition — fixed (save-before-transition).


## SCEP CI fix (this cycle)

- Audit doc + CLI paths resolve via repo root when pytest cwd is `/tmp`
- `tests/test_evaluation_platform.py` + `test_scep_e2e.py` green from `/tmp`

## Honesty

- `arena_v1` not silently modified
- Extension is a new dataset version
- Millennium never auto-claimed
- Catalog never exposes `_grader` / ground truth
