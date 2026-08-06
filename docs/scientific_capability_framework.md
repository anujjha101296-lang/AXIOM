# Scientific Capability Framework (SCF)
## AXIOM Labs — EPIC-002 Scientific Capability Evaluation Platform

> Version: 1.0.0
> Status: Ratified
> Owner: Department A (Scientific Benchmarking) + Department J (Chief Skeptic)

---

## 1. Purpose

The Scientific Capability Framework is the **objective source of truth** for evaluating whether AXIOM is becoming a better scientist. It defines 8 capability dimensions, 6 levels per dimension, evaluation rubrics, and the composite score formula.

> ⚠️ All prize readiness scores must be grounded in benchmark measurements from this framework. Estimates without evidence are rejected.

---

## 2. Capability Dimensions

### Dimension 1: Mathematical Reasoning (MR)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Cannot evaluate mathematical claims |
| L1 | Arithmetic | Correct arithmetic on integers, rationals |
| L2 | Undergraduate | Solves calculus, linear algebra, basic proofs (e.g., induction) |
| L3 | Graduate | Solves real analysis, abstract algebra, topology problems |
| L4 | Research-Adjacent | Reproduces published lemmas; identifies proof gaps |
| L5 | Research-Active | Generates novel proofs; contributes to open problems |

**Benchmark**: `benchmarks/math_reasoning/`
**Rubric**: % of test problems solved correctly (auto-graded against known solutions)
**L-threshold**: L1≥0.4, L2≥0.55, L3≥0.70, L4≥0.82, L5≥0.95

---

### Dimension 2: Proof Verification (PV)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Cannot check proofs |
| L1 | Syntactic | Checks basic LaTeX/Lean4 syntax |
| L2 | Type-Check | Compiles Lean4 type-correct declarations |
| L3 | Tactic-Valid | Verifies simple tactic proofs (ring, simp, linarith) |
| L4 | Semantic | Verifies complex tactic proofs with custom lemmas |
| L5 | Production | Compiles Mathlib-dependent proofs; catches subtle errors |

**Benchmark**: `benchmarks/proof_verification/`
**Rubric**: % of proof scripts correctly classified as valid/invalid
**L-threshold**: L1≥0.5, L2≥0.6, L3≥0.70, L4≥0.82, L5≥0.95

---

### Dimension 3: Conjecture Generation (CG)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Generates no conjectures |
| L1 | Trivial | Generates syntactically valid but trivially true/false conjectures |
| L2 | Nontrivial | Generates non-trivial conjectures with novelty score ≥0.25 |
| L3 | Domain-Specific | Generates domain-relevant conjectures from EGS patterns |
| L4 | Creative | Generates conjectures independently verified as interesting by experts |
| L5 | Prize-Adjacent | Generates conjectures directly related to open prize problems |

**Benchmark**: `benchmarks/conjecture_generation/`
**Rubric**: mean novelty score of top-5 generated conjectures + tautology rate (lower = better)
**L-threshold**: L1≥0.1, L2≥0.25, L3≥0.40, L4≥0.60, L5≥0.80

---

### Dimension 4: Knowledge Quality (KQ)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | No structured knowledge |
| L1 | Raw | Can store unstructured text about mathematics |
| L2 | Structured | Stores typed nodes (theorem, lemma, definition) with domains |
| L3 | Linked | Builds dependency graphs between theorems |
| L4 | Accurate | ≥90% of stored claims are epistemically correct |
| L5 | Complete | Domain coverage ≥85% of undergraduate curriculum |

**Benchmark**: `benchmarks/knowledge_quality/`
**Rubric**: precision of stored claims × completeness × graph connectivity
**L-threshold**: L1≥0.2, L2≥0.4, L3≥0.55, L4≥0.75, L5≥0.90

---

### Dimension 5: Counterexample Search (CE)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Cannot search for counterexamples |
| L1 | Random | Random parameter sweep (blind) |
| L2 | Heuristic | SMT-guided search within bounded domains |
| L3 | Targeted | Z3 SMT solver with domain-specific axioms |
| L4 | Adaptive | Combines SMT + symbolic + iterative refinement |
| L5 | Expert | Finds counterexamples for published open conjectures |

