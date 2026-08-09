# AXIOM Target Architecture

**Version:** 1.0 (verified against repository 2026-08-09)

## Layered Structure

```text
                         AXIOM
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       PRODUCT         RESEARCH OS       SECURITY (TSS)
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
 KNOWLEDGE (SKAI)     REASONING (SIMR)      EXPERIMENTS (SEC)
    │                      │                      │
    └──────────────────────┼──────────────────────┘
                           ▼
                  CAMPAIGN ENGINE (FRCE)
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    WORKFLOW          FORMAL (FMTP)     EVIDENCE (E&R)
    (multi-agent)                         │
         │                 │              ▼
         └─────────────────┴──────► VERIFICATION
                                           │
                                           ▼
                                    GLOBAL MEMORY
                                           ↺
```

## Component Responsibilities

| Component | Package | Responsibility | Status |
|-----------|---------|----------------|--------|
| API Gateway | `services/api_gateway/` | HTTP entry, auth, routing | PARTIAL |
| Research Workspace | `axiom/research/` | PDFs, notes, Q&A | FULL |
| Research Kernel | `axiom/research_kernel/` (branch) | Unified execution | NOT MERGED |
| Campaign Engine | `axiom/campaign/` | Long-running missions | PARTIAL |
| Knowledge System | `axiom/skai/` + EGS | Acquisition, graph | PARTIAL |
| Memory | FRCE + E&R + EGS | Institutional memory | PARTIAL |
| Reasoning | `axiom/routing/` + core | Model/tool selection | FULL |
| Planning | FRCE + SIMR compiler | Strategy generation | PARTIAL |
| Multi-Agent | `axiom/workflow/` | Task orchestration | PARTIAL |
| Model Router | `axiom/routing/` | SIMR | FULL |
| Experiment Runtime | `axiom/experiment/` | SEC sandbox | FULL |
| Formal Math | `axiom/formal_math/` | FMTP | PARTIAL |
| Evidence | `axiom/evidence/` | E&R provenance | FULL |
| Verification | core + FMTP | Truthfulness guards | PARTIAL |
| Benchmarking | `axiom/evaluation/` | SCEP | PARTIAL |
| Security | `axiom/security/` | TSS | PARTIAL |
| Observability | `axiom/observability/` | Metrics, provenance | PARTIAL |
| GCP | `axiom/grand_challenge/` | Challenge ladder | PARTIAL |

## Dependency Graph

```text
Frontend (ui/)
    ↓ requires
API Gateway (main.py)
    ↓
┌───┴───┬────────┬────────┬────────┐
▼       ▼        ▼        ▼        ▼
Research FRCE    SKAI    Workflow  GCP
    ↓       ↓        ↓        ↓
    └── SIMR ──┬── SEC ──┬── FMTP
               ↓         ↓
              E&R ←── Provenance
               ↓
            EGS (knowledge graph)
```

**Build order rule:** Never build UI for a capability before its API is tested.

## Reuse Policy

Do NOT duplicate:
- Campaign storage (use FRCE, not new campaign tables)
- Claim registry (use E&R, not parallel claim stores)
- Graph storage (bridge to EGS via SKAI, don't fork)
- Experiment execution (use SEC, never in-app exec)

## Next Architecture Additions

1. **Discovery & Hypothesis Engine** — consumes SKAI gaps → generates testable hypotheses
2. **Unified search facade** — SKAI retrieval + research FTS + EGS query
3. **Research Kernel merge** — TD-005 branch integration
