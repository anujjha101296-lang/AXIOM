# Challenge Registry

Complete catalog of Grand Challenge Program challenges across all six tiers. Every challenge specifies objective, domain, difficulty, capabilities, tools, verification, success/failure criteria, benchmark metrics, and human review process.

**Evidence tiers:** `measured` | `simulated` | `heuristic` | `baseline` | `unavailable`

---

## Tier 0 — Toy Reasoning Problems

Infrastructure and pipeline validation. Auto-graded SCEP cases.

### t0_arithmetic_series

| Field | Value |
|-------|-------|
| **Objective** | Verify the system can solve and report a basic arithmetic series problem |
| **Domain** | mathematics |
| **Difficulty** | elementary |
| **Required capabilities** | mathematical_reasoning |
| **Required tools** | scep_benchmarks, sympy_engine |
| **Verification** | Auto-graded numeric answer (SCEP mr_001) |
| **Success** | Score >= 1.0; evidence tier = measured |
| **Failure** | Score < 1.0; no reproducible artifact |
| **Metrics** | case_score, time_ms, pass_rate |
| **Human review** | Spot-check numeric answer |

### t0_gcd_computation

| Field | Value |
|-------|-------|
| **Objective** | Validate basic number-theoretic computation pipeline |
| **Domain** | mathematics |
| **Difficulty** | elementary |
| **Required capabilities** | mathematical_reasoning |
| **Required tools** | scep_benchmarks |
| **Verification** | Auto-graded (SCEP mr_003: GCD(48,18)=6) |
| **Success** | Score >= 1.0 |
| **Failure** | Incorrect GCD |
| **Metrics** | case_score, time_ms |
| **Human review** | Automated pass/fail |

### t0_modular_arithmetic

| Field | Value |
|-------|-------|
| **Objective** | Confirm modular arithmetic evaluation end-to-end |
| **Domain** | mathematics |
| **Difficulty** | elementary |
| **Required capabilities** | mathematical_reasoning |
| **Required tools** | scep_benchmarks |
| **Verification** | Auto-graded (SCEP mr_004: 2^10 mod 7 = 2) |
| **Success** | Score >= 1.0 |
| **Failure** | Incorrect modular result |
| **Metrics** | case_score, time_ms |
| **Human review** | Automated pass/fail |

---

## Tier 1 — Known-Answer Theorem and Proof Tasks

Hidden ground truth. SCEP benchmarks with honest evidence tier labeling.

### t1_fermat_little_theorem

| Field | Value |
|-------|-------|
| **Objective** | Verify 3^(p-1) ≡ 1 (mod p) for prime p=7 |
| **Domain** | mathematics |
| **Difficulty** | undergraduate |
| **Required capabilities** | mathematical_reasoning, proof_verification |
| **Required tools** | scep_benchmarks, smt_gateway |
| **Verification** | SCEP mr_005 numeric check |
| **Success** | mr_005 score >= 1.0; evidence tier recorded |
| **Failure** | Incorrect result; formal-proof claim without compiler evidence |
| **Metrics** | case_score, verification_invoked, time_ms |
| **Human review** | Confirm auto-grade; flag formal-proof claims |
| **Evidence tier** | measured |
| **Note** | Validates computation, not written proof artifact |

### t1_euler_identity

| Field | Value |
|-------|-------|
| **Objective** | Numerically verify e^(iπ) + 1 ≈ 0 |
| **Domain** | mathematics |
| **Difficulty** | undergraduate |
| **Required capabilities** | mathematical_reasoning |
| **Required tools** | scep_benchmarks |
| **Verification** | SCEP mr_008 tolerance check |
| **Success** | mr_008 score >= 1.0 |
| **Failure** | Error exceeds 0.01 |
| **Metrics** | case_score, numeric_error |
| **Human review** | Check tolerance bound |
| **Evidence tier** | measured |

### t1_proof_verification_basics