**Benchmark**: `benchmarks/counterexample_search/`
**Rubric**: % of planted counterexamples found within 60s
**L-threshold**: L1≥0.1, L2≥0.30, L3≥0.50, L4≥0.70, L5≥0.90

---

### Dimension 6: Research Planning (RP)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | No research planning capability |
| L1 | Linear | Executes a fixed, manually-specified plan |
| L2 | Decomposed | Decomposes a problem into lemmas with dependencies |
| L3 | Prioritized | Ranks sub-problems by P(L) = (impact × feasibility) / cost |
| L4 | Adaptive | Updates the plan based on proof successes/failures |
| L5 | Strategic | Self-generates research roadmaps for prize problems |

**Benchmark**: `benchmarks/research_planning/`
**Rubric**: quality of problem decomposition (completeness × ordering correctness)
**L-threshold**: L1≥0.2, L2≥0.40, L3≥0.60, L4≥0.75, L5≥0.90

---

### Dimension 7: Literature Synthesis (LS)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Cannot process mathematical literature |
| L1 | Extraction | Extracts theorem names and references from LaTeX |
| L2 | Parsing | Parses statement structure (hypothesis, conclusion) |
| L3 | Dependency | Builds citation dependency graphs |
| L4 | Cross-paper | Links theorems across multiple papers |
| L5 | Synthesis | Identifies gaps, overlaps, and research opportunities |

**Benchmark**: `benchmarks/literature_synthesis/`
**Rubric**: precision + recall of extracted mathematical objects vs. ground truth
**L-threshold**: L1≥0.4, L2≥0.55, L3≥0.65, L4≥0.78, L5≥0.90

---

### Dimension 8: Research Productivity (RD)

| Level | Name | Criteria |
|-------|------|----------|
| L0 | None | Cannot sustain research activity |
| L1 | Manual | Requires human direction for every step |
| L2 | Semi-Auto | Can execute a pre-defined research plan autonomously |
| L3 | Looped | Runs continuous discovery loops without intervention |
| L4 | Self-Improving | Identifies its weakest capability and proposes improvement |
| L5 | Autonomous | Operates as a full autonomous research team |

**Benchmark**: `benchmarks/research_productivity/`
**Rubric**: number of non-trivial verified scientific outputs per session (normalized)
**L-threshold**: L1≥0.1, L2≥0.25, L3≥0.45, L4≥0.65, L5≥0.85

---

## 3. Composite Score Formula

$$S_{composite} = \frac{1}{8} \sum_{d=1}^{8} w_d \cdot S_d$$

Where:
- $S_d$ = normalized score for dimension $d$ ∈ [0, 1]
- $w_d$ = dimension weight (see table below)
- All weights sum to 1.0

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Mathematical Reasoning | 0.20 | Core foundation |
| Proof Verification | 0.18 | Prize-critical |
| Conjecture Generation | 0.15 | Discovery engine |
| Knowledge Quality | 0.12 | Data integrity |
| Counterexample Search | 0.12 | Refutation power |
| Research Planning | 0.10 | Strategy layer |
| Literature Synthesis | 0.08 | Ingestion quality |
| Research Productivity | 0.05 | Autonomy level |

**AXIOM Readiness Threshold**: S_composite ≥ 0.85 before any prize submission attempt.

---

## 4. Level Classification Algorithm

Given raw benchmark scores for each dimension, the level is determined by:

```python
def classify_level(score: float, dimension: str) -> int:
    thresholds = LEVEL_THRESHOLDS[dimension]  # [L1, L2, L3, L4, L5]
    for level, threshold in reversed(list(enumerate(thresholds, 1))):
        if score >= threshold:
            return level
    return 0
```

---

## 5. Chief Skeptic Review (Department J)

> *"This framework is methodologically sound. However, levels L4–L5 for Proof Verification and Conjecture Generation currently have no automated benchmark mechanism without actual Lean 4 compiler access. All scores at these levels must be marked ESTIMATED until formal proof compilation is operational. No prize readiness score may exceed 0.5 until at least one dimension reaches L4 with a verified automated benchmark."*

**Mandatory review interval**: After every Epic completion.
**Rejection authority**: Department J may veto any score computed without benchmark evidence.
