# AXIOM EPIC-002: Scientific Capability Evaluation Platform (SCEP) — Survey Analysis Part 2 (R3, R4, R5)

**Author:** Explorer 2 (`explorer_scep_survey_2`)  
**Date:** 2026-08-06  
**Target Subsystems:**
- `axiom/evaluation/prize_readiness.py` (Legacy Scorer)
- `axiom/evaluation/frameworks/prize_readiness.py` (Prize Readiness Engine)
- `axiom/evaluation/frameworks/capability.py` (Capability Taxonomy & Snapshots)
- `axiom/evaluation/benchmarks/suite.py` (Runnable Benchmark Suites)
- `axiom/evaluation/reporting/delta_report.py` (Delta Report Generator)
- `axiom/evaluation/run_benchmarks.py` (CLI Benchmark Runner)
- `axiom/services/api_gateway/routes/eval_api.py` & `main.py` (Evaluation REST Endpoints)

---

## 1. Executive Summary

This survey evaluates the existing implementation of Requirements R3 (Prize Readiness Engine), R4 (Capability Delta Report Generator), and R5 (Evaluation API & CLI Runner) against the specifications in `ORIGINAL_REQUEST.md` (EPIC-002: SCEP).

### Key Findings Summary
1. **R3 (Prize Readiness Engine):** **PARTIALLY COMPLIANT**
   - A modern `PrizeReadinessEngine` exists in `axiom/evaluation/frameworks/prize_readiness.py` covering all 6 Clay Millennium Problems with prerequisite capability maps, milestones, capability gaps, and confidence intervals.
   - **Gaps:** Legacy scorer in `axiom/evaluation/prize_readiness.py` still exists with 7 problems (includes Poincaré Conjecture reference) creating code duplication and confusion. All 6 problems currently default to `estimated=True` due to missing real Lean 4 compiler feedback. `GET /eval/prize-readiness` computes readiness dynamically on-the-fly from dimension scores rather than reading stored database records from `eval_readiness`.
2. **R4 (Capability Delta Report Generator):** **PARTIALLY COMPLIANT**
   - `axiom/evaluation/reporting/delta_report.py` accurately generates JSON and Markdown delta reports. The Markdown format matches the exact specification requested in `ORIGINAL_REQUEST.md` (showing per-dimension `%` change, prize readiness integer point deltas `31 → 34`, weakest capability, highest priority engineering task, and recommended next epic `EPIC-003`).
   - **Gaps:** File naming produces `docs/capability_delta_{run_id}.md` (where `run_id` is an 8-char UUID prefix like `docs/capability_delta_15efc092.md`) instead of using a UTC timestamp (e.g. `docs/capability_delta_TIMESTAMP.md`). When no previous run exists, synthetic fake deltas (e.g., `+8%`) are invented instead of handling baseline mode explicitly.
3. **R5 (Evaluation API & CLI Runner):** **PARTIALLY COMPLIANT**
   - CLI runner `axiom/evaluation/run_benchmarks.py` and REST router `axiom/services/api_gateway/routes/eval_api.py` (`/eval/scores`, `/eval/prize-readiness`, `/eval/history`, `/eval/run`) are fully implemented and functional. CLI completes in < 1 second. Exit code logic returns `1` when `--compare-previous` is passed and a regression (>5% drop) occurs.
   - **Gaps:** SQLite table schema discrepancy: Requirement R5 explicitly mandates storing results in an `eval_results` table, but the codebase implements `eval_runs` and `eval_readiness`, missing the `eval_results` table name and individual test case result table. 3 out of 8 capability dimensions (`counterexample_search`, `literature_synthesis`, `research_productivity`) have hardcoded scores (`0.35`, `0.40`, `0.50`) in `run_benchmarks.py` and `eval_api.py` instead of executing runnable benchmark suites.

---

## 2. Requirement 3: Prize Readiness Engine

### 2.1 Specification Requirements
- **Target Domain:** All 6 Clay Millennium Prize Problems (Riemann Hypothesis, P vs NP, Yang-Mills Existence & Mass Gap, Birch and Swinnerton-Dyer Conjecture, Navier-Stokes Existence & Smoothness, Hodge Conjecture).
- **Readiness Model Requirements:**
  - Prerequisite capability map (weighted contribution of required dimensions & levels).
  - Measurable milestones (achieved & remaining).
  - Current evidence-based score in $[0.0, 1.0]$. Scores must be **grounded in benchmark results**, never estimated without evidence.
  - Confidence interval $(L_{lower}, L_{upper})$.
  - Identified capability gaps.
