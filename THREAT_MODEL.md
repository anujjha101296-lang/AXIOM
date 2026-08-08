# Threat Model

**Last updated:** 2026-08-08  
**Status:** Living document

## Assets

| Asset | Sensitivity | Trust level |
|-------|-------------|-------------|
| SQLite databases (`axiom.db`) | Internal | Application-trusted |
| Research PDFs / notes | Confidential research | **Untrusted until validated** |
| API bearer tokens / JWT | Credential/secret | Highly sensitive |
| SCEP benchmark results | Internal | Measured with evidence tier |
| LLM prompts (Paper Q&A) | Confidential | Must not leak to logs |
| Docker images | Internal | Supply-chain monitored |

## Trust boundaries

```text
User/Browser → Frontend (Next.js) → API Gateway → Backend services → SQLite
                                      ↓
                              External LLM providers (untrusted egress)
                                      ↓
                              Research PDFs (untrusted input)
```

Treat all externally supplied content (PDFs, arXiv, retrieved text, model output) as **untrusted** until validated.

## Threat categories

### Application (current exposure)

| Threat | Likelihood | Impact | Mitigation status |
|--------|------------|--------|-------------------|
| Unauthenticated `/eval/run` abuse (DoS) | Medium | Medium | Optional auth flag; enable in production |
| Unauthenticated `/gcp` campaign mutation | Low | Medium | Optional auth flag |
| Bearer token brute force | Low | High | Strong token required in production |
| Default dev credentials in production | Medium | Critical | `enforce_production_security()` blocks startup |

### Document / prompt injection

| Threat | Likelihood | Impact | Mitigation status |
|--------|------------|--------|-------------------|
| Malicious PDF instructions | Medium | High | Content wrapping + pattern detection (heuristic) |
| Retrieved-content injection | Medium | High | `TrustContentClass` separation; full pipeline integration pending |

### Agent / autonomy (future)

| Threat | Likelihood | Impact | Mitigation status |
|--------|------------|--------|-------------------|
| Unrestricted shell/network | N/A today | Critical | `ToolRiskClass` + explicit authorization required |
| Runaway research loops | Low | Medium | Budget/iteration limits not yet enforced |

### Supply chain

| Threat | Likelihood | Impact | Mitigation status |
|--------|------------|--------|-------------------|
| Vulnerable Python deps | Medium | High | `pip-audit` CI workflow |
| Compromised base image | Low | High | Pinned `python:3.11-slim`; scanning recommended |

## Out of scope (not deployed)

Kubernetes, Redis, message queues, multi-tenant row isolation — documented when introduced.

## Review cadence

Update after each TSS cycle or material architecture change.
