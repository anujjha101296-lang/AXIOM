# Milestone 006 — Golden Demo

**Status:** Complete  
**Version:** v0.5-demo  
**Tests:** 187/187 core pass (includes 5 demo API tests)

---

## Summary

AXIOM's defining demonstration: a five-minute, self-explanatory research session from new topic to professional report. Built for researchers, YC partners, investors, engineers, and enterprise audiences.

**Definition of done met:** A first-time viewer understands AXIOM's value within five minutes without reading technical documentation.

---

## Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| Demo Mode | `/demo` | ✅ Auto-play + pause + replay |
| Sample Dataset | `demo/sample_dataset/` | ✅ 3 papers + outputs JSON |
| Guided Walkthrough | Interactive Tour component | ✅ 10 steps |
| Interactive Tour | `ui/src/components/demo/InteractiveTour.tsx` | ✅ |
| Demo Project | Curated GNN drug discovery scenario | ✅ |
| Example Papers | `demo/sample_dataset/papers/` | ✅ |
| Example Outputs | `example_outputs.json` | ✅ |
| Professional UI | `ui/src/app/demo/` | ✅ |
| Loading states | Demo loading screen + progress bar | ✅ |
| Animations | Phase reveals, graph, papers | ✅ |
| Progress visualization | Top progress strip + stats | ✅ |
| Research timeline | `ResearchTimeline.tsx` | ✅ |
| Evidence graph | `EvidenceGraph.tsx` | ✅ |
| Research tree | `ResearchTree.tsx` | ✅ |
| Demo Guide | `docs/demo/DEMO_GUIDE.md` | ✅ |
| Presenter Notes | `docs/demo/PRESENTER_NOTES.md` | ✅ |
| Architecture Diagram | `docs/demo/ARCHITECTURE_DIAGRAM.md` | ✅ |
| Product Diagram | `docs/demo/PRODUCT_DIAGRAM.md` | ✅ |
| System Diagram | `docs/demo/SYSTEM_DIAGRAM.md` | ✅ |
| Demo Video Script | `docs/demo/DEMO_VIDEO_SCRIPT.md` | ✅ |
| Release Notes | `docs/demo/RELEASE_NOTES_v0.5-demo.md` | ✅ |

---

## Architecture

```
/demo (UI)  →  GET /demo/state  →  axiom/demo/data.py
                                  →  axiom/demo/schema.py
```

Demo is **read-only** and **deterministic** — optimized for flawless presentations.

---

## Demo

```bash
bash scripts/demo_golden.sh
# Open http://localhost:3000/demo
# Click ▶ Play Demo
```

---

## Honest Limitations

1. Curated sample data — not live LLM extraction during demo playback
2. Does not seed Research Workspace database (future enhancement)
3. Requires API running for state fetch
4. Keyword/heuristic narrative; real workspace uses ModelClient for Q&A

---

## Release

```bash
git tag v0.5-demo
```

---

## Next Recommended Milestone

**S0-E4** — EPIC-002 integration gate (per engineering checkpoint), then wire demo-to-workspace seeding for live PDF workflows.