- **Persistence & API:**
  - Persisted in SQLite database table `eval_readiness`.
  - Exposed via REST endpoint `GET /eval/prize-readiness`.

### 2.2 Existing Codebase Implementation Audit

#### File Analysis: `axiom/evaluation/prize_readiness.py` (Legacy Scorer)
- **Line 22–30:** Defines `CapabilityScore` struct with 5 legacy dimensions (`knowledge`, `reasoning`, `verification`, `hypothesis_gen`, `literature_coverage`).
- **Line 66–196:** Defines `PRIZE_PROBLEMS` list containing **7 problems** (the 6 Millennium Problems plus `"Poincaré Conjecture (Reference — Solved 2003)"`).
- **Line 201–309:** `PrizeReadinessScorer` computes aggregate score via geometric mean across dimensions. Dynamically adjusts scores if `EpistemicStore` graph nodes are provided, scanning nodes for keywords (e.g. `complexity`, `zeta`).
- **Issues:** This legacy file does not generate `confidence_interval` or `prerequisite` DAGs, conflicts with 6-problem scope, and does not match the 8-dimension capability framework.

#### File Analysis: `axiom/evaluation/frameworks/prize_readiness.py` (New Engine)
- **Line 13–22:** `CapabilityPrerequisite` dataclass containing `capability`, `dimension`, `required_level` ($L0\text{--}L5$), `current_level`, `weight`, `evidence`, and `gap_description`.
- **Line 25–61:** `PrizeReadinessScore` dataclass containing:
  - `problem_id`, `problem_name`, `domain`
  - `score`: float $[0, 1]$
  - `confidence_interval`: tuple `(float, float)`
  - `prerequisites`: `list[CapabilityPrerequisite]`
  - `milestones_achieved`: `list[str]`
  - `capability_gaps`: `list[str]`
  - `estimated`: `bool`
  - `evidence_sources`: `list[str]`
  - `to_dict()` serialization method.
- **Line 67–316:** Builders for all 6 Millennium Problems (`_make_riemann_readiness`, `_make_pvsnp_readiness`, `_make_yang_mills_readiness`, `_make_bsd_readiness`, `_make_navier_stokes_readiness`, `_make_hodge_readiness`).
- **Line 318–352:** `PrizeReadinessEngine.compute_all(benchmark_scores)` maps dimension scores into problem readiness scores using weighted mathematical formulas (e.g., $0.35 \times \text{MR} + 0.30 \times \text{PV} + 0.20 \times \text{LS} + 0.15 \times \text{CE}$ for Riemann).

#### File Analysis: `axiom/services/api_gateway/routes/eval_api.py`
- **Line 88–100:** Endpoint `GET /eval/prize-readiness`:
  ```python
  @router.get("/prize-readiness")
  def get_prize_readiness():
      data = _get_current_scores(settings.db_path)
      scores_map = {d_name: info.get("score", 0.0) for d_name, info in data.get("dimensions", {}).items()}
      engine = PrizeReadinessEngine()
      readiness_list = engine.compute_all(scores_map)
      return engine.to_ranked_list(readiness_list)
  ```

### 2.3 Gaps & Non-Compliance Items (R3)
1. **Hardcoded `estimated=True` Flag:** In `frameworks/prize_readiness.py`, lines 84, 143, 188, 219, 252, 286 hardcode `estimated=True` for all 6 problem builders. The audit specification R6 flags any prize readiness score computed with `estimated=True`.
2. **Confidence Intervals are Heuristic:** Confidence intervals are calculated via fixed multipliers (e.g. `(round(score * 0.85, 4), round(min(1.0, score * 1.15), 4))`) rather than statistical standard deviation/error bounds from benchmark runs.
3. **Database Query Bypassed in REST Endpoint:** `GET /eval/prize-readiness` recalculates readiness from dimension scores instead of reading stored records directly from `eval_readiness` table where past runs are persisted.
4. **Codebase Duplication:** `axiom/evaluation/prize_readiness.py` (legacy 7-problem scorer) coexists with `axiom/evaluation/frameworks/prize_readiness.py` (6-problem engine), causing confusion for consumer modules.

---

## 3. Requirement 4: Capability Delta Report Generator

### 3.1 Specification Requirements
- **Functionality:** Compares two benchmark snapshots (before/after a sprint) and generates structured comparison reports.
- **Output Content:**
  1. Per-dimension score changes in percentage (`+12%`, `-5%`).
  2. Prize readiness delta expressed as integer 0–100 points (`31 → 34`).
  3. Regression flags when any dimension drops $> 5\%$.
  4. Identification of weakest capability.
  5. Recommended next Epic (`EPIC-003`).
