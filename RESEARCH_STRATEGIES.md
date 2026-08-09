# Research Strategies

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Strategy types

| Strategy | Description |
|----------|-------------|
| `literature_first` | Survey prior work before reasoning |
| `formal_mathematics` | Symbolic + SMT + Lean path |
| `computational_exploration` | Numerical experimentation |
| `analogy` | Map to known theorems (planned) |
| `counterexample_search` | Attack claims with counterexamples |
| `hybrid` | Combine literature, computation, verification |
| `single_model` | Single-model reasoning |
| `multi_model` | Independent multi-model consensus |
| `ensemble` | LLM + symbolic + verifier (planned) |

## Selection

- Generate ≥5 candidate strategies per problem
- Score by problem fit, evidence, cost, verification difficulty
- Select multiple strategies when uncertainty > 0.55

## API

```bash
GET /routing/strategies?statement=...
POST /routing/compile
```

## A/B research

Controlled strategy comparison is planned (SIMR §29). v1 records routing decisions for later correlation.

## Refresh

```bash
make simr-health
```
