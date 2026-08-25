# AXIOM Demo Day Script

**00:00 — Problem**
"Frontier AI models are incredible at text generation but fail miserably at rigorous mathematics and logic. When a researcher uses an LLM to explore a novel scientific claim, they currently have to spend hours manually verifying if the AI's math actually holds up."

**00:45 — What AXIOM is**
"AXIOM is an autonomous research operating system. We don't just generate text; we pair language models with programmatic sandboxes and formal verification kernels like Z3 and Lean 4 to ensure every claim is logically sound."

**01:30 — Start research question**
"Let's look at a live example. I'm going to enter a research query into AXIOM: 'Verify the bounds of quadratic residues modulo 4.' This is a classic number theory problem."

**02:00 — AXIOM creates research plan**
"Instantly, the AXIOM agent decomposes the problem. It formulates a plan to search existing literature, hypothesize possible bounds, and computationally verify them."

**03:00 — Research / sources**
"You can see it querying our SQLite VectorStore. It's pulling up exact chunks from mathematical texts about modular arithmetic, directly isolating the context so it doesn't hallucinate."

**04:00 — Evidence**
"Now, the agent extracts a specific evidence snippet: 'The only quadratic residues modulo 4 are 0 and 1.' It pins this to our Knowledge Graph as a foundational node."

**05:00 — Hypothesis / analysis**
"Based on this evidence, the LLM proposes a formal hypothesis: 'For any integer x, x^2 = 3 mod 4 has no solutions.' Notice it doesn't just state it; it creates a `MathematicalClaimNode` in our Epistemic Store."

**06:00 — Experiment or verification**
"Here is where AXIOM separates from ChatGPT. AXIOM automatically translates this claim into an SMT formula and runs it through the Z3 theorem prover in a secure Python sandbox. It sweeps the entire finite domain. No hallucinations, just pure computation."

**07:00 — Research artifact**
"The solver finishes. Z3 confirms no counterexamples exist. AXIOM synthesizes this into a final verified research artifact—a complete markdown report with the claim, the proof lineage, and the Z3 execution signature."

**08:00 — Research memory / provenance**
"If we look at the Knowledge Graph Dashboard, you can trace the exact lineage. The final verified claim points directly back to the Z3 execution log, the LLM hypothesis, and the original retrieved text. Complete provenance."

**09:00 — Why existing workflows are insufficient**
"If you tried this in a standard chat interface, you'd get a plausible-sounding but unverified paragraph. To do this manually requires switching between PDF readers, Jupyter notebooks, and Lean/Z3 environments. AXIOM unifies it."

**09:30 — Vision**
"Today, we are validating localized theorems. Our long-term vision is persistent, autonomous artificial scientists—agents that can run long-horizon formal reasoning and computational experiments to discover entirely new mathematics."

**10:00 — Questions**
"Thank you. I'd love to answer any questions."
