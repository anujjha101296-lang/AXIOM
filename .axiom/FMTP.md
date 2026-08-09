# Formal Mathematics & Theorem-Proving Loop (FMTP)

AXIOM builds model-independent formal mathematics capability: understand, generate, translate, search, repair, verify, and reproduce formal mathematical arguments.

## Mission

Work on increasingly difficult mathematics while maintaining machine-checkable correctness. **Formalization does not make a theorem true** — the trusted proof system must independently accept the artifact.

## Continuous loop

```text
MATHEMATICAL PROBLEM → FORMALIZE → SEARCH KNOWLEDGE → GENERATE APPROACHES
  → SEARCH LIBRARIES → EXPERIMENT → GENERATE CONJECTURES → ATTACK CONJECTURES
  → DECOMPOSE PROOF → GENERATE PROOF → FORMALLY CHECK → INDEPENDENTLY VERIFY
  → STORE SUCCESS/FAILURE → UPDATE MATHEMATICAL MEMORY → UPDATE BENCHMARKS
  → IMPROVE STRATEGY → NEXT PROBLEM
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `FORMAL_MATH_STATUS.md` | Current formal math posture |
| `THEOREM_PROVING_STATUS.md` | Theorem proving capability |
| `FORMAL_BENCHMARKS.md` | Progressive benchmark suite |
| `PROOF_LIBRARY_STATUS.md` | Library search status |
| `MATHEMATICAL_CAPABILITY.md` | Capability maturity |
| `MILLENNIUM_READINESS.md` | Prize campaign readiness gate |
| `scripts/fmtp_health_check.py` | Automated FMTP gate |

## Code modules

- `axiom/formal_math/models.py` — domain models and trust layers
- `axiom/formal_math/prover_registry.py` — Lean, Coq, Isabelle, SMT, SymPy
- `axiom/formal_math/store.py` — versioned proofs and entities
- `axiom/formal_math/formalization.py` — informal → formal pipeline
- `axiom/formal_math/explanation.py` — formal → informal (linked)
- `axiom/formal_math/compilation.py` — prover compilation with truthfulness guards
- `axiom/formal_math/proof_search.py` — proof strategy generation
- `axiom/formal_math/library_search.py` — theorem library search
- `axiom/formal_math/counterexample.py` — counterexample engine
- `axiom/formal_math/millennium_gate.py` — readiness evaluation
- `axiom/services/api_gateway/routes/formal_math_api.py` — `/formal/*` API

## Trust layers

Clearly distinguished: axioms, trusted kernel, formal libraries, automation, tactics, generated code, LLM output, human assertions.

## Constraints

- Never label LLM-generated proofs as `FORMALLY_VERIFIED`
- Never silently resolve mathematical ambiguity
- Never claim discovery without literature search, counterexample search, formal verification, and human review
- Failed approaches are preserved in failure memory

## Production requirements

```bash
REQUIRE_AUTH_FOR_FORMAL_MATH_ROUTES=true
```

## Integration

- **MIP** — Lean4 generator, conjecture engine
- **E&R** — evidence gate for discovery claims
- **SIMR** — verification-aware routing
- **TSS** — sandbox for code execution
- **SCEP** — capability benchmarking
