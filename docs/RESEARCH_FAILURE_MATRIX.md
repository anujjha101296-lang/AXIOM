# Research Failure Matrix

| Failure | Frequency | Severity | User Impact | Root Cause | Component | Reproducibility | Current Mitigation | Proposed Fix | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ModelGatewayClient ImportError** | 100% | Critical | Blocks all LLM logic | Bad import or syntax error in `axiom/services/model_gateway/client.py` | ModelGateway | 100% | None | Fix syntax / import in client.py | P0 |
| **VectorStore Async Coupling** | High | High | Fails sync workers | `VectorStore.search` requires `AsyncSession` | Retrieval | 100% | Use mock data | Refactor `VectorStore` to support sync db / agnostic backend | P1 |
| **SmtGateway Mock Silencing** | High | High | Hallucinates proofs | `SmtGateway` uses `pass` and mock strings | Verification | 100% | Human review | Implement actual `z3` subprocess checks or remove mock | P1 |
