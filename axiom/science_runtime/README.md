# AXIOM Scientific Runtime

This package is the **local-first scientific execution track** of AXIOM.

## First benchmark

> Investigate the transition from stable to chaotic behavior in the Lorenz system.

The runtime deliberately separates:

1. **Question / hypothesis** — may be LLM-generated.
2. **Execution** — deterministic numerical code.
3. **Evidence** — measured outputs with parameters and method.
4. **Verification** — independent checks and repeatability.
5. **Claim** — never stronger than the evidence tier.

The first implementation uses a deterministic RK4 integrator and paired-trajectory sensitivity experiment. It requires no API key and no paid service.

## Run

From the repository root:

```bash
python -m axiom.science_runtime.cli --rho 28
python -m axiom.science_runtime.cli --sweep
```

## Optional local intelligence

Install Ollama separately and run a local model. The adapter in `agent.py` uses the local HTTP endpoint and does not require an OpenAI key.

```bash
ollama pull llama3.2
python -c "from axiom.science_runtime.agent import plan_with_ollama; print(plan_with_ollama('Study chaos in the Lorenz system'))"
```

The LLM can propose plans, but it cannot certify scientific claims. Numerical and formal tools remain the source of evidence.
