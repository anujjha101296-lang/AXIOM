# SCEP Survey Analysis: R1 (Scientific Capability Framework) & R2 (Benchmark Suite)

**Author**: Explorer 1 (`explorer_scep_survey_1`)  
**Date**: 2026-08-06  
**Target Subsystem**: AXIOM EPIC-002: Scientific Capability Evaluation Platform (SCEP)  
**Codebase Locations**:  
- `axiom/evaluation/frameworks/capability.py`
- `axiom/evaluation/benchmarks/suite.py`
- `axiom/evaluation/frameworks/prize_readiness.py`
- `axiom/evaluation/reporting/delta_report.py`
- `axiom/evaluation/run_benchmarks.py`
- `docs/scientific_capability_framework.md`
- `tests/test_evaluation_platform.py` & `tests/test_benchmark.py`

---

## Executive Summary

An exhaustive investigation of the existing codebase for **EPIC-002: Scientific Capability Evaluation Platform (SCEP)** was conducted to assess the current status, implementation fidelity, and missing requirements for:
1. **R1: Scientific Capability Framework (SCF)**
2. **R2: Benchmark Suite**

The SCEP implementation provides a clean, well-architected framework for objective capability measurement. However, key discrepancies exist between documentation and code, and 3 out of 8 capability dimensions currently lack runnable benchmark implementations (relying instead on static fallback estimates in `run_benchmarks.py`).

---

## 1. Requirement 1 (R1) — Scientific Capability Framework Analysis

### 1.1 Current Code Implementation (`axiom/evaluation/frameworks/capability.py`)
- **Dimensions**: Defines the `CapabilityDimension` Enum covering exactly 8 dimensions:
  1. `MATHEMATICAL_REASONING` (weight: `0.20`)
  2. `PROOF_VERIFICATION` (weight: `0.18`)
  3. `CONJECTURE_GENERATION` (weight: `0.15`)
  4. `KNOWLEDGE_QUALITY` (weight: `0.12`)
  5. `COUNTEREXAMPLE_SEARCH` (weight: `0.12`)
  6. `RESEARCH_PLANNING` (weight: `0.10`)
  7. `LITERATURE_SYNTHESIS` (weight: `0.08`)
  8. `RESEARCH_PRODUCTIVITY` (weight: `0.05`)
- **Weights**: Sum of `DIMENSION_WEIGHTS` is strictly `1.00`.
- **Level Taxonomy**: 6 discrete levels defined (`LEVEL_NAMES`):
  - `L0: None`, `L1: Basic`, `L2: Undergraduate`, `L3: Graduate`, `L4: Research-Adjacent`, `L5: Research-Active`.
- **Level Thresholds**: `LEVEL_THRESHOLDS` mapping provides 5 threshold cutoffs `[L1, L2, L3, L4, L5]` for each dimension. Classification is executed via `classify_level(score, dimension)`.
- **Composite Score Formula**: Computed in `CapabilitySnapshot.compute_composite()`:
  $$S_{\text{composite}} = \sum_{d=1}^{8} w_d \cdot S_d$$
  where $S_d \in [0.0, 1.0]$ is the raw dimension score and $w_d$ is the weight.
- **Dataclass Architecture**:
  - `BenchmarkCase`: ID, description, category, expected answer, difficulty.
  - `BenchmarkResult`: case ID, score $[0, 1]$, passed status, execution time in ms, notes, raw output.
  - `DimensionScore`: dimension, raw score, level (0–5), level name, confidence, benchmark count, `estimated` flag.
  - `CapabilitySnapshot`: run ID, timestamp, list of `DimensionScore`, composite score, list of estimated dimension names.

### 1.2 Current Documentation (`docs/scientific_capability_framework.md`)
- Exists at `docs/scientific_capability_framework.md`.
- Defines all 8 dimensions with detailed criterion tables for levels L0–L5.
- Specifies L-thresholds for each dimension.
- Documents Department J (Chief Skeptic) review authority and estimated score handling.

