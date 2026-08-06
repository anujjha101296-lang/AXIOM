# AXIOM Golden Demo — Demo Guide

**Version:** v0.5-demo  
**Milestone:** 006  
**URL:** `http://localhost:3000/demo` (UI) · `http://localhost:8000/demo/state` (API)

---

## What This Demo Shows

A researcher arrives with a **new topic** (GNN generalization for drug discovery). In under five minutes, AXIOM:

1. Creates a research project with a precise question
2. Ingests three foundational papers
3. Extracts concepts and builds an evidence graph
4. Creates structured, tagged notes
5. Detects contradictions across papers
6. Identifies research gaps
7. Proposes testable hypotheses
8. Plans experiments with expected outcomes
9. Produces a professional research report

**No technical documentation required** for a first-time viewer.

**Important:** This page runs in **Demo Mode** — curated illustration only. It does **not** represent live AI or measured scientific capability. For real work, use **Research Mode** at `/research`. See `docs/MODES.md`.

---

## Operation Modes

| Mode | URL | Capability claims? |
|------|-----|------------------|
| **Demo Mode** | `/demo` | **No** — presentation reliability |
| **Research Mode** | `/research` | Yes — with uncertainty |

A persistent banner on every page indicates the active mode.

---

## Quick Start

```bash
# Terminal 1 — API
AXIOM_API_TOKEN=axiom-dev-token python3 -m uvicorn axiom.services.api_gateway.main:app --port 8000

# Terminal 2 — UI
cd ui && npm install && npm run dev

# Open
open http://localhost:3000/demo
```

Or run the automated script:

```bash
bash scripts/demo_golden.sh
```

---

## Demo Modes

| Mode | How to activate | Best for |
|------|-----------------|----------|
| **Play Demo** | Click ▶ Play Demo on `/demo` | Live presentations, YC, investors |
| **Guided Tour** | Click Guided Tour | Step-by-step walkthrough with narration prompts |
| **Replay** | Click ↺ Replay after completion | Second viewing, Q&A sessions |
| **API** | `GET /demo/state` | Engineers integrating with AXIOM |

---

## Audience Tips

### Researchers
Focus on contradictions, gaps, and experiment plans. Emphasize evidence classification.

### YC / Investors
Lead with Play Demo. Value prop: "4 minutes from papers to research program."

### Engineers
Show `/demo/state` JSON schema and evidence graph structure. Link to Research Workspace at `/research`.

### Enterprise
Highlight reproducibility, explicit limitations, and session memory.

---

## Sample Dataset

Located in `demo/sample_dataset/`:

- `papers/` — three markdown paper excerpts (Gilmer, Hu, Sun)
- `example_outputs.json` — expected output counts

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Loading Golden Demo…" stuck | Ensure API is running on port 8000 |
| CORS error | Check `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| Animations too fast | Use Guided Tour for manual pacing |

---

## Honest Limitations

This Golden Demo uses **curated sample data** for presentation reliability. The live Research Workspace at `/research` supports real PDF upload and Q&A. Demo outputs are pre-authored to guarantee a flawless five-minute narrative.

See `docs/MILESTONE_006.md` for full scope and limitations.
