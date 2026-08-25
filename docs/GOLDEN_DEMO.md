# Golden Demo: AXIOM v0.1

**Scenario**: Validating a localized mathematical conjecture using autonomous research and formal verification.

## Setup
1. `export OPENAI_API_KEY="..."` or `GEMINI_API_KEY="..."`
2. Run database migration / setup script.
3. Start FastAPI server (`uvicorn axiom.services.api_gateway.main:app`).
4. Start Next.js UI (`npm run dev` in `ui/`).

## Input
- **Project**: "Number Theory Explorations"
- **Query**: "Verify the bounds of quadratic residues modulo 4."

## Expected Steps
1. **Retrieval**: System queries VectorStore for context on quadratic residues.
2. **Hypothesis**: Agent conjectures that `x^2 = 3 mod 4` has no solutions.
3. **Graph Creation**: `MathematicalClaimNode` is created with EpistemicStatus = `CONJECTURED`.
4. **Verification**: `SmtGateway` runs a Z3 subprocess check against `x**2 == 3` mod 4.
5. **Update**: Node transitions to `VERIFIED` status, supported by SMT Evidence snippet.

## Failure Recovery
- If the OpenAI API times out, `ModelClient` gracefully degrades to Gemini or a mock generator.
- If `z3` fails, the system executes an exhaustive loop up to the modulus (4).

## Final Artifact
- A rendered Knowledge Graph showing the verified claim and proof lineage in the dashboard.