### 1.3 Discrepancies & Missing Elements for R1
1. **Formula Inconsistency in Documentation**:
   - In `docs/scientific_capability_framework.md` Section 3, the LaTeX equation is written as $S_{\text{composite}} = \frac{1}{8} \sum_{d=1}^{8} w_d \cdot S_d$.
   - Below the equation, the document correctly states "All weights sum to 1.0".
   - Multiplying by $\frac{1}{8}$ when weights sum to 1.0 yields a maximum possible composite score of $0.125$, contradicting the $0.85$ prize submission threshold.
   - **Code Implementation**: `CapabilitySnapshot.compute_composite()` in `capability.py` correctly calculates $\sum_{d=1}^{8} w_d \cdot S_d$ (without dividing by 8). The documentation formula contains a notation typo ($\frac{1}{8}$) that should be removed.
2. **Static Estimated Scores for 3 Dimensions**:
   - In `axiom/evaluation/run_benchmarks.py`, 3 of the 8 dimensions are not backed by benchmark functions in `suite.py`:
     - `COUNTEREXAMPLE_SEARCH`: hardcoded to `0.35` (`estimated=True`)
     - `LITERATURE_SYNTHESIS`: hardcoded to `0.40` (`estimated=True`)
     - `RESEARCH_PRODUCTIVITY`: hardcoded to `0.50` (`estimated=True`)
   - To achieve full R1 fidelity, runnable benchmarks for these 3 dimensions must be added to `suite.py`.
3. **Directory Path Misalignment**:
   - `docs/scientific_capability_framework.md` lists paths like `benchmarks/math_reasoning/`, `benchmarks/proof_verification/`, etc.
   - In the codebase, all benchmarks are consolidated in `axiom/evaluation/benchmarks/suite.py`.

---

## 2. Requirement 2 (R2) — Benchmark Suite Analysis

### 2.1 Current Implementation (`axiom/evaluation/benchmarks/suite.py`)
The benchmark suite currently contains 5 executable benchmark runner functions:

| Category # | Dimension / Category | Function Name | Case Count | Tested Capabilities / Scope |
|---|---|---|---|---|
| **1** | `MATHEMATICAL_REASONING` | `run_math_reasoning_benchmarks()` | 10 (`mr_001`–`mr_010`) | Arithmetic series sum, quadratic roots, GCD, modular exponentiation, Fermat's Little Theorem, polynomial derivative, definite integral, Euler's identity ($e^{i\pi}+1=0$), primality test, $\zeta(2) = \pi^2/6$. |
| **2** | `PROOF_VERIFICATION` | `run_proof_verification_benchmarks()` | 7 (`pv_001`–`pv_007`) | Lean4 script validity & comment failure, Coq script validity & Qed failure, Isabelle script validity, Lean4 `ring` tactic, Lean4 `linarith` tactic. |
| **3** | `CONJECTURE_GENERATION` | `run_conjecture_benchmarks()` | 5 (`cg_001`–`cg_005`) | Tautology detection (positive/negative), novelty score range $[0, 1]$, candidate generation count $\ge 1$, mean novelty $\ge 0.2$, tautology filtering on generated candidates. |
| **4** | `KNOWLEDGE_QUALITY` | `run_knowledge_quality_benchmarks()` | 5 (`kq_001`–`kq_005`) | `mip_domains` table domain count ($\ge 8$), `MathObjectType` count ($15$), domain text classification accuracy, v5 migration table verification ($7$ MIP tables), Millennium Problem metadata completeness ($6$). |
| **5** | `RESEARCH_PLANNING` | `run_research_planning_benchmarks()` | 5 (`rp_001`–`rp_005`) | All 6 Millennium Problem decomposition trees present, $P(L) = \frac{\text{impact} \cdot \text{feasibility}}{\text{cost}}$ priority index formula verification, queue sorting descending, Riemann Hypothesis lemma count ($\ge 5$), top feasibility lemma check. |

### 2.2 Requirement Comparison Table (R2 vs. Current Code)

