# AXIOM Observability

Guide for contributors working on logging, metrics, and debugging.

---

## Logging

### Configuration

| Variable | Values | Default |
|----------|--------|---------|
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR | INFO |
| `LOG_FORMAT` | `json`, `console` | json (prod), console (dev) |

Set in `.env` or CI (`LOG_FORMAT=console` for readable test output).

### Usage

```python
from axiom.observability.logger import get_logger

logger = get_logger(__name__)
logger.info("Document uploaded", project_id=project_id, chars=char_count)
```

`configure_logging()` is called once at API startup in `axiom/services/api_gateway/main.py`.

### JSON log fields

Each line includes: `timestamp`, `level`, `logger`, `message`, plus any extra keys passed via logging `extra={}`.

### Local development

```bash
LOG_FORMAT=console LOG_LEVEL=DEBUG make dev
```

---

## Metrics

### Endpoint

`GET /metrics` — Prometheus text exposition format.

### Usage in code

```python
from axiom.observability.metrics import METRICS

METRICS.api_requests_total.inc(method="GET", endpoint="/health", status="200")
with METRICS.api_request_duration.time():
    ...
```

### Available metrics

| Metric | Type | Labels |
|--------|------|--------|
| `axiom_api_requests_total` | counter | method, endpoint, status |
| `axiom_api_request_duration_seconds` | histogram | — |
| `axiom_papers_ingested_total` | counter | — |
| `axiom_graph_nodes_total` | counter | node_type |
| `axiom_smt_checks_total` | counter | result |
| `axiom_hypotheses_generated_total` | counter | strategy |

### Local Prometheus

```bash
make docker-up
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/axiom-admin)
```

Note: `deploy/grafana/provisioning/` may be incomplete — see `MASTER_PROGRESS.md`.

---

## Debugging Tips

1. **API errors:** Check uvicorn stdout; enable `LOG_LEVEL=DEBUG`
2. **Test failures:** Run single test with `-v --tb=long`
3. **DB state:** `make db-status` for knowledge graph migrations
4. **Health:** `curl http://localhost:8000/health`

---

## Contributor Checklist

When adding a new subsystem:

- [ ] Use `get_logger(__name__)` — not `print()`
- [ ] Log errors with context (ids, not secrets)
- [ ] Add a counter or histogram if the path is performance-critical
- [ ] Do not log JWT tokens, passwords, or full PDF content
