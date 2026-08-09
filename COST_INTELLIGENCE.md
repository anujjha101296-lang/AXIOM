# Cost Intelligence

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Tracked metrics

| Metric | Storage |
|--------|---------|
| Tokens | `simr_costs` table |
| Model calls | `simr_costs` table |
| Tool calls | `simr_costs` table |
| Compute seconds | `simr_costs` table |
| Estimated USD | `simr_costs` table |

## Per-decision estimates

Each routing decision includes `cost_estimate` based on model cost-per-token and strategy estimate.

## Campaign metrics (planned)

- Cost per successful result
- Cost per verified result
- Cost per research iteration

## API

```bash
POST /routing/costs
GET /routing/dashboard
```

## Policy

Do not optimize cost at the expense of scientific reliability.

## Refresh

```bash
make simr-health
```