| R2 Requirement | Required Specification | Current Code Implementation | Status / Gap |
|---|---|---|---|
| **Category Count** | $\ge 5$ runnable categories | 5 runnable categories in `suite.py` | **PASS** |
| **Test Case Count** | $\ge 3$ test cases per category | 10, 7, 5, 5, 5 test cases respectively | **PASS** (exceeds requirement) |
| **Undergraduate Algebra / Calculus** | Auto-gradable problems | 10 cases in `run_math_reasoning_benchmarks()` covering algebra, modular arithmetic, derivatives, integrals, series. | **PASS** |
| **Theorem Reproduction** | Published theorem reproduction tests | Euler identity ($e^{i\pi}+1=0$) and $\zeta(2)$ tested in Math Reasoning, but no dedicated `run_theorem_reproduction_benchmarks()` category. | **PARTIAL** (embedded in MR, needs explicit category mapping) |
| **Proof Verification** | Formal proof verification benchmarks | 7 cases in `run_proof_verification_benchmarks()` testing Lean4, Coq, Isabelle generators/simulators and tactic selection. | **PASS** |
| **Conjecture Novelty** | Novelty benchmarks for generated claims | 5 cases in `run_conjecture_benchmarks()` evaluating tautology filter, novelty range $[0,1]$, candidate output, and mean novelty. | **PASS** |
| **Open Problem Decomposition** | Decomposition tree benchmarks | 5 cases in `run_research_planning_benchmarks()` testing Millennium problem trees, $P(L)$ calculation, and queue priority ordering. | **PASS** |
| **Run Limit** | $< 2$ minutes total run time | Total suite execution time: **~0.25 seconds** | **PASS** (well within limit) |
| **Score Bounding** | Numeric score in $[0, 1]$ | Every benchmark function returns a normalized float in $[0, 1]$ | **PASS** |

### 2.3 Gaps & Deficiencies in R2
1. **Missing Runnable Benchmarks for 3 Dimensions**:
   - `COUNTEREXAMPLE_SEARCH`: Needs a benchmark suite (e.g. testing SMT Z3 counterexample discovery on invalid modular/algebraic claims). Currently hardcoded to `0.35` in `run_benchmarks.py`.
   - `LITERATURE_SYNTHESIS`: Needs a benchmark suite (e.g. LaTeX AST parsing precision, theorem/citation extraction accuracy). Currently hardcoded to `0.40` in `run_benchmarks.py`.
   - `RESEARCH_PRODUCTIVITY`: Needs a benchmark suite (e.g. measuring autonomous research loop cycles, verified outputs per minute). Currently hardcoded to `0.50` in `run_benchmarks.py`.
2. **Explicit Theorem Reproduction Category**:
   - R2 explicitly lists "published theorem reproduction tests" as a benchmark requirement. While `mr_008` ($e^{i\pi}+1=0$) and `mr_010` ($\zeta(2) = \pi^2/6$) cover this, creating a dedicated `run_theorem_reproduction_benchmarks()` or mapping it clearly in `suite.py` will satisfy the requirement directly.

---

## 3. Summary of Findings & Next Steps

1. **R1 Summary**:
   - Code structure in `capability.py` is robust and matches the 8 dimensions, L0–L5 taxonomy, and $S_{\text{composite}} = \sum w_d \cdot S_d$ formula.
   - Action item for documentation: Fix the $\frac{1}{8}$ notation error in `docs/scientific_capability_framework.md` Section 3.
2. **R2 Summary**:
   - The runnable benchmark suite in `suite.py` satisfies 5 categories with $\ge 3$ test cases each, completes in $< 1$ second, and outputs bounded scores in $[0, 1]$.
   - Action item for benchmark suite: Implement runnable benchmark functions for `COUNTEREXAMPLE_SEARCH`, `LITERATURE_SYNTHESIS`, and `RESEARCH_PRODUCTIVITY` so `run_benchmarks.py` no longer relies on hardcoded estimated values.
