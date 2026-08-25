# Founder Demo FAQ

**What is AXIOM?**
AXIOM is an autonomous research operating system designed to discover, test, and formally verify mathematical and scientific knowledge.

**Who is it for?**
Quantitative researchers, formal verification engineers, and scientific laboratories who need rigorous proof, not just generative text.

**What does it do today?**
It ingests reference documents, formulates mathematical claims, and verifies finite-domain conjectures using a built-in Z3 SMT solver and secure Python sandbox, logging all steps in a Knowledge Graph.

**What does an agent actually do?**
An agent orchestrates the loop: it searches the `VectorStore`, extracts evidence, constructs a `MathematicalClaimNode`, and translates that claim into code or SMT logic to be executed by a tool.

**Where does research data come from?**
Currently, data is provided locally via user-uploaded documents stored in our SQLite-backed `VectorStore`. 

**How are citations verified?**
Citations are structurally tied to `DocumentChunk` IDs. The agent cannot cite evidence that does not exist in the isolated Project DB.

**How are mathematical claims verified?**
AXIOM translates claims into Z3 SMT logic or executable Python assertions. It then runs them in a sandboxed subprocess. If the solver finds a counterexample, the claim is falsified.

**What happens when AXIOM is wrong?**
If a claim fails verification, it is marked as `FALSIFIED` in the Knowledge Graph, and the counterexample is attached as provenance. The agent learns from this and iterates.

**How does memory work?**
Research state is saved as snapshots in the `EpistemicStore`. Failed proof attempts are recorded so agents do not repeat the same invalid tactics (Memory Anti-Rediscovery).

**How are agents controlled?**
Agents operate within a strict `ToolRegistry` and Sandbox. Budgets limit the number of loops and LLM calls to prevent infinite runaway execution.

**How much does a research task cost?**
Currently, tasks cost a fraction of a cent using Gemini 1.5 Flash/Pro or GPT-4o mini, bound by strict token and iteration budgets.

**What is the moat?**
The tightly coupled integration of an epistemic Knowledge Graph, safe execution sandboxing, and formal verification backends.

**What is still incomplete?**
Serverless/distributed worker architecture, infinite-horizon task persistence, and interactive (multi-step) Lean 4 kernel integration.
