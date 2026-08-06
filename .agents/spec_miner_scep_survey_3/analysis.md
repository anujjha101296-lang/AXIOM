# Specification Analysis: EPIC-002 Scientific Capability Evaluation Platform (SCEP)

> **Agent**: Spec Miner 3 (`spec_miner_scep_survey_3`)  
> **Target Subsystem**: SCEP — Scientific Capability Evaluation Platform  
> **Source Documents**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/ORIGINAL_REQUEST.md`, `EPIC_002_SPEC.md`, `docs/scientific_capability_framework.md`, `docs/audit/EPIC_002_audit.md`, `axiom/evaluation/*`, `axiom/services/api_gateway/routes/eval_api.py`

---

## Executive Summary

The **Scientific Capability Evaluation Platform (SCEP)** forms the foundational evaluation harness for AXIOM Labs, establishing an objective, multi-dimensional capability measurement system inspired by AlphaFold's evaluation-first philosophy. This specification document encapsulates all explicit and implicit requirements for SCEP across four primary domains:
1. **R4 Capability Delta Report Exact Text & Structure Specifications**
2. **R5 CLI Runner (`run_benchmarks.py`) Command Line Interface, Exit Codes, and SQLite Database Schema**
3. **R5 REST API Endpoints (`/eval/*`)**
4. **R6 Independent Audit Layer Specifications (`docs/audit/EPIC_002_audit.md`)**

---

## 1. R4 Capability Delta Report Exact Text Format

### 1.1 Overview & Text Structure
The Capability Delta Report measures capability growth across benchmark runs rather than code line count. Every Epic completion must generate a structured report adhering to the exact text format specified in `ORIGINAL_REQUEST.md`.

### 1.2 Exact Formatting Specification
The report uses a strict line-by-line block structure with blank line separators (`\n\n`) between major sections and items.

```markdown
EPIC-002 COMPLETE

Capability Delta

<Dimension 1 Name>
<Signed Delta %>

<Dimension 2 Name>
<Signed Delta %>

...

Prize Readiness

<Problem 1 Short Name>
<Prev Points> → <Curr Points>

<Problem 2 Short Name>
<Prev Points> → <Curr Points>

...

Weakest Capability
<Weakest Capability Display Name>

Highest Priority
<Engineering Action Priority Statement>

Recommended Next Epic
<Next Epic ID>
```

### 1.3 Detailed Text Element Specifications

| Component | Format Rule | Example / Specification |
|-----------|-------------|-------------------------|
| **Epic Header** | `<EPIC_ID> COMPLETE\n\n` | `EPIC-002 COMPLETE` |
| **Section 1 Header** | `Capability Delta\n\n` | `Capability Delta` |
| **Dimension Name** | Enum key mapped to official display name | See mapping table below |
| **Dimension % Delta** | Explicit sign (`+` or `-`), integer rounded % change | `+12%`, `+0%`, `-5%` |
| **Section 2 Header** | `Prize Readiness\n\n` | `Prize Readiness` |
| **Problem Short Name** | Problem ID mapped to short display name | See mapping table below |
| **Readiness Points Delta**| `<prev_pts> → <curr_pts>\n\n` using Unicode U+2192 `→` | `31 → 34`, `76 → 78` |
| **Section 3 Header** | `Weakest Capability\n<Capability Name>\n\n` | `Weakest Capability\nAutomated Lemma Discovery` |
| **Section 4 Header** | `Highest Priority\n<Action Statement>\n\n` | `Highest Priority\nBuild Formal Proof & Lemma Discovery Platform` |
| **Section 5 Header** | `Recommended Next Epic\n<Epic ID>` | `Recommended Next Epic\nEPIC-003` |

### 1.4 Mapping Tables

#### Capability Dimension Display Names
| Internal Dimension Key (`CapabilityDimension`) | Report Display Name |
|-----------------------------------------------|---------------------|
| `mathematical_reasoning` | `Mathematical Reasoning` |
| `proof_verification` | `Proof Verification` |
| `conjecture_generation` | `Conjecture Generation` |
| `knowledge_quality` | `Knowledge Understanding` |
| `counterexample_search` | `Counterexample Search` |
| `research_planning` | `Research Planning` |
| `literature_synthesis` | `Literature Synthesis` |
| `research_productivity` | `Research Productivity` |

#### Prize Problem Short Display Names
| Internal Problem ID | Report Short Display Name |
|---------------------|---------------------------|
| `riemann_hypothesis` | `Riemann` |
| `p_vs_np` | `P vs NP` |
| `navier_stokes` | `Navier-Stokes` / `Navier–Stokes` |
| `birch_swinnerton_dyer` | `Birch–Swinnerton-Dyer` |
| `yang_mills` | `Yang–Mills` |
| `hodge_conjecture` | `Hodge Conjecture` |

### 1.5 Weakest Capability to Priority Mapping
When a capability dimension is identified as the weakest ($S_{min}$), SCEP maps it to an explicit engineering priority:

| Weakest Capability | Highest Priority Action Statement |
|--------------------|-----------------------------------|
| `Proof Verification` / `Automated Lemma Discovery` | `Build Formal Proof & Lemma Discovery Platform` |
| `Conjecture Generation` | `Enhance MCTS Exploration & Novelty Search Engine` |
| `Counterexample Search` | `Scale SMT Parameter Sweep & Z3 Axiom Integration` |
| `Literature Synthesis` | `Expand arXiv Batch Parser & Reference Graph Builder` |
| `Research Planning` | `Refine Millennium Decomposition DAGs & P(L) Heuristics` |
| `Knowledge Quality` | `Enforce Strict Ontological Domain Classifications` |
| `Mathematical Reasoning` | `Integrate Exact SymPy Arbitrary-Precision Solver` |
| `Research Productivity` | `Implement Fully Autonomous Discovery Cycles` |

### 1.6 Output Persistence Targets
- **Human-Readable Markdown**: Saved to `docs/capability_delta_<run_id>.md` (e.g. `docs/capability_delta_3d8be7ce.md`).
- **Machine-Readable JSON**: Saved to `benchmark_results.json` at root directory.
- **SQLite Storage**: Stored inside `eval_runs` (`json_data` column).

---

## 2. R5 CLI Runner (`run_benchmarks.py`), Exit Code Rules, and SQLite Schema

### 2.1 CLI Invocation & Argument Parsing
The CLI benchmark runner is executed via:
```bash
python -m axiom.evaluation.run_benchmarks [--db DB_PATH] [--compare-previous]
# OR
python axiom/evaluation/run_benchmarks.py [--db DB_PATH] [--compare-previous]
```

#### Command Line Arguments
- `--db PATH`: Path to SQLite database (type: `str`, default: `axiom.db`).
- `--compare-previous`: Flag to perform regression checking against the prior database snapshot (type: `bool`, `action="store_true"`).

### 2.2 Execution Pipeline & Rules
1. **Database Initialization**: Calls `init_db(db_path)` to ensure required tables (`eval_runs`, `eval_readiness`) exist.
2. **Benchmark Execution**: Executes all 5 runnable benchmark suites in < 2 minutes total:
   - `run_math_reasoning_benchmarks()` (10 test cases)
   - `run_proof_verification_benchmarks()` (7 test cases)
   - `run_conjecture_benchmarks(db_path)` (5 test cases)
   - `run_knowledge_quality_benchmarks(db_path)` (5 test cases)
   - `run_research_planning_benchmarks()` (5 test cases)
   - Evaluates estimated baselines for Counterexample Search (0.35), Literature Synthesis (0.40), Research Productivity (0.50).
3. **Snapshot Construction**: Computes composite score $S_{composite} = \sum_{d=1}^{8} w_d \cdot S_d$ using weights:
   - MR: 0.20, PV: 0.18, CG: 0.15, KQ: 0.12, CE: 0.12, RP: 0.10, LS: 0.08, RD: 0.05.
4. **Prize Readiness Calculation**: Runs `PrizeReadinessEngine().compute_all(scores_map)` for all 6 Millennium Problems.
5. **Database Storage**: Persists the run snapshot to `eval_runs` and readiness records to `eval_readiness`.
6. **Delta Report Generation**: Compares current run with previous run (`get_latest_run`).
7. **Regression Guard**: Evaluates exit code condition.

### 2.3 Exit Code Specification

$$\text{Exit Code} = \begin{cases} 
1 & \text{if } \text{--compare-previous is set AND } \exists d : \Delta S_d < -0.05 \text{ (drop > 5\%)} \\
0 & \text{otherwise (pass / no regression / flag omitted)}
\end{cases}$$

- **Exit Code 0**: Evaluation completed successfully with no capability regression exceeding 5% (or when `--compare-previous` is omitted).
- **Exit Code 1**: `--compare-previous` flag is active AND at least one capability dimension experienced a score regression > 5% ($S_{curr} - S_{prev} < -0.05$).
  - **Stdout Error Output on Exit 1**:
    ```
    ❌ REGRESSION CHECK FAILED! One or more capabilities dropped significantly.
      - <dimension_key> dropped by <pct>% (<prev_score> → <curr_score>)
    ```

### 2.4 SQLite Database Schema (`eval_results` / Evaluation Schema)
The evaluation platform persists benchmark snapshots and prize readiness evaluations in SQLite (`axiom.db`).

```sql
-- Table 1: Benchmark Run Snapshots
CREATE TABLE IF NOT EXISTS eval_runs (
    run_id TEXT PRIMARY KEY,          -- 8-character UUID slice or custom run ID
    timestamp TEXT NOT NULL,          -- ISO 8601 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)
    composite_score REAL NOT NULL,    -- Weighted composite score in [0.0, 1.0]
    json_data TEXT NOT NULL           -- Full serialized CapabilitySnapshot JSON object
);

-- Table 2: Prize Readiness Evaluation Records
CREATE TABLE IF NOT EXISTS eval_readiness (
    run_id TEXT NOT NULL,             -- Foreign key referencing eval_runs(run_id)
    problem_id TEXT NOT NULL,         -- Millennium problem identifier (e.g. riemann_hypothesis)
    score REAL NOT NULL,              -- Evidence-based readiness score in [0.0, 1.0]
    json_data TEXT NOT NULL,          -- Serialized PrizeReadinessScore JSON object
    PRIMARY KEY (run_id, problem_id)  -- Compound primary key
);
```

---

## 3. R5 REST API Endpoints Specification

The REST API is implemented using FastAPI in `axiom/services/api_gateway/routes/eval_api.py` and included in the main FastAPI application (`axiom/services/api_gateway/main.py`) under prefix `/eval`.

### 3.1 Endpoint Summary Table
| Method | Endpoint | Description | Response Model / Structure |
|--------|----------|-------------|----------------------------|
| `GET` | `/eval/scores` | Fetch current 8-dimension capability scores | JSON object mapping dimension key to score metadata |
| `POST` | `/eval/run` | Trigger synchronous benchmark run & delta report | `BenchmarkRunResponse` JSON |
| `GET` | `/eval/history` | Retrieve last 10 benchmark run summaries | JSON list of `{run_id, timestamp, composite_score}` |
| `GET` | `/eval/prize-readiness` | Retrieve structured readiness for 6 prize problems | JSON list of ranked `PrizeReadinessScore` objects |

### 3.2 Detailed Endpoint Specifications

#### 1. `GET /eval/scores`
- **Description**: Returns the latest capability scores across all 8 dimensions stored in SQLite `eval_runs`.
- **Query Strategy**: `SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1`. Falls back to baseline defaults if DB is uninitialized.
- **Sample Output JSON**:
```json
{
  "mathematical_reasoning": {
    "score": 0.90,
    "level": 5,
    "level_name": "L5: Research-Active",
    "confidence": 0.8,
    "benchmark_count": 10,
    "estimated": false,
    "weighted": 0.18
  },
  "proof_verification": {
    "score": 0.7143,
    "level": 3,
    "level_name": "L3: Graduate",
    "confidence": 0.8,
    "benchmark_count": 7,
    "estimated": false,
    "weighted": 0.1286
  },
  ...
}
```

#### 2. `POST /eval/run`
- **Description**: Synchronously executes all 5 runnable benchmark suites, calculates composite scores, updates SQLite database (`eval_runs` and `eval_readiness`), generates delta report vs. previous run, and writes `docs/capability_delta_<run_id>.md`.
- **Response Schema (`BenchmarkRunResponse`)**:
```json
{
  "run_id": "3d8be7ce",
  "timestamp": "2026-08-06T11:22:00Z",
  "composite_score": 0.5843,
  "dimensions": { ... },
  "readiness": [ ... ],
  "weakest_capability": "Counterexample Search",
  "highest_priority": "Scale SMT Parameter Sweep & Z3 Axiom Integration",
  "recommended_next_epic": "EPIC-003",
  "regression_detected": false
}
```

#### 3. `GET /eval/history`
- **Description**: Fetches up to 10 previous benchmark run summaries sorted by timestamp descending.
- **SQL Query**: `SELECT run_id, timestamp, composite_score FROM eval_runs ORDER BY timestamp DESC LIMIT 10`.
- **Sample Output JSON**:
```json
[
  {
    "run_id": "3d8be7ce",
    "timestamp": "2026-08-06T11:22:00Z",
    "composite_score": 0.5843
  },
  {
    "run_id": "a1b2c3d4",
    "timestamp": "2026-08-06T10:00:00Z",
    "composite_score": 0.5020
  }
]
```

#### 4. `GET /eval/prize-readiness`
- **Description**: Calculates evidence-based readiness scores for all 6 Clay Millennium Prize Problems using current capability scores.
- **Sample Output JSON**:
```json
[
  {
    "problem_id": "riemann_hypothesis",
    "problem_name": "Riemann Hypothesis",
    "domain": "number_theory",
    "score": 0.3805,
    "confidence_interval": [0.3234, 0.4376],
    "estimated": true,
    "prerequisites": [
      {
        "capability": "Analytic Number Theory — Zeta Function",
        "dimension": "mathematical_reasoning",
        "required_level": 5,
        "current_level": 5,
        "gap": 0,
        "evidence": "MR benchmark: 0.900"
      }
    ],
    "milestones_achieved": [
      "Mathematical ontology for number theory domain",
      "Functional equation structure decomposition tree"
    ],
    "capability_gaps": [
      "Analytic continuation formalization",
      "Zero-free region expansion automation"
    ],
    "evidence_sources": ["EPIC-001 MIP validation suite", "math_reasoning benchmark"]
  }
]
```

---

## 4. R6 Independent Audit Layer Specifications (`docs/audit/EPIC_002_audit.md`)

### 4.1 Audit Bodies & Scope
The audit layer is owned jointy by:
- **Department J (Chief Skeptic)**: Audits score optimism, benchmark gaming, and holds veto authority over ungrounded readiness claims.
- **Department I (Independent Audit)**: Audits compiler grounding, execution integrity, and baseline database consistency.
- **Audit Document Path**: `docs/audit/EPIC_002_audit.md`.

### 4.2 Key Findings & Directives

```
   ┌────────────────────────────────────────────────────────────────────────┐
   │                       CHIEF SKEPTIC DIRECTIVE                          │
   ├────────────────────────────────────────────────────────────────────────┤
   │ 1. All unevidenced capability scores MUST be marked estimated=true.   │
   │ 2. PV Level L3+ cannot be certified without live Lean 4 compilation.   │
   │ 3. Static test cases must be randomized to prevent gaming.            │
   │ 4. Riemann Hypothesis readiness is DISPUTED until zero tracking runs.  │
   │ 5. Dept J holds veto power on any readiness score > 0.5 without proof. │
   └────────────────────────────────────────────────────────────────────────┘
```

#### Detailed Findings & Directives Matrix

| # | Finding Name | Dept | Risk Level | Description | Audit Directive |
|---|--------------|------|------------|-------------|-----------------|
| 1 | **Optimistic Score Assumptions** | Dept J | **HIGH** | 3 of 8 capability dimensions (CE: 0.35, LS: 0.40, RD: 0.50) rely on hardcoded estimates rather than runnable benchmark suites. | Mark scores as `estimated: true`. Composite score calculation must flag lower confidence. |
| 2 | **Lack of Live Compiler Grounding** | Dept I | **CRITICAL** | Proof Verification benchmarks use fallback simulation (`_simulate_lean4_check`) instead of live Lean4/Coq/Isabelle binary subprocesses. | Level L3+ in Proof Verification **cannot be certified** without live compiler verification. |
| 3 | **Benchmark Gaming / Overfitting** | Dept J | **MEDIUM** | Mathematical Reasoning uses 10 static question IDs (`mr_001`–`mr_010`). Self-improvement loops could hardcode exact answers. | Future sprints MUST introduce randomized parameter seeding (e.g. dynamic quadratic coefficients). |
| 4 | **Empty Database Baseline Drift** | Dept I | **LOW** | Empty DB runs fallback to synthetic baseline score estimates, inflating initial growth. | Hardcode post-EPIC-001 snapshot in SQLite as the official immutable baseline. |
| 5 | **Prize Readiness Grounding** | Dept J & I | **HIGH** | Riemann Hypothesis score (0.3805) relies on unverified CE & LS estimates. | Mark Riemann Hypothesis score status as **DISPUTED**. Ground all 6 problem scores in concrete tests. |

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Delta Report | Markdown Format Generator | Generates exact text report matching `ORIGINAL_REQUEST.md` specification | Previous snapshot, Current snapshot, Readiness scores | Formatted Markdown text string | Fallback baseline estimates if previous snapshot is missing | `delta_report.py` & `ORIGINAL_REQUEST.md` |
| 2 | Delta Report | Dimension Display Mapping | Maps snake_case dimension keys to standardized human-readable display names | Dimension key string (e.g. `knowledge_quality`) | Standardized display string (`Knowledge Understanding`) | Returns title-cased string if key unmapped | `delta_report.py:54-63` |
| 3 | Delta Report | Readiness Short Name Mapping | Maps full problem keys to concise problem short names | Problem ID string (e.g. `riemann_hypothesis`) | Short name string (`Riemann`) | Returns full name if unmapped | `delta_report.py:74-81` |
| 4 | CLI Runner | Argument Parser | Parses CLI flags `--db` and `--compare-previous` | Terminal command arguments | `args.db`, `args.compare_previous` | Exit code 2 on invalid flags (argparse standard) | `run_benchmarks.py:136-139` |
| 5 | CLI Runner | Regression Guard | Checks if any dimension score dropped > 5% vs previous run | Baseline run, current run | Exit code 0 (pass) or 1 (regression) | Exits with 1 and prints regression details to stderr/stdout | `run_benchmarks.py:228-233` |
| 6 | SQLite DB | Schema Migration (`eval_runs` / `eval_readiness`) | Creates and maintains evaluation tables in SQLite | Database connection path | Created tables in SQLite database | Raises `sqlite3.OperationalError` if path unwritable | `run_benchmarks.py:39-66` |
| 7 | REST API | `GET /eval/scores` | Endpoint returning latest capability scores for 8 dimensions | HTTP GET request | JSON map of 8 capability dimension scores | Returns fallback baseline JSON if DB empty | `eval_api.py:81-85` |
| 8 | REST API | `POST /eval/run` | Endpoint triggering full benchmark run synchronously | HTTP POST request | `BenchmarkRunResponse` JSON | 500 Internal Server Error if benchmark execution fails | `eval_api.py:124-246` |
| 9 | REST API | `GET /eval/history` | Endpoint returning last 10 evaluation run summaries | HTTP GET request | JSON list of run summary objects | Returns empty list `[]` if DB uninitialized | `eval_api.py:103-122` |
| 10 | REST API | `GET /eval/prize-readiness` | Endpoint returning evidence-based readiness for 6 prize problems | HTTP GET request | Ranked JSON list of 6 prize readiness scores | 500 Internal Server Error on calculation failure | `eval_api.py:88-100` |
| 11 | Audit Layer | Chief Skeptic Audit Document | Formal audit findings document capturing risks and directives | Manual/Automated audit analysis | `docs/audit/EPIC_002_audit.md` | Non-blocking document (used for compliance review) | `docs/audit/EPIC_002_audit.md` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Regression Guard | Score drop of exactly 5.0% (`diff = -0.05`) | `diff < -0.05` evaluates to `False`. System does NOT trigger regression exit code 1; exits 0. |
| 2 | Regression Guard | Score drop of 5.01% (`diff = -0.0501`) | `diff < -0.05` evaluates to `True`. System triggers exit code 1 and prints regression failure details. |
| 3 | CLI Runner | First run on empty SQLite database with `--compare-previous` | Database has no previous run. Delta generator creates synthetic baseline (estimating `prev = curr - 0.08`), resulting in synthetic +8% deltas. |
| 4 | Delta Report Format | Percentage delta equal to 0% (`diff = 0.0`) | Output formats as `+0%` (explicit plus sign prefix retained). |
| 5 | Delta Report Format | Negative percentage delta (`diff = -0.12`) | Output formats as `-12%` (minus sign prefix retained). |
| 6 | Delta Report Format | Unicode Arrow character | Uses exact Unicode U+2192 rightwards arrow (`→`) in `<old> → <new>` integer point deltas. |
| 7 | Proof Verification | Sandbox missing Lean 4 compiler binary | Benchmark switches to `_simulate_lean4_check()` fallback. Audit layer flags score as `estimated: true` and restricts PV level to < L3. |
| 8 | REST API `/eval/run` | Concurrent benchmark execution requests | Synchronous DB table lock in SQLite. SQLite handles concurrent reads/writes via internal busy timeout. |
