# AXIOM Cognitive Architecture (ACA)

**Status:** Implemented  
**Package:** `axiom/cognitive/`

## Core principle

**Models are interchangeable. The cognitive architecture is permanent.**

ACA separates: Knowledge, Reasoning, Memory, Planning, Verification, Execution, Learning, Reflection.

## Nine cognitive layers

| Layer | Pillar | Delegates to |
|-------|--------|--------------|
| 1. Perception | Knowledge | `arxiv_parser`, `pdf_extractor` |
| 2. Understanding | Knowledge | `EpistemicStore`, `semantic_tracker` |
| 3. Memory | Memory | `WorkingMemory`, `SMEStore` |
| 4. Reasoning | Reasoning | `HypothesisEngine`, `MctsSolver` |
| 5. Planning | Planning | `WorkflowScheduler`, MIP strategy |
| 6. Execution | Execution | `ParallelExecutor`, `ModelClient` |
| 7. Verification | Verification | `truthfulness`, `SmtGateway` |
| 8. Learning | Learning | `SelfImprovementLoop`, SME phases |
| 9. Reflection | Reflection | `EngineeringReview`, evidence framework |

## Model providers

```python
from axiom.cognitive.model_provider import register_provider, get_model_provider

# Swap providers without changing ACA
provider = get_model_provider("heuristic")  # or "default" (ModelClient)
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /aca/architecture` | Full manifest with subsystem mappings |
| `GET /aca/layers` | List 9 layers |
| `GET /aca/providers` | Available model providers |
| `POST /aca/cycles` | Create cognitive cycle |
| `POST /aca/cycles/{id}/run` | Execute all 9 layers |
| `POST /aca/cycles/{id}/layers` | Execute single layer |

## Relationship to SME

- **ACA** = how AXIOM thinks (permanent cognitive model, model-agnostic)
- **SME** = how AXIOM researches (10-phase scientific method, mandatory for workflows)
- Link via `sme_session_id` on cognitive cycles

## Benchmark

```bash
make aca-benchmark
# Writes aca_benchmark_results.json
```

## Tests

```bash
pytest tests/test_cognitive_architecture.py -v
```
