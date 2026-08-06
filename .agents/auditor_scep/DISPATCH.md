## 2026-08-06T10:53:44Z
<USER_REQUEST>
You are Forensic Auditor (teamwork_preview_auditor) for EPIC-002 SCEP.
Working directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/auditor_scep
Project root: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom

Tasks:
1. Create your working directory if needed. Create BRIEFING.md and progress.md in your working directory.
2. Read ORIGINAL_REQUEST.md at /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/ORIGINAL_REQUEST.md.
3. Read PROJECT.md at /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/orchestrator/PROJECT.md.
4. Conduct thorough forensic integrity audit across all EPIC-002 files:
   - `docs/scientific_capability_framework.md`
   - `docs/audit/EPIC_002_audit.md`
   - `axiom/evaluation/frameworks/capability.py`
   - `axiom/evaluation/frameworks/prize_readiness.py`
   - `axiom/evaluation/benchmarks/suite.py`
   - `axiom/evaluation/reporting/delta_report.py`
   - `axiom/evaluation/run_benchmarks.py`
   - `axiom/services/api_gateway/routes/eval_api.py`
   - `tests/test_evaluation_platform.py`
   - `tests/test_scep_e2e.py`
5. Check for integrity violations:
   - Are any test scores, verification results, or benchmark outputs hardcoded or dummy facades?
   - Are composite scores ($S_{composite} = \sum w_d S_d$) dynamically computed?
   - Are prize readiness scores grounded in benchmark outputs?
   - Is DB persistence (`eval_runs`, `eval_readiness`, `eval_results`) authentic?
   - Does `run_benchmarks.py --compare-previous` exit 0 on pass / no regression and exit 1 on regression > 5%?
6. Write your audit report in `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/auditor_scep/analysis.md` and handoff in `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/auditor_scep/handoff.md`.
7. Issue a clear verdict: CLEAN or INTEGRITY VIOLATION. Send a message back with your verdict and key evidence.
</USER_REQUEST>