| Field | Value |
|-------|-------|
| **Objective** | Run proof-verification cases with honest evidence tier |
| **Domain** | mathematics |
| **Difficulty** | undergraduate |
| **Required capabilities** | proof_verification |
| **Required tools** | scep_benchmarks, smt_gateway, lean_exporter |
| **Verification** | SCEP pv_001–pv_003 |
| **Success** | >= 2/3 pass; evidence tier not mislabeled |
| **Failure** | < 2/3 pass; simulated labeled as proven |
| **Metrics** | pass_rate, evidence_tier_accuracy |
| **Human review** | Audit evidence tier labels |
| **Evidence tier** | simulated (when compilers absent) |

### t1_theorem_reproduction_zeta

| Field | Value |
|-------|-------|
| **Objective** | Numerically reproduce ζ(2) = π²/6 |
| **Domain** | mathematics |
| **Difficulty** | graduate |
| **Required capabilities** | mathematical_reasoning, knowledge_quality |
| **Required tools** | scep_benchmarks |
| **Verification** | SCEP mr_010 |
| **Success** | mr_010 score >= 1.0 |
| **Failure** | Error exceeds 0.01 |
| **Metrics** | case_score, numeric_error |
| **Human review** | Confirm numerical method documented |
| **Evidence tier** | measured |

---

## Tier 2 — Research Paper Reproduction

Methodology replication. Requires workflow execution and human review.

### t2_workflow_demo_reproduction

| Field | Value |
|-------|-------|
| **Objective** | Execute GNN paper research workflow demo |
| **Domain** | computer_science |
| **Difficulty** | graduate |
| **Required capabilities** | research_planning, literature_synthesis, research_productivity |
| **Required tools** | workflow_engine, workflow_workers |
| **Verification** | Workflow completion + artifact checklist |
| **Success** | Workflow completes; research note and report produced |
| **Failure** | Workflow failure; missing artifacts |
| **Metrics** | workflow_completion_rate, artifact_count, duration_s |
| **Human review** | Inspect artifact quality and traceability |
| **Evidence tier** | baseline |

### t2_literature_synthesis_bench

| Field | Value |
|-------|-------|
| **Objective** | Score literature synthesis on SCEP benchmarks |
| **Domain** | research |
| **Difficulty** | graduate |
| **Required capabilities** | literature_synthesis |
| **Required tools** | scep_benchmarks, retrieval_engine |
| **Verification** | SCEP literature_synthesis pass rate |
| **Success** | Score >= 0.5 |
| **Failure** | Score < 0.5 |
| **Metrics** | dimension_score, pass_rate |
| **Human review** | Sample outputs for factual accuracy |
| **Evidence tier** | baseline |

---

## Tier 3 — Small Open Research Questions

Bounded novelty. Heuristic scoring with human domain review.

### t3_open_problem_decomposition

| Field | Value |
|-------|-------|
| **Objective** | Decompose bounded open problem into testable sub-questions |
| **Domain** | mathematics |
| **Difficulty** | research |
| **Required capabilities** | research_planning, conjecture_generation, reasoning |
| **Required tools** | hypothesis_engine, scep_benchmarks, working_memory |
| **Verification** | SCEP rp benchmarks; >= 2 competing hypotheses |
| **Success** | >= 2 hypotheses; plan with success criteria; rp score >= 0.4 |
| **Failure** | Single hypothesis; no weaknesses documented |
| **Metrics** | hypothesis_count, plan_completeness, rp_score |
| **Human review** | Domain reviewer evaluates falsifiability |
| **Evidence tier** | heuristic |

### t3_conjecture_novelty

