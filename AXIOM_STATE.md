# AXIOM State

**Last updated:** 2026-08-09  
**Directive:** AXIOM-MASTER-001  
**Branch:** `cursor/integrate-mainline-dc7e`

## One-line status

Integrated tip is MVP-ready for founder merge, including controlled UNTRUSTED web source acquisition.

## What works

| Area | Status |
|------|--------|
| Research / auth / ownership / campaigns / experiments | Live |
| Docker compose api+ui smoke | Live |
| Controlled web acquire `/sources` + `/skai/acquire-url` | Live (allowlisted HTTPS, UNTRUSTED, dedupe) |

## Next

1. **Founder merges PR #29 to `main`**
2. Fix remaining SCEP CI doc failures
3. Close superseded draft PRs after merge

## Evidence

- `tests/test_mvp_web_research.py` green
- PR: https://github.com/anujjha101296-lang/AXIOM/pull/29
