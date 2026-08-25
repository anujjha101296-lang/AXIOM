# AXIOM Unit Economics & Cost Control

**Goal**: Model actual infrastructure costs against proposed SaaS tiers to ensure a sustainable margin, preventing runaway inference or compute debt.

## 1. Measured Infrastructure Costs

### Compute (API / Worker)
- **FastAPI Core**: Minimal. Render/Fly.io base instances scale easily. (~$10/mo per instance)
- **Z3 SMT Solver Subprocess**: Very CPU-bursty. Average theorem takes ~0.4s to compile and solve. Hard bounds must be placed on execution time (e.g. max 5s timeout) to prevent halting problem scenarios draining CPU credits.

### Storage (Knowledge Graph & VectorStore)
- **SQLite Database**: Ephemeral/Attached Volumes. Very cheap.
- **Documents**: Highly dense text requires storage; but limit is primarily token-based embedding size.

### LLM Inference (The Primary Cost Driver)
- **Gemini 1.5 Flash**: ~$0.075 / 1M input tokens, ~$0.30 / 1M output tokens.
- **GPT-4o Mini**: ~$0.150 / 1M input tokens, ~$0.60 / 1M output tokens.
*Average Research Mission (10 iterative hypothesis loops)*: ~20k input tokens, ~5k output tokens.
*Cost per Research Mission*: ~$0.003 - $0.006 (Extremely low due to deterministic tooling offload).

## 2. Product Tiers (Estimated Cost vs Revenue)

- **FREE / TRIAL**: 5 missions/mo. Estimated cost: $0.03/user.
- **PRO ($20/mo)**: 50 missions/mo. Estimated LLM cost: $0.30/mo. Infrastructure markup: ~98% Gross Margin on variable costs.
- **TEAM ($100/mo)**: 500 missions/mo. Estimated LLM cost: $3.00/mo.

## 3. High-Cost Operations
The most dangerous operation is an unbounded multi-agent loop running Z3 subprocesses indefinitely. **Budgets (iteration counters and timeouts)** are strictly enforced inside the agent state machine to prevent infinite loops.