| Field | Value |
|-------|-------|
| **Objective** | Generate novel conjectures; score on SCEP benchmarks |
| **Domain** | mathematics |
| **Difficulty** | research |
| **Required capabilities** | conjecture_generation |
| **Required tools** | mip_conjecture, hypothesis_engine, scep_benchmarks |
| **Verification** | SCEP conjecture_generation score |
| **Success** | cg score >= 0.3 |
| **Failure** | cg < 0.3; duplicate without attribution |
| **Metrics** | cg_score, novelty_estimate |
| **Human review** | Check non-triviality and scope |
| **Evidence tier** | heuristic |

---

## Tier 4 — Domain Grand Challenges

Multi-year scientific campaigns. Composite capability + checkpoint discipline.

### t4_multi_domain_capability

| Field | Value |
|-------|-------|
| **Objective** | Sustain measured capability across >= 6 SCEP dimensions for 30 days |
| **Domain** | cross_domain |
| **Difficulty** | research |
| **Required capabilities** | 6+ SCEP dimensions |
| **Required tools** | scep_benchmarks, eval_api, workflow_engine, checkpoint_store |
| **Verification** | Composite >= 0.6; no regression > 0.1 |
| **Success** | Composite >= 0.6; 30-day checkpoint trail |
| **Failure** | Composite < 0.6; unexplained regression |
| **Metrics** | composite_score, dimension_coverage, regression_delta |
| **Human review** | Monthly capability review |
| **Evidence tier** | measured |

### t4_long_running_autonomous

| Field | Value |
|-------|-------|
| **Objective** | 72-hour campaign with checkpoint recovery |
| **Domain** | research |
| **Difficulty** | research |
| **Required capabilities** | research_planning, research_productivity, recovery_from_failure |
| **Required tools** | workflow_engine, checkpoint_store, working_memory |
| **Verification** | >= 3 checkpoints; continuous journal |
| **Success** | Checkpoints saved; recovery from simulated failure |
| **Failure** | Data loss; journal gaps > 24h |
| **Metrics** | checkpoint_count, journal_completeness, recovery_success |
| **Human review** | Weekly journal and evidence review |
| **Evidence tier** | baseline |

---

## Tier 5 — Frontier Open Problems

Organizational capability tests. **Does not solve prize problems.**

### t5_prize_readiness_assessment

| Field | Value |
|-------|-------|
| **Objective** | Measure readiness against prize prerequisites; NO solution attempt |
| **Domain** | prize_track |
| **Difficulty** | frontier |
| **Required capabilities** | 5+ SCEP dimensions |
| **Required tools** | prize_readiness_scorer, scep_benchmarks, knowledge_graph |
| **Verification** | Readiness report with explicit gaps |
| **Success** | Report generated; gaps listed; no prize claims |
| **Failure** | Unsupported prize progress claim |
| **Metrics** | readiness_score, gap_count, weakest_dimension |
| **Human review** | **Mandatory** human authorization before activation |
| **Evidence tier** | baseline |

### t5_frontier_benchmark_participation

| Field | Value |
|-------|-------|
| **Objective** | Participate in external frontier benchmarks with provenance |
| **Domain** | cross_domain |
| **Difficulty** | frontier |
| **Required capabilities** | mathematical_reasoning, reasoning, verification |
| **Required tools** | eval_api, provenance_records |
| **Verification** | External score with provenance envelope |
| **Success** | Provenance complete; limitations documented |
| **Failure** | Missing provenance; score inflation |
| **Metrics** | external_score, provenance_completeness |
| **Human review** | Human authorizes participation and reviews public results |
| **Evidence tier** | unavailable (no external benchmark integrated) |

---

## Registry Summary

| Tier | Challenges | Primary Evidence | Automation Level |
|------|-----------|----------------|------------------|
| 0 | 3 | measured | Full auto-grade |
| 1 | 4 | measured/simulated | Auto-grade + human audit |
| 2 | 2 | baseline | Workflow + human review |
| 3 | 2 | heuristic | Human domain review |
| 4 | 2 | measured/baseline | Campaign discipline + human review |
| 5 | 2 | baseline/unavailable | Human authorization required |
