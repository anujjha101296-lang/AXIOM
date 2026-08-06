# Handoff Report: Scientific Capability Evaluation Platform (SCEP) Specification Mining

> **From**: Spec Miner 3 (`spec_miner_scep_survey_3`)  
> **To**: Orchestrator (`d56bd15b-46e2-449e-bc7e-9f1e4fd24cc5`)  
> **Handoff Type**: Hard  
> **Date**: 2026-08-06  

---

## 1. Observation

Direct code and documentation observations from `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`:

1. **`ORIGINAL_REQUEST.md` (lines 185–226)**:
   - Prescribes exact text template for Capability Delta Report:
     `EPIC-002 COMPLETE\n\nCapability Delta\n\n<Name>\n+<Pct>%\n\nPrize Readiness\n\n<ShortName>\n<Old> → <New>\n\nWeakest Capability\n<Weakest>\n\nHighest Priority\n<Priority>\n\nRecommended Next Epic\n<NextEpic>`
2. **`axiom/evaluation/run_benchmarks.py` (lines 135–240)**:
   - CLI parser handles `--db` (default `axiom.db`) and `--compare-previous` (`action="store_true"`).
   - `init_db(db_path)` sets up SQLite tables `eval_runs` (`run_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, composite_score REAL NOT NULL, json_data TEXT NOT NULL`) and `eval_readiness` (`run_id TEXT NOT NULL, problem_id TEXT NOT NULL, score REAL NOT NULL, json_data TEXT NOT NULL, PRIMARY KEY (run_id, problem_id)`).
   - Exit code logic: if `args.compare_previous` and `report.regression_detected` (any dimension drop > 5%), prints failure message and exits with code 1 (`sys.exit(1)`). Otherwise exits 0 (`sys.exit(0)`).
3. **`axiom/evaluation/reporting/delta_report.py` (lines 46–105, 148–153)**:
   - Implements display name mapping (`knowledge_quality` → `Knowledge Understanding`), problem short names (`riemann_hypothesis` → `Riemann`), Unicode U+2192 arrow (`→`), signed integer percentages (`+12%`, `+0%`, `-5%`).
   - Checks regression threshold `diff < -0.05` (`regression_threshold = 0.05`).
4. **`axiom/services/api_gateway/routes/eval_api.py` (lines 81–125, 124–246)**:
   - Endpoint `/eval/scores`: `GET` returning latest 8 capability dimension scores.
   - Endpoint `/eval/run`: `POST` running benchmarks synchronously, saving to SQLite, returning `BenchmarkRunResponse`.
   - Endpoint `/eval/history`: `GET` returning last 10 run summaries (`SELECT run_id, timestamp, composite_score FROM eval_runs ORDER BY timestamp DESC LIMIT 10`).
   - Endpoint `/eval/prize-readiness`: `GET` returning ranked readiness scores for 6 Millennium Problems.
5. **`docs/audit/EPIC_002_audit.md` (lines 19–60)**:
   - Authored by Department J (Chief Skeptic) & Department I (Independent Audit).
   - Identifies 5 key findings: (1) Optimistic assumptions on unevidenced dimensions (CE, LS, RD marked `estimated`), (2) Lack of live Lean 4 compiler grounding (simulation fallback caps PV at < L3), (3) Static benchmark gaming vulnerability, (4) Synthetic empty DB baseline drift, (5) Riemann Hypothesis prize readiness score marked **DISPUTED**.

---

## 2. Logic Chain

1. **R4 Delta Report Format Verification**:
   - Compate `ORIGINAL_REQUEST.md` (lines 185-226) with `delta_report.py` output logic.
   - The string generator `to_markdown()` formats exact headings (`EPIC-002 COMPLETE`, `Capability Delta`, `Prize Readiness`, `Weakest Capability`, `Highest Priority`, `Recommended Next Epic`), signed percentages (`+X%`), problem short names, rightward arrow `→`, and line breaks.

2. **R5 CLI Runner & SQLite Schema Verification**:
   - `run_benchmarks.py` uses `argparse` with `--db` and `--compare-previous`.
   - SQLite tables `eval_runs` and `eval_readiness` form the storage schema.
   - Exit code check: `report.regression_detected` is set to `True` when any dimension drops by > 5% (`diff < -0.05`). When `--compare-previous` is present and regression is detected, `sys.exit(1)` triggers; otherwise `sys.exit(0)`.

3. **R5 REST API Route Verification**:
   - `eval_api.py` mounts 4 routes under `/eval`: `GET /scores`, `POST /run`, `GET /history`, `GET /prize-readiness`.
   - Direct integration in `main.py` via `app.include_router(eval_router)`.

4. **R6 Audit Layer Verification**:
   - Document `docs/audit/EPIC_002_audit.md` details 5 actionable findings.
   - Dept J holds veto authority over unevidenced scores and mandates `estimated: true` flags and compiler verification requirements.

---

## 3. Caveats

- **Sandbox Binary Availability**: Current environment lacks installed Lean 4 (`/usr/local/bin/lean` or `lean` binary), forcing reliance on structural simulation functions during benchmark runs. Audit layer explicitly highlights this as a critical limitation.
- **Estimated Baselines**: Dimensions 5 (CE), 7 (LS), 8 (RD) use constant baselines until underlying subsystem tools are fully integrated into benchmark suite callers.

---

## 4. Conclusion

The specification mining for SCEP (EPIC-002) is complete. All explicit and implicit requirements across R4 (Capability Delta Report text format), R5 (CLI runner, exit codes, SQLite schema, REST API endpoints), and R6 (Independent Audit layer directives) have been thoroughly documented in `analysis.md`.

---

## 5. Verification Method

To verify these mined specifications independently:

1. **Verify CLI Runner & Exit Codes**:
   ```bash
   python axiom/evaluation/run_benchmarks.py --db axiom.db
   echo "Exit code: $?" # Expect 0
   
   python axiom/evaluation/run_benchmarks.py --db axiom.db --compare-previous
   echo "Exit code: $?" # Expect 0 if no regression
   ```
2. **Verify Output Documents**:
   - Check created report at `docs/capability_delta_*.md` against text format rules.
   - Check created JSON at `benchmark_results.json`.
   - Check database tables `eval_runs` and `eval_readiness` in `axiom.db`.
3. **Verify REST API Routes**:
   - Inspect `axiom/services/api_gateway/routes/eval_api.py` for route declarations: `/eval/scores`, `/eval/run`, `/eval/history`, `/eval/prize-readiness`.
4. **Verify Audit Document**:
   - Inspect `docs/audit/EPIC_002_audit.md` for Dept I & Dept J findings.
