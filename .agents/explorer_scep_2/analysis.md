# Specification Mining Analysis Report — EPIC-002 Scientific Capability Evaluation Platform (SCEP)

> **Agent**: Explorer 2 (Spec Miner)  
> **Target Subsystem**: Scientific Capability Evaluation Platform (SCEP)  
> **Workspace**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`  
> **Date**: 2026-08-06  
> **Status**: Completed Specification Mining  

---

## Executive Summary

This document specifies the complete, authoritative, mined requirements for **EPIC-002: Scientific Capability Evaluation Platform (SCEP)** of AXIOM Labs. SCEP provides an objective, evaluation-first measurement system that determines whether engineering sprints measurably advance AXIOM's scientific discovery capabilities.

The framework is modeled on AlphaFold's evaluation-first philosophy, establishing rigorous benchmarks, taxonomy levels, grounding requirements, prize readiness models, and capability delta tracking prior to downstream feature optimization.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | R1: Capability Framework | Dimension Taxonomy (L0–L5) | Defines 6 maturity levels (L0 None, L1 Basic, L2 Undergraduate, L3 Graduate, L4 Research-Adjacent, L5 Research-Active) across 8 scientific dimensions | Dimension score float $\in [0, 1]$, dimension enum | Integer level $L \in \{0..5\}$ and level name string | Defaults to L0 if score below L1 threshold | `docs/scientific_capability_framework.md`, `axiom/evaluation/frameworks/capability.py` |
| 2 | R1: Capability Framework | Level Classification Algorithm | `classify_level(score, dimension)` maps raw benchmark score to level based on per-dimension thresholds | `score: float`, `dimension: CapabilityDimension` | `level: int` (0–5) | Returns 0 if score < lowest threshold | `axiom/evaluation/frameworks/capability.py:135` |
| 3 | R1: Capability Framework | Composite Score Formula | $S_{\text{composite}} = \sum_{d=1}^{8} w_d \cdot S_d$ with 8 weighted dimensions summing to 1.0 | 8 normalized dimension scores $S_d \in [0, 1]$ | `composite_score: float` rounded to 4 decimals | Unset dimensions defaulted to 0.0 | `docs/scientific_capability_framework.md:158`, `axiom/evaluation/frameworks/capability.py:105` |
| 4 | R1: Capability Framework | Dimension Weighting Schema | Mathematical Reasoning (0.20), Proof Verification (0.18), Conjecture Gen (0.15), Knowledge Quality (0.12), Counterexample Search (0.12), Research Planning (0.10), Literature Synth (0.08), Research Productivity (0.05) | N/A (Static weight dictionary) | Weight mapping dictionary | Weights sum strictly to 1.00 | `axiom/evaluation/frameworks/capability.py:24` |
| 5 | R2: Benchmark Suite | Auto-Gradable Math Reasoning Suite | 10 math test cases (arithmetic, quadratic, GCD, modular, calculus, Fermat, Euler, prime, zeta) | Test case parameters | `BenchmarkResult(case_id, score, passed, time_ms, notes)` | Catches exceptions, sets `passed=False`, score=0.0 | `axiom/evaluation/benchmarks/suite.py:40` |
| 6 | R2: Benchmark Suite | Proof Verification Suite | 7 formal proof cases for Lean4/Coq/Isabelle syntax, tactic suggestions, and simulation checks | Script templates, target statements | `BenchmarkResult` with pass/fail and execution timing | Fallback simulation logs warning if compiler missing | `axiom/evaluation/benchmarks/suite.py:152` |
| 7 | R2: Benchmark Suite | Conjecture Novelty Suite | 5 cases testing tautology filtering, novelty scoring range $[0, 1]$, candidate count, and mean novelty | `db_path: str` | `BenchmarkResult` list and category score | Returns score 0.0 if conjecture engine unavailable | `axiom/evaluation/benchmarks/suite.py:234` |
| 8 | R2: Benchmark Suite | Knowledge Quality Suite | 5 cases evaluating domain table counts, 15 object types, classification accuracy, table migrations, and Millennium metadata | SQLite `db_path: str` | `BenchmarkResult` list and category score | Temporary DB cleanup in `finally` block on migration fail | `axiom/evaluation/benchmarks/suite.py:347` |
| 9 | R2: Benchmark Suite | Open Problem Decomposition Suite | 5 cases testing 6 Millennium problem trees, $P(L)$ priority index calculation, and sorted lemma queues | Problem ID string | `BenchmarkResult` list and category score | Returns 0.0 score if strategy module missing | `axiom/evaluation/benchmarks/suite.py:474` |
| 10 | R2: Benchmark Suite | Counterexample Search Suite | 5 cases testing modular arithmetic, real inequality bounds, polynomial identities, and Fermat composite disproof | SymPy / Z3 SMT gateway inputs | `BenchmarkResult` list and category score | Catches solver timeout/errors, logs notes | `axiom/evaluation/benchmarks/suite.py:561` |
| 11 | R2: Benchmark Suite | Literature Synthesis Suite | 5 cases testing LaTeX environment parsing, citation graph keys, epistemic tagging, and domain classification | TeX content string | `BenchmarkResult` list and category score | Graceful fallback if parser modules missing | `axiom/evaluation/benchmarks/suite.py:661` |
| 12 | R2: Benchmark Suite | Research Productivity Suite | 5 cases testing hypothesis engine execution, working memory snapshot/restore, tactic search, refutation, and loop stability | SQLite DB path & `WorkingMemory` instance | `BenchmarkResult` list and category score | Returns 0.0 on import error | `axiom/evaluation/benchmarks/suite.py:788` |
| 13 | R3: Prize Readiness Engine | Scored Readiness Model | Scored readiness model for all 6 Millennium Problems (Riemann, P vs NP, Yang-Mills, BSD, Navier-Stokes, Hodge) | Dict of benchmark dimension scores | `list[PrizeReadinessScore]` with score, CI, prerequisites, gaps | Sets `estimated=True` if live compiler evidence missing | `axiom/evaluation/frameworks/prize_readiness.py:318` |
| 14 | R3: Prize Readiness Engine | Capability Prerequisite Mapping | Maps required capabilities, required level (L0-L5), current level, weight, and gap descriptions | Benchmark dimension scores | `list[CapabilityPrerequisite]` objects per problem | Mapped dynamically from benchmark outputs | `axiom/evaluation/frameworks/prize_readiness.py:13` |
| 15 | R3: Prize Readiness Engine | Grounded Score & CI Formula | Weighted combination of dimension scores per problem; confidence intervals derived from score error bounds | Benchmark dimension scores | Score $\in [0, 1]$, CI tuple $(c_{\text{low}}, c_{\text{high}})$ | Clamped to $[0.0, 1.0]$ | `axiom/evaluation/frameworks/prize_readiness.py:74` |
| 16 | R4: Delta Report Generator | Capability Delta Report Generator | Compares previous and current snapshot runs, producing structured JSON & formatted Markdown | `prev_snapshot`, `curr_snapshot`, `prev_readiness`, `curr_readiness` | `CapabilityDeltaReport` object | Baselines against synthetic prior run if no history | `axiom/evaluation/reporting/delta_report.py:108` |
| 17 | R4: Delta Report Generator | Exact Markdown Format Spec | Generates Markdown report matching strict AXIOM specification layout with per-dimension % and 100-pt integer readiness | `CapabilityDeltaReport` instance | Formatted Markdown string | Displays `⚠️ REGRESSIONS DETECTED` if flag set | `axiom/evaluation/reporting/delta_report.py:46`, `ORIGINAL_REQUEST.md:183` |
| 18 | R4: Delta Report Generator | Weakest Capability & Priority Mapper | Identifies lowest dimension score and maps it to explicit engineering priority and recommended next epic | Current dimension scores | `weakest_capability: str`, `highest_priority: str`, `recommended_next_epic: str` | Defaults to "Build Formal Proof & Lemma Discovery Platform" | `axiom/evaluation/reporting/delta_report.py:127` |
| 19 | R4: Delta Report Generator | Regression Guard | Flags regression if any dimension score drops by > 5% ($\Delta < -0.05$) between consecutive runs | `regression_threshold: float = 0.05` | `regression_detected: bool`, `regression_details: list[str]` | Populates detailed regression messages | `axiom/evaluation/reporting/delta_report.py:148` |
| 20 | R5: API & CLI Runner | Benchmark CLI Runner | CLI script executing all 8 benchmark suites, persisting to SQLite, saving reports, and enforcing exit codes | Arguments `--db PATH`, `--compare-previous` | Exits with code 0 (success) or 1 (regression detected) | Exits with code 1 when `--compare-previous` detects >5% drop | `axiom/evaluation/run_benchmarks.py:138` |
| 21 | R5: API & CLI Runner | Evaluation SQLite Schema | Tables `eval_runs` (`run_id`, `timestamp`, `composite_score`, `json_data`) and `eval_readiness` (`run_id`, `problem_id`, `score`, `json_data`) | SQLite database connection | Table creation and snapshot insertion | `CREATE TABLE IF NOT EXISTS` prevents schema collision | `axiom/evaluation/run_benchmarks.py:42` |
| 22 | R6: Audit Layer | Independent Audit Directives | Chief Skeptic (Dept J) and Independent Audit (Dept I) audit report flagging optimistic assumptions and gamed benchmarks | SCEP codebase and benchmark execution logs | Audit findings in `docs/audit/EPIC_002_audit.md` | Disputes scores calculated without live compiler evidence | `docs/audit/EPIC_002_audit.md` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | R1: Level Classification | Score $0.3999$ for Mathematical Reasoning (threshold L1 is 0.40) | Classified as Level 0 (None) because score $< 0.40$ threshold. |
| 2 | R1: Composite Score Calculation | Missing dimension score in snapshot | Missing dimension raw score defaults to $0.0$, contributing $0.0$ to weighted sum. |
| 3 | R2: Benchmark Execution | Formal Lean4/Coq compiler binaries absent in environment | Benchmark uses structural simulation check (`_simulate_lean4_check`), returns pass/fail, logs diagnostic note, and flags score as `estimated=True`. |
| 4 | R2: Benchmark Suite Timing | Slow SMT solver or MCTS tactic search step | `suite.py` measures `time_ms` per test case using high-precision `time.perf_counter()`; total suite completes in $< 2$ seconds. |
| 5 | R2: Quad Equation Solver (`mr_002`) | Negative discriminant quadratic | Python stdlib solver handles roots gracefully using float/complex arithmetic. |
| 6 | R3: Prize Readiness Grounding | Zero benchmark data available for dimension | Score engine returns baseline weighted score with `estimated=True` flag and minimal confidence bounds. |
| 7 | R3: Prize Readiness Grounding | High benchmark scores (e.g. 0.90 across all dimensions) | Readiness score increases proportionally (e.g. RH score goes from $0.10 \to > 0.60$), but remains bounded by $[0, 1]$. |
| 8 | R4: Capability Delta Report | First benchmark run (no previous database snapshot) | Generator sets `previous_run_id="BASELINE"`, computes baseline estimate (curr score - 0.05 / curr points - 2), and generates valid comparative delta report. |
| 9 | R4: Capability Delta Report | Dimension score drops from $0.75$ to $0.68$ ($\Delta = -0.07$ or $-7\%$) | Sets `regression_detected=True`, appends `"proof_verification dropped by 7% (0.750 → 0.680)"` to `regression_details`, and CLI `--compare-previous` exits with code 1. |
| 10 | R4: Capability Delta Report | Integer point conversion for prize readiness score $0.336$ | Converted via `int(round(0.336 * 100))` to `34` points. Delta rendered as `31 → 34`. |
| 11 | R5: Database Run Storage | Concurrent CLI runs accessing SQLite database | Uses SQLite transactional locks; `save_run` executes in a single committed transaction. |

---

## Deep Dive: Requirement Specifications

### R1. Scientific Capability Framework (SCF)

#### 1. Capability Dimensions & Weights
The framework tracks 8 scientific capability dimensions. The composite score formula is:
$$S_{\text{composite}} = \sum_{d=1}^{8} w_d \cdot S_d$$
where $\sum_{d=1}^{8} w_d = 1.00$.

| Dimension Enum | Display Name | Weight ($w_d$) | Description | Rationale |
|----------------|--------------|----------------|-------------|-----------|
| `mathematical_reasoning` | Mathematical Reasoning | 0.20 | Core mathematical problem solving (algebra, calculus, number theory) | Core foundation |
| `proof_verification` | Proof Verification | 0.18 | Formal proof checking and tactic validation (Lean 4, Coq, Isabelle) | Prize-critical |
| `conjecture_generation` | Conjecture Generation | 0.15 | Autonomous hypothesis generation and novelty scoring | Discovery engine |
| `knowledge_quality` | Knowledge Understanding | 0.12 | Ontological graph structure, claim precision, and curriculum coverage | Data integrity |
| `counterexample_search` | Counterexample Search | 0.12 | SMT solver parameter sweeps and symbolic disproof | Refutation power |
| `research_planning` | Research Planning | 0.10 | Problem decomposition trees and $P(L)$ priority ranking | Strategy layer |
| `literature_synthesis` | Literature Synthesis | 0.08 | LaTeX parsing, citation graphs, and epistemic claim tagging | Ingestion quality |
| `research_productivity` | Research Productivity | 0.05 | Autonomous discovery loop stability and working memory management | Autonomy level |

#### 2. Taxonomy Levels (L0–L5) & Thresholds
Each dimension is classified into levels L0 through L5 based on explicit score thresholds:

| Level | Level Name | Criteria Summary |
|-------|------------|------------------|
| L0 | None | Cannot evaluate or process claims in this dimension |
| L1 | Basic / Arithmetic | Performs basic arithmetic / syntax checks / raw storage |
| L2 | Undergraduate / Structured | Solves undergraduate problems, compiles basic typed declarations |
| L3 | Graduate / Tactic-Valid | Solves graduate problems, verifies tactic proofs, domain conjectures |
| L4 | Research-Adjacent / Semantic | Reproduces published lemmas, semantic verification, adaptive planning |
| L5 | Research-Active / Autonomous | Solves/decomposes open prize problems, autonomous discovery loops |

Per-dimension Level Cutoff Thresholds (`LEVEL_THRESHOLDS`):
- **Mathematical Reasoning**: L1 $\ge 0.40$, L2 $\ge 0.55$, L3 $\ge 0.70$, L4 $\ge 0.82$, L5 $\ge 0.95$
- **Proof Verification**: L1 $\ge 0.50$, L2 $\ge 0.60$, L3 $\ge 0.70$, L4 $\ge 0.82$, L5 $\ge 0.95$
- **Conjecture Generation**: L1 $\ge 0.10$, L2 $\ge 0.25$, L3 $\ge 0.40$, L4 $\ge 0.60$, L5 $\ge 0.80$
- **Knowledge Quality**: L1 $\ge 0.20$, L2 $\ge 0.40$, L3 $\ge 0.55$, L4 $\ge 0.75$, L5 $\ge 0.90$
- **Counterexample Search**: L1 $\ge 0.10$, L2 $\ge 0.30$, L3 $\ge 0.50$, L4 $\ge 0.70$, L5 $\ge 0.90$
- **Research Planning**: L1 $\ge 0.20$, L2 $\ge 0.40$, L3 $\ge 0.60$, L4 $\ge 0.75$, L5 $\ge 0.90$
- **Literature Synthesis**: L1 $\ge 0.40$, L2 $\ge 0.55$, L3 $\ge 0.65$, L4 $\ge 0.78$, L5 $\ge 0.90$
- **Research Productivity**: L1 $\ge 0.10$, L2 $\ge 0.25$, L3 $\ge 0.45$, L4 $\ge 0.65$, L5 $\ge 0.85$

---

### R2. Benchmark Suite Specification

The benchmark suite consists of 8 modular suites executing in under 2 minutes (total runtime $\sim 1.5$s in test environment). Scores for all cases are normalized in $[0.0, 1.0]$.

#### Mandatory Category Mappings (≥5 Categories, ≥3 Cases Each)

1. **`algebra/calculus`** (7 test cases):
   - `mr_001`: Sum of arithmetic series $1+2+...+100 = 5050$
   - `mr_002`: Roots of quadratic $x^2 - 5x + 6 = 0 \to \{2, 3\}$
   - `mr_003`: Greatest Common Divisor $\text{GCD}(48, 18) = 6$
   - `mr_004`: Modular arithmetic $2^{10} \bmod 7 = 2$
   - `mr_006`: Derivative of $x^3$ at $x=2 \to 12$
   - `mr_007`: Definite integral $\int_0^3 x^2 \, dx = 9$
   - `mr_009`: Primality check for $127 \to \text{True}$

2. **`theorem reproduction`** (3 test cases):
   - `mr_005`: Fermat's Little Theorem $3^{7-1} \bmod 7 = 1$
   - `mr_008`: Euler's Identity $e^{i\pi} + 1 = 0$ (imaginary part check)
   - `mr_010`: Basel Problem $\zeta(2) = \frac{\pi^2}{6}$ numerical check (error $< 0.01$)

3. **`proof verification`** (7 test cases):
   - `pv_001`: Lean4 structural validity of addition commutativity
   - `pv_002`: Lean4 failure check on empty/invalid script
   - `pv_003`: Coq structural validity of addition associativity
   - `pv_004`: Coq failure check on missing `Qed`
   - `pv_005`: Isabelle structural validity of multiplication distributivity
   - `pv_006`: Lean4 tactic suggestion (`ring`/`norm_num`) for equality
   - `pv_007`: Lean4 tactic suggestion (`linarith`) for inequality $a \le b$

4. **`conjecture novelty`** (5 test cases):
   - `cg_001`: Tautology filter detection ($x=x$, $1=1$ vs non-tautologies)
   - `cg_002`: Novelty score bounding in range $[0, 1]$
   - `cg_003`: Generator produces $\ge 1$ candidate conjecture
   - `cg_004`: Mean novelty score of top generated conjectures $\ge 0.20$
   - `cg_005`: All candidate conjectures pass tautology filter

5. **`open problem decomposition`** (5 test cases):
   - `rp_001`: All 6 Millennium problems have decomposition trees
   - `rp_002`: Priority index formula $P(L) = \frac{\text{impact} \times \text{feasibility}}{\text{cost}}$
   - `rp_003`: Priority queue for Riemann Hypothesis sorted descending
   - `rp_004`: Riemann Hypothesis tree contains $\ge 5$ sub-lemmas
   - `rp_005`: Top-feasibility RH sub-lemma is computational verification

#### Additional Benchmark Suites Covered:
- **`knowledge quality`** (`kq_001` to `kq_005`): Domain table counts, 15 object types, domain classification accuracy, v5 migration integrity, Millennium metadata completeness.
- **`counterexample search`** (`ce_001` to `ce_005`): Modular counterexamples, real inequality bounds, polynomial identity checks, Fermat $F_5 = 2^{32}+1$ factor search ($641$).
- **`literature synthesis`** (`ls_001` to `ls_005`): LaTeX environment parsing, citation keys, epistemic status tagging, `EXTENDS` graph edges, semantic domain classification.
- **`research productivity`** (`rd_001` to `rd_005`): Hypothesis engine execution, working memory snapshot/restore, tactic search path efficiency, hypothesis refutation removal, session stability.

---

### R3. Prize Readiness Engine

The engine models readiness across all **6 Clay Millennium Prize Problems**. Each problem readiness score is calculated directly from benchmark scores.

#### 1. Scored Readiness Formulas & Weights

- **Riemann Hypothesis** (`riemann_hypothesis`, Domain: `number_theory`):
  $$S_{\text{RH}} = 0.35 \cdot S_{\text{MR}} + 0.30 \cdot S_{\text{PV}} + 0.20 \cdot S_{\text{LS}} + 0.15 \cdot S_{\text{CE}}$$
- **P vs NP** (`p_vs_np`, Domain: `computational_complexity`):
  $$S_{\text{PvsNP}} = 0.40 \cdot S_{\text{MR}} + 0.35 \cdot S_{\text{PV}} + 0.25 \cdot S_{\text{RP}}$$
- **Yang–Mills Existence and Mass Gap** (`yang_mills`, Domain: `mathematical_physics`):
  $$S_{\text{YM}} = (0.50 \cdot S_{\text{MR}} + 0.50 \cdot S_{\text{PV}}) \times 0.45$$
- **Birch and Swinnerton-Dyer Conjecture** (`birch_swinnerton_dyer`, Domain: `algebraic_geometry`):
  $$S_{\text{BSD}} = (0.45 \cdot S_{\text{MR}} + 0.35 \cdot S_{\text{PV}}) \times 0.50$$
- **Navier–Stokes Existence and Smoothness** (`navier_stokes`, Domain: `pde_analysis`):
  $$S_{\text{NS}} = (0.50 \cdot S_{\text{MR}} + 0.50 \cdot S_{\text{PV}}) \times 0.50$$
- **Hodge Conjecture** (`hodge_conjecture`, Domain: `algebraic_geometry`):
  $$S_{\text{Hodge}} = (0.50 \cdot S_{\text{MR}} + 0.50 \cdot S_{\text{PV}}) \times 0.40$$

#### 2. Prerequisites & Confidence Intervals
Each problem defines a list of `CapabilityPrerequisite` items specifying:
- `capability`: Human-readable capability name
- `dimension`: Associated `CapabilityDimension`
- `required_level`: Target taxonomy level (L1–L5)
- `current_level`: Calculated level from current benchmark score
- `weight`: Weight within problem score
- `evidence`: Grounded benchmark metric string

Confidence intervals are calculated dynamically:
$$\text{CI} = \left[ \text{round}(\text{score} \times (1 - \alpha), 4), \, \min\left(1.0, \, \text{round}(\text{score} \times (1 + \alpha), 4)\right) \right]$$
where $\alpha \in [0.15, 0.30]$ depending on domain complexity.

---

### R4. Capability Delta Report Generator

#### 1. Markdown Specification Format
The Capability Delta Report must adhere strictly to the following text format required by the master specification:

```markdown
EPIC-002 COMPLETE

