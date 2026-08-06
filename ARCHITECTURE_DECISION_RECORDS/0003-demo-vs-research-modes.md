# ADR-0003: Demo Mode vs Research Mode

**Status:** Accepted  
**Date:** 2026-08-06

## Context

AXIOM ships a Golden Demo (`/demo`) for presentations and a Research Workspace (`/research`) for live work. Curated demo outputs must never be mistaken for measured scientific capability.

## Decision

Maintain **two explicit operation modes** with machine-readable contracts in `axiom/modes.py`:

| Mode | Purpose | `represents_scientific_capability` |
|------|---------|-----------------------------------|
| **Demo Mode** | Presentation reliability (conferences, YC, investors) | `false` |
| **Research Mode** | Real PDFs, models, uncertainty | `true` |

**Requirements:**
- Persistent UI banner on every mode-specific page
- API endpoints: `GET /demo/mode`, `/research/mode`, `/research-loop/mode`
- Demo payloads include `operation_mode` and `illustrative_only` markers
- Presenters must verbally identify Demo Mode

Full policy: `docs/MODES.md`.

## Consequences

- **Positive:** Honest capability claims; regulatory and investor trust
- **Positive:** Demo reliability without faking live inference
- **Negative:** Two code paths to maintain (demo data vs live store)
- **Invariant:** No PR may remove mode indicators or imply demo outputs are live AI
