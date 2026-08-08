# Scientific Method Engine (SME)

**Status:** Implemented  
**Package:** `axiom/scientific_method/`

## Purpose

The Scientific Method Engine governs every autonomous research task through 10 mandatory phases. No research workflow may bypass SME — workflow creation requires a completed SME session.

## Mandatory phases

| # | Phase | Output |
|---|-------|--------|
| 1 | Problem Definition | Question, assumptions, success criteria, constraints |
| 2 | Knowledge Acquisition | Tracked sources (literature, proofs, datasets, failures) |
| 3 | Knowledge Graph Construction | Definitions, theorems, dependencies, unknowns |
| 4 | Hypothesis Generation | ≥2 competing hypotheses with reasoning, evidence, weaknesses, confidence |
| 5 | Criticism | Independent critic attacks per hypothesis |
| 6 | Experimentation | Discriminating experiment designs per domain |
| 7 | Verification | Claims classified: verified, supported, speculative, rejected, unknown |
| 8 | Reflection | Learnings, failures, assumption changes, new questions |
| 9 | Research Memory | Failed/successful strategies, insights, journal, decisions |
| 10 | Human Review | Research notebook, evidence graph, timeline, open questions |

## API

| Endpoint | Description |
|----------|-------------|
| `GET /sme/phases` | List mandatory phases |
| `POST /sme/sessions` | Create research session |
| `POST /sme/sessions/{id}/run` | Execute full 10-phase cycle |
| `POST /sme/sessions/{id}/phases` | Execute single phase |
| `GET /sme/sessions/{id}/notebook` | Human review package |
| `POST /sme/validate-gate` | Validate workflow gate |
| `POST /workflows` | Requires `sme_session_id` (completed SME) |

## Usage

```bash
# 1. Create SME session
curl -X POST http://localhost:8000/sme/sessions \
  -H "Content-Type: application/json" \
  -d '{"objective":"Test prime gaps","domain":"mathematics"}'

# 2. Run full scientific method cycle
curl -X POST http://localhost:8000/sme/sessions/{id}/run

# 3. Create workflow (blocked without completed SME)
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{"objective":"...","domain":"research","sme_session_id":"{id}"}'
```

## Benchmark

```bash
make sme-benchmark
# Writes sme_benchmark_results.json
```

## Integration

- **Epistemic Graph:** Knowledge acquisition and graph construction
- **HypothesisEngine:** Competing hypothesis generation
- **TheoremRetrievalEngine:** Literature/formal source retrieval
- **Truthfulness layer:** Verification classification
- **H1-OBS provenance:** SME completion recorded as `run_type=sme`
- **Workflow engine:** Gated via `sme_session_id` requirement

## Tests

```bash
pytest tests/test_scientific_method_engine.py -v
```
