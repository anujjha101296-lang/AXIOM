# AXIOM Honest Limitations

This document explicitly documents the known limitations of AXIOM's
evaluation platform and capability claims. We do not hide limitations.

## Phase 8 Evaluation Platform Limitations

### Benchmark Dataset Size
- The current benchmark datasets are **small and deterministic by design**.
- `retrieval_corpus.json`: 3 documents, 6 chunks, 5 queries.
- `grounding_cases.json`: 5 cases.
- `agent_tasks.json`: 7 controlled tasks.
- Small datasets allow full reproducibility but **cannot prove generalization**.
- Good benchmark scores on these datasets do not prove real-world performance.

### Retrieval Benchmark
- **Uses TF-IDF similarity, not the production embedding model.**
  The production system uses neural embeddings (e.g., OpenAI text-embedding-ada-002).
  TF-IDF scores will differ from embedding-based retrieval scores.
- Results are deterministic but **do not represent production retrieval quality**.
- The corpus contains only English text. Non-English queries are not tested.
- No evaluation on adversarial queries (queries designed to confuse retrieval).
- No evaluation on very long documents or very short chunks.

### Grounding Benchmark
- **Uses a rule-based mock QA system**, NOT the real AXIOM LLM.
  The mock returns deterministic rule-based answers, not actual LLM outputs.
- Real LLM hallucination rates on the same grounding cases are **not measured**.
- Citation validity is measured for mock outputs only.
- The 5 grounding cases cannot cover all types of evidence scenarios.
- "Contradiction detection" is rule-based (keyword matching), not semantic.

### Research Agent Benchmark
- **Uses state machine simulation, NOT live agent execution.**
  The benchmark exercises the agent state machine logic, not the full
  engine with a real LLM and real database.
- Budget enforcement is verified at the simulation level.
  Real-world timing (MAX_RUNTIME_SECONDS) is NOT measured.
- Async cancellation race conditions are NOT tested.
- The 7 tasks cover basic scenarios. Complex multi-step research tasks
  are not included.
- Tool call results are simulated, not real tool invocations.

### Regression Detection
- Regression tolerance is set at **5%** by default.
  This may be too lenient for safety-critical capabilities.
- Regression detection only covers **quantitative metrics** (pass rate).
  Qualitative regressions (e.g., answer style, verbosity) are not detected.
- The baseline must be established manually with `--save-baseline`.
  There is no automated baseline management.

## AXIOM Capability Claim Limitations

### Document Retrieval (cap_001)
- Benchmarked on a 6-chunk deterministic corpus.
- Production retrieval uses neural embeddings — benchmark uses TF-IDF.
- No evaluation on adversarial queries or out-of-distribution topics.
- Retrieval quality depends on chunk size and overlap configuration.

### Evidence-Backed Q&A (cap_002)
- Answer quality depends on LLM provider and configuration.
- Citation validity rate not yet measured in production traffic.
- Benchmark uses mock QA; real LLM grounding is not benchmarked.
- Evaluated on 5 controlled grounding cases only.

### Insufficient Evidence Detection (cap_003)
- Measured only in rule-based mock QA system, not real LLM.
- Benchmark does not cover all uncertainty scenarios.
- LLM hallucination on absent topics is not fully evaluated.

### Contradiction Detection (cap_004)
- Only 1 contradiction case in current benchmark.
- Detection is rule-based in mock QA, not LLM semantic reasoning.
- Real contradiction detection quality depends on LLM reasoning.

### Agent Budget Enforcement (cap_005)
- Tested via state machine simulation only.
- Real-world timing measurements (MAX_RUNTIME_SECONDS) not included.
- Does not test preemptive cancellation of in-flight LLM calls.

### Agent Safe Cancellation (cap_006)
- Cancellation tested via state machine simulation only.
- Does not cover concurrent cancellation races in async execution.
- Requires manual verification in live system.

### Agent Tool Allowlist (cap_007)
- Tool allowlist enforcement tested at state machine level only.
- Jailbreak resistance not evaluated.
- Prompt injection defense not benchmarked in Phase 8.

### Regression Detection (cap_008)
- Requires at least one prior baseline run.
- Tolerance may be too lenient for critical capabilities.
- Does not capture qualitative regressions.

## What Good Benchmark Scores Do NOT Prove

1. **Good retrieval metrics do NOT guarantee factual correctness.**
   A system can retrieve the right chunks but still generate hallucinated answers.

2. **Agent task completion does NOT prove autonomous scientific discovery.**
   The 7 benchmark tasks are controlled scenarios with known expected behaviors.

3. **Benchmark performance does NOT prove general intelligence.**
   AXIOM is a document research assistant, not a general-purpose AI.

4. **High citation validity rate does NOT prove semantic correctness.**
   A citation can be formally valid (chunk exists, was retrieved) but
   still used in a misleading or incorrect context.

5. **Passing regression tests does NOT mean no regressions occurred.**
   The regression detector only covers measured metrics.
   Unmeasured capabilities can regress without detection.

## Future Measurement Priorities

1. Real LLM grounding evaluation (using actual production QA system).
2. Production embedding-based retrieval benchmark.
3. Async runtime budget enforcement measurement.
4. Larger, more diverse benchmark datasets.
5. Red team evaluation (adversarial queries, prompt injection).
6. Cross-user isolation measurement.
7. Performance benchmarks (latency, throughput).
