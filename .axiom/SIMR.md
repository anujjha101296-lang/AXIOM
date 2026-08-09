# Scientific Intelligence & Model Routing Loop (SIMR)

AXIOM continuously selects, evaluates, combines, and improves the models, tools, knowledge sources, reasoning strategies, and verification systems used for scientific research.

## Mission

Use the right reasoning system for the right problem — not assume one AI model is sufficient.

## Continuous loop

```text
RESEARCH PROBLEM → PROFILE → IDENTIFY CAPABILITIES → SELECT MODELS
  → SELECT TOOLS → GENERATE STRATEGIES → SELECT STRATEGIES → EXECUTE
  → VERIFY → MEASURE → UPDATE PERFORMANCE → UPDATE ROUTING
  → UPDATE FAILURE MEMORY → UPDATE BENCHMARKS → REPEAT
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `MODEL_REGISTRY.md` | Model catalog posture |
| `TOOL_REGISTRY.md` | Scientific tool catalog |
| `CAPABILITY_GRAPH.md` | Problem → capability → model/tool mapping |
| `MODEL_BENCHMARKS.md` | Benchmark integration status |
| `ROUTING_POLICY.md` | Routing rules and constraints |
| `MODEL_FAILURE_MEMORY.md` | Failure tracking posture |
| `RESEARCH_STRATEGIES.md` | Strategy types and selection |
| `COST_INTELLIGENCE.md` | Cost tracking posture |
| `scripts/simr_health_check.py` | Automated SIMR gate |

## Code modules

- `axiom/routing/models.py` — domain models
- `axiom/routing/model_registry.py` — model catalog
- `axiom/routing/tool_registry.py` — tool catalog
- `axiom/routing/capability_graph.py` — capability resolution
- `axiom/routing/profiler.py` — problem profiling
- `axiom/routing/selector.py` — model router
- `axiom/routing/strategies.py` — strategy generation/selection
- `axiom/routing/failure_memory.py` — failure profiles
- `axiom/routing/store.py` — routing decisions and costs
- `axiom/routing/compiler.py` — research compiler
- `axiom/routing/context.py` — context management
- `axiom/services/api_gateway/routes/routing_api.py` — `/routing/*` API

## API surface

| Endpoint | Purpose |
|----------|---------|
| `GET /routing/models` | List model registry |
| `GET /routing/tools` | List tool registry |
| `POST /routing/profile` | Profile a research problem |
| `POST /routing/select` | Route to model/tools/strategy |
| `POST /routing/compile` | Compile research execution plan |
| `GET /routing/strategies` | List candidate strategies |
| `GET /routing/dashboard` | Routing dashboard |
| `POST /routing/failures` | Record model failure |
| `POST /routing/conflicts` | Record knowledge conflict |

## Constraints

- Do NOT assume model superiority without benchmark evidence
- Do NOT treat model agreement as proof
- Do NOT silently change models on failure — record fallback
- Do NOT optimize cost at the expense of scientific reliability
- Speculative memories must not silently become verified facts

## Production requirements

```bash
REQUIRE_AUTH_FOR_ROUTING_ROUTES=true
```

## Relationship to other loops

- **SCEP/EPIC-002** — capability dimensions drive routing
- **H1-OBS** — provenance for routed runs
- **E&R** — evidence gate for discovery claims
- **TSS** — tool risk classification
- **GCP** — campaign capability requirements