- **Formats:** Both JSON (`benchmark_results.json`) and Markdown saved to `docs/capability_delta_TIMESTAMP.md`.
- **Strict Format Spec:** Must adhere to the exact format given in `ORIGINAL_REQUEST.md` (lines 187–226).

### 3.2 Existing Codebase Implementation Audit

#### File Analysis: `axiom/evaluation/reporting/delta_report.py`
- **Line 17–44:** `CapabilityDeltaReport` dataclass storing `epic_name`, `previous_run_id`, `current_run_id`, `timestamp`, `dimension_deltas`, `readiness_deltas`, `weakest_capability`, `highest_priority`, `recommended_next_epic`, `regression_detected`, `regression_details`.
- **Line 46–105:** `to_markdown()` formats output into the exact specification:
  - Header: `{self.epic_name} COMPLETE\n\nCapability Delta`
  - Display Name Mapping (lines 54–63): Maps internal keys like `knowledge_quality` to `"Knowledge Understanding"`.
  - Percentage Deltas: Adds explicit `+` or `-` sign to percentage changes (e.g. `+12%`).
  - Prize Readiness: Maps short names (`riemann_hypothesis` $\to$ `"Riemann"`) and formats points as `{prev_pts} → {curr_pts}`.
  - Sections: `"Weakest Capability"`, `"Highest Priority"`, `"Recommended Next Epic"`.
  - Regression Section: Appends `⚠️ REGRESSIONS DETECTED:` list if `regression_detected` is `True`.
- **Line 108–196:** `generate_delta_report()`:
  - Compares `prev_snapshot` vs `curr_snapshot`.
  - Computes `diff = curr_val - prev_val` and `pct_change = int(round(diff * 100))`.
  - Detects regression if `diff < -0.05`.
  - Converts float readiness scores $[0.0, 1.0]$ to integer points $[0, 100]$: `int(round(curr_val * 100))`.
  - Maps `weakest_capability` to `highest_priority` using `priority_map` (lines 159–168).

#### Output Verification via Real Execution (`python3 axiom/evaluation/run_benchmarks.py`):
```text
EPIC-002 COMPLETE

Capability Delta

Mathematical Reasoning
+0%

Proof Verification
+0%

Conjecture Generation
+0%

Knowledge Understanding
+0%

Counterexample Search
+0%

Research Planning
+0%

Literature Synthesis
+0%

Research Productivity
+0%

Prize Readiness

Riemann
78 → 78

P vs NP
100 → 100

Yang–Mills
45 → 45

Birch–Swinnerton-Dyer
40 → 40

Navier–Stokes
50 → 50

Hodge Conjecture
40 → 40

Weakest Capability
Counterexample Search

Highest Priority
Scale SMT Parameter Sweep & Z3 Axiom Integration

Recommended Next Epic
EPIC-003
```

### 3.3 Gaps & Non-Compliance Items (R4)
1. **File Naming Mismatch:** Requirement R4 states the report must be written to `docs/capability_delta_TIMESTAMP.md` (e.g., `docs/capability_delta_20260806T112458Z.md`). `run_benchmarks.py` (line 218) writes to `docs/capability_delta_{run_id}.md` (e.g. `docs/capability_delta_15efc092.md`).
2. **Synthetic Baseline Invention:** When no `prev_snapshot` exists in the database, `generate_delta_report()` invents synthetic prior values (`curr_val - 0.08` and `curr_pts - 2`) in baseline mode (lines 133, 186) rather than explicitly reporting baseline status or `0%` change.

---

## 4. Requirement 5: Evaluation API & CLI Runner

### 4.1 Specification Requirements
- **CLI Runner:** `axiom/evaluation/run_benchmarks.py`
  - Runs all benchmarks against live system (< 2 minutes runtime).
  - Stores results in SQLite database table `eval_results`.
  - `--compare-previous` flag to compare with prior run.
  - Exits with code `0` (no regression) or code `1` (regression detected).
- **REST API Endpoints:** `/eval/*` in FastAPI gateway (`axiom/services/api_gateway/routes/eval_api.py`)
  - `GET /eval/scores`: current capability scores for all 8 dimensions.
  - `POST /eval/run`: triggers benchmark run and returns results.
  - `GET /eval/history`: returns last 10 benchmark run summaries.
  - `GET /eval/prize-readiness`: returns prize readiness for all 6 problems.

### 4.2 Existing Codebase Implementation Audit

