# Release Notes — v0.5-demo

**Release:** v0.5-demo (Release Candidate)  
**Date:** 2026-08-06  
**Milestone:** 006 — Golden Demo

---

## Highlights

AXIOM's **Golden Demo** is a self-contained, five-minute presentation that shows a complete research session — from new topic to professional report — without requiring technical documentation or live setup.

**Try it:** `http://localhost:3000/demo`

---

## New Features

### Demo Mode (`/demo`)
- Auto-play engine with 12-phase state machine
- Curated GNN drug-discovery research scenario
- Progress visualization and live stats strip
- Replay and pause controls

### Interactive Tour
- 10-step guided walkthrough with presenter prompts
- Skip, back, next, and dot navigation

### Visualizations
- **Evidence Graph** — animated SVG knowledge graph with typed nodes
- **Research Tree** — hierarchical project → papers → hypotheses → experiments
- **Research Timeline** — phase-by-phase progress tracker

### Demo API (public, no auth)
- `GET /demo/state` — full curated demo payload
- `GET /demo/tour` — tour steps
- `GET /demo/health` — demo subsystem status

### Sample Dataset
- `demo/sample_dataset/papers/` — three paper excerpts
- `demo/sample_dataset/example_outputs.json` — expected output counts

### Documentation
- `docs/demo/DEMO_GUIDE.md`
- `docs/demo/PRESENTER_NOTES.md`
- `docs/demo/ARCHITECTURE_DIAGRAM.md`
- `docs/demo/PRODUCT_DIAGRAM.md`
- `docs/demo/SYSTEM_DIAGRAM.md`
- `docs/demo/DEMO_VIDEO_SCRIPT.md`
- `docs/MILESTONE_006.md`

### Landing Page
- Primary CTA: **Watch Golden Demo**
- Nav link to `/demo`

---

## Technical

| Component | Change |
|-----------|--------|
| Version | `0.3.0` → `0.5.0` |
| New package | `axiom/demo/` |
| New route | `axiom/services/api_gateway/routes/demo.py` |
| New UI | `ui/src/app/demo/`, `ui/src/components/demo/` |
| Tests | `tests/test_demo_api.py` (5 tests) |
| Script | `scripts/demo_golden.sh` |

---

## Test Evidence

```
pytest tests/test_demo_api.py  →  5 passed
pytest tests/ --ignore=tests/e2e  →  187 passed (core suite)
```

---

## Known Limitations

1. **Curated data** — Demo uses pre-authored content for presentation reliability; not live LLM extraction
2. **Read-only** — Demo does not write to Research Workspace database
3. **No auth** — `/demo` is public; no user session required
4. **API dependency** — UI requires API on port 8000 for state fetch

See `docs/MILESTONE_006.md` for honest scope boundaries.

---

## Upgrade Notes

No breaking API changes. New endpoints are additive under `/demo/*`.

```bash
git checkout v0.5-demo
pip install -e .
cd ui && npm install && npm run dev
bash scripts/demo_golden.sh
```

---

## What's Next

- S0-E4 EPIC-002 integration gate (engineering baseline)
- Wire Golden Demo to seed real Research Workspace projects
- Record official demo video per `DEMO_VIDEO_SCRIPT.md`
