# Knowledge Acquisition Status

**Version:** 1.0  
**Status:** Operational

## Capabilities

| Capability | Status |
|------------|--------|
| Multi-channel source acquisition | ✅ |
| Full provenance tracking | ✅ |
| Source quality tiers | ✅ |
| LaTeX/text structure extraction | ✅ |
| Scientific knowledge graph (SKAI store) | ✅ |
| EGS bridge | ✅ |
| E&R bridge | ✅ |
| Citation graph | ✅ (key-based) |
| Conflict detection | ✅ |
| Research gap detection | ✅ |
| Literature saturation estimate | ✅ |
| Research question expansion | ✅ |
| Reasoning-aware retrieval | ✅ |
| Knowledge versioning | ✅ |
| Scope isolation | ✅ |
| FRCE literature integration | ✅ |

## API

Prefix: `/skai/*`

## Verification

```bash
make skai-health
cd /tmp && pytest /workspace/tests/test_skai_knowledge.py -q
```

## Known limitations (v1)

- arXiv network ingest not wired through SKAI orchestrator (use legacy `/ingest` or text acquire)
- BibTeX citation keys not resolved to paper nodes
- Cross-domain structural similarity detection is stub
- Knowledge compression hierarchy defined but not fully automated