#### File Analysis: `axiom/evaluation/run_benchmarks.py`
- **Line 39–66:** `init_db(db_path)` creates two SQLite tables:
  ```sql
  CREATE TABLE IF NOT EXISTS eval_runs (
      run_id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL,
      composite_score REAL NOT NULL,
      json_data TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS eval_readiness (
      run_id TEXT NOT NULL,
      problem_id TEXT NOT NULL,
      score REAL NOT NULL,
      json_data TEXT NOT NULL,
      PRIMARY KEY (run_id, problem_id)
  );
  ```
- **Line 147–166:** Executes 5 benchmark suites from `axiom/evaluation/benchmarks/suite.py`:
  1. `run_math_reasoning_benchmarks()` (10 test cases)
  2. `run_proof_verification_benchmarks()` (7 test cases)
  3. `run_conjecture_benchmarks()` (5 test cases)
  4. `run_knowledge_quality_benchmarks()` (5 test cases)
  5. `run_research_planning_benchmarks()` (5 test cases)
- **Line 169–171:** **Hardcoded Dimensions:**
  ```python
  ce_score = 0.35  # Counterexample: basic SMT sweep
  ls_score = 0.40  # Literature: arXiv parsing
  rd_score = 0.50  # Productivity: autonomous loop iterations
  ```
- **Line 229–233:** Exit Code Logic:
  ```python
  if args.compare_previous and report.regression_detected:
      print("\n❌ REGRESSION CHECK FAILED! One or more capabilities dropped significantly.")
      for reg in report.regression_details:
          print(f"  - {reg}")
      sys.exit(1)

  print("\n🎉 Evaluation run completed successfully.")
  sys.exit(0)
  ```

#### File Analysis: `axiom/services/api_gateway/routes/eval_api.py`
- **Prefix:** `/eval`
- **Endpoints:**
  - `GET /eval/scores` (lines 81–85): Returns dict of 8 capability dimensions.
  - `GET /eval/prize-readiness` (lines 88–100): Returns ranked list of 6 prize readiness scores.
  - `GET /eval/history` (lines 103–122): Returns list of up to 10 past runs (`run_id`, `timestamp`, `composite_score`).
  - `POST /eval/run` (lines 124–246): Synchronously executes benchmarks, calculates snapshot & prize readiness, stores to DB, generates delta report, writes markdown file, and returns `BenchmarkRunResponse`.

### 4.3 Gaps & Non-Compliance Items (R5)
1. **Missing `eval_results` Database Table:** Requirement R5 explicitly specifies that results must be stored in an `eval_results` SQLite table. The code uses `eval_runs` and `eval_readiness`, leaving `eval_results` uncreated. Individual benchmark case outputs (e.g. per-case pass/fail) are not persisted in DB tables.
2. **Unimplemented / Hardcoded Benchmark Suites:** 3 out of the 8 capability dimensions in `run_benchmarks.py` and `eval_api.py` (`counterexample_search`, `literature_synthesis`, `research_productivity`) are hardcoded constants (`0.35`, `0.40`, `0.50`) instead of being computed from executable test cases in `benchmarks/suite.py`.
3. **Table Creation Duplication in API:** `eval_api.py` duplicates SQLite table creation SQL inline inside `trigger_benchmark()` (lines 186–202) instead of reusing `init_db()` from `run_benchmarks.py`.
4. **Database Location Mismatch Risk:** `run_benchmarks.py` defaults to `--db axiom.db` in current working directory, whereas `eval_api.py` uses `settings.db_path`. If `settings.db_path` differs from `axiom.db`, CLI and API read/write different SQLite files.

---

## 5. Comparative Requirement vs Implementation Matrix