Capability Delta

Knowledge Understanding
+12%

Proof Verification
+8%

Research Planning
+6%

Conjecture Generation
+4%

Counterexample Search
+0%

Prize Readiness

Riemann
31 → 34

P vs NP
28 → 30

Navier-Stokes
26 → 28

Weakest Capability
Automated Lemma Discovery

Highest Priority
Build Formal Proof & Lemma Discovery Platform

Recommended Next Epic
EPIC-003
```

#### 2. JSON Schema Output (`CapabilityDeltaReport.to_dict()`)

```json
{
  "epic_name": "EPIC-002",
  "previous_run_id": "BASELINE",
  "current_run_id": "15efc092",
  "timestamp": "2026-08-06T16:00:00Z",
  "dimension_deltas": {
    "mathematical_reasoning": {
      "prev_score": 0.85,
      "curr_score": 0.90,
      "delta_raw": 0.05,
      "delta_pct": 5,
      "curr_level": 5
    },
    "proof_verification": {
      "prev_score": 0.63,
      "curr_score": 0.7143,
      "delta_raw": 0.0843,
      "delta_pct": 8,
      "curr_level": 3
    }
  },
  "readiness_deltas": [
    {
      "problem_id": "riemann_hypothesis",
      "problem_name": "Riemann Hypothesis",
      "prev_points": 31,
      "curr_points": 34,
      "delta_points": 3
    }
  ],
  "weakest_capability": "Proof Verification",
  "highest_priority": "Build Formal Proof & Lemma Discovery Platform",
  "recommended_next_epic": "EPIC-003",
  "regression_detected": false,
  "regression_details": []
}
```

#### 3. Weakest Capability to Priority Mapping Matrix

| Weakest Capability Dimension | Identifies As | Highest Engineering Priority String | Recommended Next Epic |
|------------------------------|---------------|-------------------------------------|----------------------|
| `proof_verification` | Proof Verification | Build Formal Proof & Lemma Discovery Platform | EPIC-003 |
| `conjecture_generation` | Conjecture Generation | Enhance MCTS Exploration & Novelty Search Engine | EPIC-003 |
| `counterexample_search` | Counterexample Search | Scale SMT Parameter Sweep & Z3 Axiom Integration | EPIC-003 |
| `literature_synthesis` | Literature Synthesis | Expand arXiv Batch Parser & Reference Graph Builder | EPIC-003 |
| `research_planning` | Research Planning | Refine Millennium Decomposition DAGs & P(L) Heuristics | EPIC-003 |
| `knowledge_quality` | Knowledge Understanding | Enforce Strict Ontological Domain Classifications | EPIC-003 |
| `mathematical_reasoning` | Mathematical Reasoning | Integrate Exact SymPy Arbitrary-Precision Solver | EPIC-003 |
| `research_productivity` | Research Productivity | Implement Fully Autonomous Discovery Cycles | EPIC-003 |

---

### R5 & R6. API, CLI, and Audit Layer

#### 1. REST API Endpoints (`/eval/*`)
- `GET /eval/scores`: Returns current 8 capability dimension scores, levels, composite score, and estimated flags.
- `POST /eval/run`: Triggers benchmark suite execution, saves run snapshot in SQLite, generates delta report vs previous run.
- `GET /eval/history`: Returns last 10 benchmark run summaries.
- `GET /eval/prize-readiness`: Returns structured JSON for all 6 Millennium Problems with prerequisites and confidence intervals.

#### 2. CLI Runner (`axiom/evaluation/run_benchmarks.py`)
- Command: `python3 -m axiom.evaluation.run_benchmarks [--compare-previous] [--db PATH]`
- Options:
  - `--db PATH`: Path to SQLite database (default: `axiom.db`).
  - `--compare-previous`: Compares run with previous stored run; exits with code `1` if any dimension score drops by $> 5\%$ ($\Delta < -0.05$).
- Artifact Outputs:
  - `benchmark_results.json`: JSON output of `CapabilityDeltaReport.to_dict()`.
  - `docs/capability_delta_{RUN_ID}.md`: Formatted Markdown report.

#### 3. Audit Layer Directives (`docs/audit/EPIC_002_audit.md`)
- **Department J (Chief Skeptic) & Department I (Independent Audit)**:
  - Directive 1: Any dimension score lacking live automated compiler verification must be tagged `estimated=True`.
  - Directive 2: No prize readiness score may exceed $0.50$ until live formal proof compilation is operational.
  - Directive 3: Disallows self-assessment gaming; benchmark suites must use deterministic, verifiable mathematical outputs.
