# AXIOM State

**Last updated:** 2026-08-09  
**Directive:** AXIOM-MASTER-001  
**Branch:** `cursor/integrate-mainline-dc7e`

## One-line status

Integrated tip includes Scientific Discovery Engine v0.1 (gap→hypotheses→experiments→counterexample→attack) with FDR=0 on deterministic traps; ready for founder merge.

## What works

| Area | Status |
|------|--------|
| Research / auth / ownership / campaigns / experiments | Live |
| Docker compose api+ui smoke | Live |
| Controlled web acquire `/sources` + `/skai/acquire-url` | Live (allowlisted HTTPS, UNTRUSTED, dedupe) |
| **Scientific Discovery Engine** `/discovery` | **Partial live** — cycle + benchmarks + human control; no novelty claims |

## Next

1. **Founder merges PR #29 to `main`**
2. Enrich novelty search / formal bridge inside discovery cycle
3. Fix remaining SCEP CI doc failures

## Evidence

- `tests/test_discovery_engine.py` green
- `docs/DISCOVERY_ENGINE_STATUS.md`
- PR: https://github.com/anujjha101296-lang/AXIOM/pull/29
