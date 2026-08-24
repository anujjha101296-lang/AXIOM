# AXIOM v0.1 — Founder Release & Architecture Specification

## 1. Overview
AXIOM v0.1 (**Founder Release**) is an autonomous scientific research and formal verification platform. It integrates:
- **Phase 10**: Controlled External Research & Security Infrastructure
- **Phase 11**: Document Intelligence & Semantic Retrieval Engine
- **Phase 12**: Controlled Source Provenance & External Research
- **Phase 13**: Scientific Knowledge Graph & Claim Graph
- **Phase 14**: Hypothesis & Scientific Reasoning Engine
- **Phase 15**: Computational Experiment & Verification Engine
- **Phase 16**: Formal Mathematics & Proof Verification Engine (Lean 4 / SMT Z3)

---

## 2. Multi-Tenant Security & Isolation
- **RBAC & Token Authentication**: JWT Bearer Tokens with signature validation.
- **Project Isolation**: Foreign key ownership validation across all endpoints (`403 Forbidden` on unauthorized project access).
- **Sandbox Security**: AST code validation + `sys.settrace()` runtime limit enforcement (wall-clock timeout, memory allocation limit, output truncation, prohibited modules).

---

## 3. Production Deployment Architecture
- **API Gateway**: FastAPI (`http://localhost:8000`)
- **Frontend UI**: Next.js 16 Web Application (`http://localhost:3000`)
- **Database & Migrations**: SQLite / PostgreSQL with Alembic Migrations (`alembic upgrade head`)
- **Docker Stack**: `docker-compose up --build -d`

---

## 4. Python Client SDK
Available in `sdk/axiom_client.py`:
```python
from sdk.axiom_client import AxiomClient

client = AxiomClient(base_url="http://localhost:8000", token="axiom-dev-token")
client.create_project("Quantum Gravity")
client.formalize_claim("proj-id", "n + 0 = n")
```
