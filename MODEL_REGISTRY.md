# Model Registry

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Registered models

| Model ID | Provider | Capabilities | Availability |
|----------|----------|--------------|--------------|
| `mock-model` | axiom | Offline testing, summarization | Always available |
| `gpt-4o-mini` | openai | General, coding, math, literature | Requires `OPENAI_API_KEY` |
| `gpt-4o` | openai | General, long context, coding | Requires `OPENAI_API_KEY` |
| `gemini-1.5-flash` | google | Long context, general | Requires `GEMINI_API_KEY` |
| `gemini-pro` | google | General, literature | Requires `GEMINI_API_KEY` |

## Tracked attributes

Each model records: capabilities, context window, modalities, tool support, structured output, cost, latency, limitations, reliability score, benchmark scores, and license notes.

## API

```bash
GET /routing/models
GET /routing/models/{model_id}
```

## Policy

No hard-coded model superiority — selection uses capability benchmark scores and failure memory.

## Refresh

```bash
make simr-health
```
