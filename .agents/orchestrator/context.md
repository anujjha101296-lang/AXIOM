# Context — EPIC-002 Scientific Capability Evaluation Platform (SCEP)

## Project Context
- **Root Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`
- **Orchestrator Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/orchestrator`
- **User Request Source**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/ORIGINAL_REQUEST.md` (`## 2026-08-06T05:55:00Z`)

## Architectural Overview
EPIC-002 SCEP builds an objective evaluation platform for AXIOM AI Scientific Discovery Platform.
It comprises:
1. Scientific Capability Framework (taxonomy, rubrics, composite scoring)
2. Benchmark Suite (runnable, < 2 min total, 5 categories, 3 cases each)
3. Prize Readiness Engine (6 Millennium problems, DB store, REST API)
4. Capability Delta Report Generator (JSON/Markdown formatting per exact prompt specs)
5. Evaluation API & CLI Runner (`run_benchmarks.py --compare-previous`, exit code 0 or 1)
6. Independent Audit Layer (`docs/audit/EPIC_002_audit.md`)