| Req | Requirement Description | Implementation Location | Compliance Status | Specific Gaps / Discrepancies |
|---|---|---|---|---|
| **R3** | 6 Clay Millennium Problems scored readiness model | `axiom/evaluation/frameworks/prize_readiness.py` | **Partial** | Legacy `prize_readiness.py` has 7 problems including Poincaré. Duplicate models exist. |
| **R3** | Grounded in benchmark results, no estimation | `frameworks/prize_readiness.py`:84,143,188... | **Partial** | All 6 problems hardcode `estimated=True`. Scores are computed from weighted formulas of dimensions, 3 of which are hardcoded. |
| **R3** | Prerequisite map & Milestones & Gaps | `frameworks/prize_readiness.py`:13-60 | **Compliant** | `CapabilityPrerequisite` and problem builders define prerequisites, achieved milestones, and capability gaps. |
| **R3** | Confidence Intervals | `frameworks/prize_readiness.py`:76,135,180... | **Partial** | Multiplier-based heuristic `(score*0.85, score*1.15)` rather than statistical confidence. |
| **R3** | Stored in DB & REST `GET /eval/prize-readiness` | `eval_api.py`:88-100, `run_benchmarks.py`:121 | **Partial** | REST endpoint recomputes dynamically from dimension scores instead of querying `eval_readiness` table directly. |
| **R4** | Capability Delta Report (JSON & Markdown) | `axiom/evaluation/reporting/delta_report.py` | **Compliant** | `generate_delta_report()` produces both JSON dict and formatted Markdown string. |
| **R4** | % change per dimension & Prize delta (`31 → 34`) | `delta_report.py`:65-89, 137-193 | **Compliant** | Display names, percentage signs, and integer point conversions match requirements. |
| **R4** | Weakest capability & Recommended next epic | `delta_report.py`:91-98, 159-171 | **Compliant** | Correctly identifies lowest dimension and maps to priority & `EPIC-003`. |
| **R4** | Saved to `docs/capability_delta_TIMESTAMP.md` | `run_benchmarks.py`:218, `eval_api.py`:230 | **Partial** | Saved as `docs/capability_delta_{run_id}.md` (using 8-char UUID) instead of UTC timestamp format. |
| **R4** | Baseline mode behavior | `delta_report.py`:133, 186 | **Partial** | Synthetic values (`curr_val - 0.08`, `curr_pts - 2`) are invented when no previous run exists. |
| **R5** | CLI runner (`run_benchmarks.py`) < 2 mins | `axiom/evaluation/run_benchmarks.py` | **Compliant** | Executed in < 1 second on test runs. |
| **R5** | `--compare-previous` flag & exit codes (0 vs 1) | `run_benchmarks.py`:138, 229-233 | **Compliant** | Exits 1 if `--compare-previous` passed and regression > 5% detected, else 0. |
| **R5** | SQLite `eval_results` table schema | `run_benchmarks.py`:46-62 | **Non-Compliant** | Missing `eval_results` table. Implemented as `eval_runs` and `eval_readiness`. |
| **R5** | REST API endpoints (`/eval/*`) | `axiom/services/api_gateway/routes/eval_api.py` | **Compliant** | `/eval/scores`, `/eval/prize-readiness`, `/eval/history`, `/eval/run` all implemented and mounted. |
| **R5** | Full 8-dimension benchmark execution | `axiom/evaluation/benchmarks/suite.py` | **Partial** | 5 suites implemented. 3 dimensions (`counterexample_search`, `literature_synthesis`, `research_productivity`) use hardcoded floats. |

---

## 6. Actionable Remediation Plan for Implementers

To bring R3, R4, and R5 into 100% compliance with EPIC-002 requirements, implementers should perform the following targeted fixes:

1. **Database Schema Standardisation (R5):**
   - Add `eval_results` table in `init_db()` (and `eval_api.py`):
     ```sql
     CREATE TABLE IF NOT EXISTS eval_results (
         run_id TEXT NOT NULL,
         case_id TEXT NOT NULL,
         dimension TEXT NOT NULL,
         score REAL NOT NULL,
         passed BOOLEAN NOT NULL,
         time_ms REAL NOT NULL,
         PRIMARY KEY (run_id, case_id)
     );
     ```
   - Persist individual `BenchmarkResult` items from the benchmark suites into `eval_results`.

2. **Complete the 3 Missing Benchmark Suites (R5):**
   - In `axiom/evaluation/benchmarks/suite.py`, implement:
     - `run_counterexample_benchmarks()` (testing SMT Z3 sweep & modular counterexamples).
     - `run_literature_synthesis_benchmarks()` (testing arXiv parser node extraction).
     - `run_research_productivity_benchmarks()` (testing MCTS iterations per second).
   - Replace hardcoded floats (`0.35`, `0.40`, `0.50`) in `run_benchmarks.py` and `eval_api.py` with calls to these new benchmark runners.

3. **Report File Naming & Baseline Mode (R4):**
   - In `run_benchmarks.py` and `eval_api.py`, change output filename format from `docs/capability_delta_{run_id}.md` to `docs/capability_delta_{timestamp_slug}.md` (e.g., `docs/capability_delta_20260806_112458.md`).
   - In `delta_report.py`, when `prev_snapshot` is `None`, set `prev_val = curr_val` (0% change) or explicitly label as `BASELINE` instead of synthesizing fake `-0.08` differences.

4. **Prize Readiness Endpoint & Legacy Scorer Clean-up (R3):**
   - Update `GET /eval/prize-readiness` in `eval_api.py` to query `eval_readiness` table for the latest run ID first.
   - Deprecate or remove `axiom/evaluation/prize_readiness.py` (legacy 7-problem scorer) to avoid confusion with `axiom/evaluation/frameworks/prize_readiness.py`.
