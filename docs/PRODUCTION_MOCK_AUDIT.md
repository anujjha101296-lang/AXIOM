# Production Mock Audit

This document records all remaining occurrences of 'Mock', 'Fake', or 'Dummy' patterns in the repository, explicitly classifying their safety and enforcement status in the production runtime.

## Found Occurrences

### 1. `MockEmbeddingProvider` (axiom/research/embeddings.py)
- **Status**: SAFE / GATED.
- **Classification**: TEST ONLY.
- **Enforcement**: Code explicitly checks `if os.getenv("ENVIRONMENT").lower() == "production": raise EmbeddingConfigurationError()`. Production cannot execute this path.

### 2. `MockLLMProvider` (axiom/research/llm.py)
- **Status**: SAFE / GATED.
- **Classification**: TEST ONLY / DEVELOPMENT ONLY.
- **Enforcement**: Explicit hard-fail check in the factory (`get_llm_provider()`) throws `ProviderConfigurationError` if `ENVIRONMENT="production"` without an explicit API key. The mock itself also natively throws a configuration error if somehow called during production.

### 3. `Mock Answer grounded for [question]` (axiom/research/agent/tools.py)
- **Status**: RESOLVED (REMOVED).
- **Classification**: DEAD CODE.
- **Enforcement**: Removed from the production branch. The method `ask_grounded_research_engine_handler` now explicitly imports and invokes the actual LLM `generate()` payload on valid source evidence.

### 4. `Mock authorization check` (axiom/research/agent/tools.py)
- **Status**: SAFE / GATED.
- **Classification**: TEST ONLY.
- **Enforcement**: A testing branch logic block that was rewritten to assert `if ENVIRONMENT=="production": raise RuntimeError()` to aggressively block any mock assumptions in live deployment.

## Production Rule
**NO MOCKS EXECUTED IN PRODUCTION.**
If the production deployment lacks `OPENAI_API_KEY` or `GEMINI_API_KEY`, the application will explicitly throw a 500 Server Error (`ProviderConfigurationError` or `EmbeddingConfigurationError`) instead of silently fabricating results.
